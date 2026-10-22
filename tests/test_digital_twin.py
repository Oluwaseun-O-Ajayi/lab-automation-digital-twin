"""Tests for the digital twin: exact results for deterministic flow lines, queueing
theory for random arrivals and service, capacity limits, and traceability."""

import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from lab_digital_twin import Device, Simulation, Workflow, capacity_limit, draw, mean_duration

ROOT = Path(__file__).resolve().parents[1]


def line(times, capacities=None):
    capacities = capacities or [1] * len(times)
    devices = [Device(f"D{i}", c, t) for i, (t, c) in enumerate(zip(times, capacities))]
    return devices, Workflow("line", [d.name for d in devices])


# ------------------------------------------------------------------ exact results
@pytest.mark.parametrize("times,n", [([2, 5, 3, 1], 20), ([4, 4, 4], 10), ([1, 7], 5)])
def test_flow_line_makespan_matches_closed_form(times, n):
    """All samples present at t = 0, one slot per device: makespan = sum(p) + (n - 1) max(p)."""
    devices, wf = line(times)
    sim = Simulation(devices)
    sim.add_samples(wf, n)
    assert sim.run().makespan == pytest.approx(sum(times) + (n - 1) * max(times))


def test_single_sample_turnaround_is_processing_plus_transport():
    devices, wf = line([2, 3, 4])
    sim = Simulation(devices, transport_time=1.5)
    sim.add_sample("A", wf)
    s = sim.run().samples.iloc[0]
    assert s["turnaround"] == pytest.approx(2 + 3 + 4 + 2 * 1.5)
    assert s["total_wait"] == 0 and s["total_transport"] == pytest.approx(3.0)


def test_parallel_slots_process_samples_together():
    devices, wf = line([10], capacities=[4])
    sim = Simulation(devices)
    sim.add_samples(wf, 8)
    assert sim.run().makespan == pytest.approx(20)


def test_queue_is_first_in_first_out():
    devices, wf = line([5])
    sim = Simulation(devices)
    for i, t in enumerate([0, 1, 2]):
        sim.add_sample(f"S{i}", wf, t)
    done = sim.run().samples.set_index("sample_id")["completion_time"]
    assert list(done) == [5, 10, 15]


def test_slot_freed_at_t_is_available_to_an_arrival_at_t():
    devices, wf = line([5])
    sim = Simulation(devices)
    sim.add_sample("A", wf, 0)
    sim.add_sample("B", wf, 5)
    assert sim.run().samples.set_index("sample_id").loc["B", "total_wait"] == 0


# ------------------------------------------------------------- queueing theory
@pytest.mark.parametrize("rho", [0.5, 0.8])
def test_mm1_waiting_time_and_utilization_match_theory(rho):
    """M/M/1 queue: utilization rho and mean wait in queue rho / (mu - lambda)."""
    mu, lam = 1.0, rho
    sim = Simulation([Device("S", 1, ("exponential", 1 / mu))], seed=7)
    sim.add_samples(Workflow("m", ["S"]), 40000, ("exponential", 1 / lam))
    dev = sim.run().devices.loc["S"]
    assert dev["utilization"] == pytest.approx(rho, rel=0.03)
    assert dev["mean_wait"] == pytest.approx(rho / (mu - lam), rel=0.08)


def test_throughput_approaches_the_capacity_limit():
    devices = [Device("A", 1, 2), Device("B", 2, 5), Device("C", 1, 1)]
    wf = Workflow("x", ["A", "B", "C"])
    limits = capacity_limit(devices, wf)
    assert limits == {"A": 0.5, "B": 0.4, "C": 1.0}
    sim = Simulation(devices)
    sim.add_samples(wf, 500)
    result = sim.run()
    assert result.bottleneck == "B"
    assert result.metrics()["throughput"] == pytest.approx(0.4, rel=0.01)


def test_repeat_visits_count_against_capacity():
    devices = [Device("Store", 1, 1), Device("Read", 1, 1)]
    limits = capacity_limit(devices, Workflow("w", ["Store", "Read", "Store"]))
    assert limits["Store"] == pytest.approx(0.5)


# ---------------------------------------------------------------- traceability
def test_every_sample_is_traceable_and_conserved():
    devices = [Device("Storage", 10, 0.5), Device("Handler", 1, ("normal", 6, 1)),
               Device("Reader", 1, ("uniform", 3, 5))]
    wf = Workflow("w", ["Storage", "Handler", "Reader", "Storage"])
    sim = Simulation(devices, transport_time=("exponential", 1.0), seed=3)
    sim.add_samples(wf, 60, ("exponential", 7))
    result = sim.run()
    check = result.verify_traceability()
    assert len(check) == 60 and check["trace_ok"].all()
    assert result.devices.loc["Storage", "samples_processed"] == 120
    assert result.devices["utilization"].between(0, 1).all()


def test_tampered_audit_log_is_detected():
    devices, wf = line([1, 1, 1])
    sim = Simulation(devices)
    sim.add_samples(wf, 3)
    result = sim.run()
    drop = result.audit_log[(result.audit_log["sample_id"] == "S2") &
                            (result.audit_log["device"] == "D1")].index
    result.audit_log = result.audit_log.drop(drop)
    check = result.verify_traceability().set_index("sample_id")["trace_ok"]
    assert not check["S2"] and check["S1"] and check["S3"]


def test_runs_are_reproducible_with_a_seed():
    def run(seed):
        sim = Simulation([Device("S", 1, ("exponential", 1.0))], seed=seed)
        sim.add_samples(Workflow("m", ["S"]), 200, ("exponential", 1.2))
        return sim.run().samples["completion_time"].to_numpy()
    assert np.array_equal(run(5), run(5)) and not np.array_equal(run(5), run(6))


# ---------------------------------------------------------------------- inputs
def test_durations():
    rng = np.random.default_rng(0)
    assert draw(3, rng) == 3.0
    assert draw(("normal", 0.0, 1.0), rng) >= 0
    assert mean_duration(("uniform", 2, 4)) == 3
    with pytest.raises(ValueError):
        draw(("gamma", 1), rng)


def test_invalid_inputs_are_rejected():
    with pytest.raises(ValueError):
        Device("X", capacity=0)
    with pytest.raises(ValueError):
        Workflow("empty", [])
    sim = Simulation([Device("A")])
    with pytest.raises(ValueError):
        sim.add_sample("S", Workflow("w", ["A", "Missing"]))
    with pytest.raises(ValueError):
        Simulation([Device("A"), Device("A")])
    with pytest.raises(ValueError):
        Simulation([Device("A")]).run()


# --------------------------------------------------------------------- scripts
SCRIPTS = sorted(p.name for p in (ROOT / "examples").glob("*.py") if not p.name.startswith("_"))


@pytest.mark.parametrize("script", SCRIPTS)
def test_examples_run(script, tmp_path):
    env = dict(os.environ, MPLBACKEND="Agg", PYTHONIOENCODING="utf-8")
    proc = subprocess.run([sys.executable, str(ROOT / "examples" / script)], cwd=tmp_path, env=env,
                          capture_output=True, text=True, timeout=600)
    assert proc.returncode == 0, proc.stderr[-2000:]
