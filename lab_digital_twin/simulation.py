"""Discrete-event simulation of samples moving through laboratory devices.

Each device has a number of parallel slots (capacity) and a first-in, first-out
queue of unlimited length. A sample visits the devices named in its workflow in
order. Between steps it spends `transport_time` in transit. The simulation
advances a clock from event to event, so results do not depend on the speed of
the computer and are reproducible for a given seed.

Time units are whatever the user chooses (minutes in the examples).
"""

import heapq
import itertools
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence

import numpy as np
import pandas as pd

from .components import Device, Duration, Workflow, draw

# At equal times, finishing work is handled before new arrivals, so a slot freed
# at time t can be taken by a sample that arrives at time t.
_FINISH, _ARRIVE = 0, 1


@dataclass
class _Sample:
    sample_id: str
    workflow: Workflow
    arrival_time: float
    step: int = 0
    completion_time: Optional[float] = None


@dataclass
class SimulationResult:
    """Outcome of one simulation run. All tables are pandas DataFrames."""

    audit_log: pd.DataFrame
    samples: pd.DataFrame
    devices: pd.DataFrame
    workflows: Dict[str, Workflow] = field(repr=False)

    @property
    def makespan(self) -> float:
        """Time from the first arrival to the last completion."""
        done = self.samples.dropna(subset=["completion_time"])
        if done.empty:
            return 0.0
        return float(done["completion_time"].max() - self.samples["arrival_time"].min())

    @property
    def bottleneck(self) -> str:
        """The device with the highest utilization."""
        return str(self.devices.sort_values("utilization", ascending=False).index[0])

    def metrics(self) -> Dict[str, float]:
        """Workflow-level summary."""
        done = self.samples.dropna(subset=["completion_time"])
        span = self.makespan
        return {
            "samples_completed": int(len(done)),
            "makespan": span,
            "throughput": len(done) / span if span > 0 else float("nan"),
            "mean_turnaround": float(done["turnaround"].mean()) if len(done) else float("nan"),
            "p95_turnaround": float(done["turnaround"].quantile(0.95)) if len(done) else float("nan"),
            "mean_wait": float(done["total_wait"].mean()) if len(done) else float("nan"),
            "bottleneck": self.bottleneck,
        }

    def verify_traceability(self) -> pd.DataFrame:
        """Check every sample's recorded history against its workflow.

        A sample passes when the audit log shows it started and finished every
        step in the workflow order, each finish after its start, and was then
        marked complete.
        """
        rows = []
        for sid, events in self.audit_log.groupby("sample_id", sort=False):
            wf = self.workflows[events["workflow"].iloc[0]]
            started = events.loc[events["event"] == "started", "device"].tolist()
            finished = events.loc[events["event"] == "finished", "device"].tolist()
            t_start = events.loc[events["event"] == "started", "time"].to_numpy()
            t_finish = events.loc[events["event"] == "finished", "time"].to_numpy()
            complete = (events["event"] == "completed").any()
            ok = (started == wf.steps and finished == wf.steps and complete
                  and len(t_start) == len(t_finish) and bool(np.all(t_finish >= t_start))
                  and bool(np.all(np.diff(events["time"].to_numpy()) >= 0)))
            rows.append({"sample_id": sid, "workflow": wf.name, "steps_expected": len(wf.steps),
                         "steps_recorded": len(finished), "complete": bool(complete), "trace_ok": bool(ok)})
        return pd.DataFrame(rows)


class Simulation:
    """A digital twin of a set of devices.

    Args:
        devices: the devices in the workcell.
        transport_time: time to move a sample between consecutive steps (see Duration).
        seed: seed for all random draws, for reproducible runs.
    """

    def __init__(self, devices: Iterable[Device], transport_time: Duration = 0.0, seed: Optional[int] = None):
        self.devices: Dict[str, Device] = {}
        for d in devices:
            if d.name in self.devices:
                raise ValueError(f"Duplicate device name '{d.name}'")
            self.devices[d.name] = d
        self.transport_time = transport_time
        self.rng = np.random.default_rng(seed)
        self._samples: List[_Sample] = []
        self._ids = set()
        self._workflows: Dict[str, Workflow] = {}

    # ------------------------------------------------------------------ input
    def add_sample(self, sample_id: str, workflow: Workflow, arrival_time: float = 0.0):
        """Schedule one sample to enter its workflow at arrival_time."""
        missing = [s for s in workflow.steps if s not in self.devices]
        if missing:
            raise ValueError(f"Workflow '{workflow.name}' uses unknown devices: {missing}")
        if sample_id in self._ids:
            raise ValueError(f"Duplicate sample id '{sample_id}'")
        self._ids.add(sample_id)
        self._workflows[workflow.name] = workflow
        self._samples.append(_Sample(sample_id, workflow, float(arrival_time)))

    def add_samples(self, workflow: Workflow, n: int, interarrival: Duration = 0.0,
                    start_time: float = 0.0, prefix: str = "S"):
        """Schedule n samples, one every `interarrival` time units (fixed or random)."""
        t = float(start_time)
        width = len(str(n))
        offset = len(self._samples)
        for i in range(n):
            if i > 0:
                t += draw(interarrival, self.rng)
            self.add_sample(f"{prefix}{offset + i + 1:0{width}d}", workflow, t)

    # -------------------------------------------------------------------- run
    def run(self) -> SimulationResult:
        """Run until every sample has completed its workflow."""
        if not self._samples:
            raise ValueError("No samples scheduled")
        counter = itertools.count()
        events: list = []
        log: List[dict] = []
        busy = {name: 0 for name in self.devices}
        queues: Dict[str, deque] = {name: deque() for name in self.devices}
        busy_time = {name: 0.0 for name in self.devices}
        processed = {name: 0 for name in self.devices}
        waits: Dict[str, List[float]] = {name: [] for name in self.devices}
        max_queue = {name: 0 for name in self.devices}
        enqueued_at: Dict[tuple, float] = {}
        sample_wait: Dict[str, float] = {s.sample_id: 0.0 for s in self._samples}
        sample_proc: Dict[str, float] = {s.sample_id: 0.0 for s in self._samples}
        sample_transport: Dict[str, float] = {s.sample_id: 0.0 for s in self._samples}

        def record(t, sample, event, device=None, **extra):
            log.append({"time": t, "sample_id": sample.sample_id, "workflow": sample.workflow.name,
                        "event": event, "device": device, **extra})

        def start(t, sample, device):
            busy[device] += 1
            wait = t - enqueued_at.pop((sample.sample_id, sample.step))
            waits[device].append(wait)
            sample_wait[sample.sample_id] += wait
            duration = draw(self.devices[device].process_time, self.rng)
            busy_time[device] += duration
            sample_proc[sample.sample_id] += duration
            record(t, sample, "started", device, wait=wait)
            heapq.heappush(events, (t + duration, _FINISH, next(counter), sample, device))

        for s in self._samples:
            record(s.arrival_time, s, "registered")
            heapq.heappush(events, (s.arrival_time, _ARRIVE, next(counter), s, s.workflow.steps[0]))

        while events:
            t, kind, _, sample, device = heapq.heappop(events)
            if kind == _ARRIVE:
                enqueued_at[(sample.sample_id, sample.step)] = t
                record(t, sample, "arrived", device)
                if busy[device] < self.devices[device].capacity:
                    start(t, sample, device)
                else:
                    queues[device].append(sample)
                    max_queue[device] = max(max_queue[device], len(queues[device]))
                    record(t, sample, "queued", device, queue_length=len(queues[device]))
            else:  # finish
                busy[device] -= 1
                processed[device] += 1
                record(t, sample, "finished", device)
                sample.step += 1
                if sample.step < len(sample.workflow.steps):
                    move = draw(self.transport_time, self.rng)
                    sample_transport[sample.sample_id] += move
                    nxt = sample.workflow.steps[sample.step]
                    record(t, sample, "transport", device, destination=nxt, duration=move)
                    heapq.heappush(events, (t + move, _ARRIVE, next(counter), sample, nxt))
                else:
                    sample.completion_time = t
                    record(t, sample, "completed")
                if queues[device]:
                    start(t, queues[device].popleft(), device)

        audit = pd.DataFrame(log).sort_values(["time"], kind="stable").reset_index(drop=True)
        samples = pd.DataFrame([{
            "sample_id": s.sample_id, "workflow": s.workflow.name, "arrival_time": s.arrival_time,
            "completion_time": s.completion_time,
            "turnaround": None if s.completion_time is None else s.completion_time - s.arrival_time,
            "total_wait": sample_wait[s.sample_id], "total_processing": sample_proc[s.sample_id],
            "total_transport": sample_transport[s.sample_id]} for s in self._samples])
        start_t = samples["arrival_time"].min()
        end_t = samples["completion_time"].max()
        horizon = max(end_t - start_t, 1e-12)
        devices = pd.DataFrame([{
            "device": name, "capacity": d.capacity, "samples_processed": processed[name],
            "busy_time": busy_time[name], "utilization": busy_time[name] / (d.capacity * horizon),
            "mean_wait": float(np.mean(waits[name])) if waits[name] else 0.0,
            "max_queue_length": max_queue[name]} for name, d in self.devices.items()]).set_index("device")
        return SimulationResult(audit, samples, devices, dict(self._workflows))


def capacity_limit(devices: Sequence[Device], workflow: Workflow) -> Dict[str, float]:
    """Long-run maximum throughput each device allows for this workflow.

    A device visited k times per sample, with c slots and mean processing time p,
    can complete at most c / (k p) samples per time unit. The smallest of these is
    the throughput ceiling of the whole workflow, and its device is the
    theoretical bottleneck. Devices with zero processing time are unlimited.
    """
    from .components import mean_duration
    by_name = {d.name: d for d in devices}
    visits = pd.Series(workflow.steps).value_counts()
    limits = {}
    for name, k in visits.items():
        p = mean_duration(by_name[name].process_time)
        limits[name] = float("inf") if p == 0 else by_name[name].capacity / (k * p)
    return limits
