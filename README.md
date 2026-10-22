# Laboratory Automation Digital Twin Framework

**A discrete-event digital twin of automated laboratory workflows: device capacity, queues, processing and transport times, sample traceability, throughput and bottlenecks.**

[![tests](https://github.com/Oluwaseun-O-Ajayi/lab-automation-digital-twin/actions/workflows/tests.yml/badge.svg)](https://github.com/Oluwaseun-O-Ajayi/lab-automation-digital-twin/actions/workflows/tests.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21689198.svg)](https://doi.org/10.5281/zenodo.21689198)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## DOI and Archival Record

This software is archived on Zenodo to support long-term preservation, reproducibility, and scholarly citation.

**Current Version:** 2.0.0

**DOI:** https://doi.org/10.5281/zenodo.21689198

---

## Overview

The framework models an automated laboratory workcell as a set of devices, each with a number of parallel slots and a processing time, and moves samples through ordered workflows. A simulation clock advances from event to event: samples arrive, wait in first-in, first-out queues when a device is full, are processed, and are transported to the next step. Every event is recorded with its simulated time, so each sample has a complete chain of custody, and the run reports throughput, turnaround, waiting time, device utilization and the bottleneck.

It is intended for education, early-stage design of automated workflows, and what-if analysis before equipment or schedules are changed.

---

## What This Framework Does

- Models devices with capacity (parallel slots) and fixed or random processing times
- Moves samples through ordered workflows, including repeat visits to the same device
- Simulates transport time between steps (fixed or random)
- Schedules samples at fixed or random arrival intervals
- Records a time-stamped audit log and verifies each sample's chain of custody
- Reports makespan, throughput, mean and 95th-percentile turnaround, waiting time, utilization, queue lengths and the bottleneck
- Calculates the capacity limit of each device, so simulated throughput can be compared with theory

## What This Framework Does Not Do

- It does not control real laboratory robots or instruments
- It does not connect to proprietary automation systems
- It does not include confidential industrial workflows
- It does not replace validated LIMS, MES, or instrument control software
- It does not model robot kinematics, collisions, finite buffers, device failures or shift schedules

---

## Installation

```bash
git clone https://github.com/Oluwaseun-O-Ajayi/lab-automation-digital-twin.git
cd lab-automation-digital-twin
pip install .            # or: pip install ".[test]" to include the test dependencies
```

Requires Python 3.9 or later, NumPy and pandas.

## Quick Start

```python
from lab_digital_twin import Device, Workflow, Simulation, capacity_limit

devices = [
    Device("Storage", capacity=10, process_time=0.5),
    Device("Liquid handler", capacity=1, process_time=6.0),
    Device("Incubator", capacity=8, process_time=60.0),
    Device("Plate reader", capacity=1, process_time=("uniform", 3.0, 5.0)),
]
workflow = Workflow("Plate screening",
                    ["Storage", "Liquid handler", "Incubator", "Plate reader", "Storage"])

sim = Simulation(devices, transport_time=1.5, seed=1)
sim.add_samples(workflow, n=48, interarrival=5.0)
result = sim.run()

print(result.metrics())                  # throughput, turnaround, waiting, bottleneck
print(result.devices)                    # utilization and queues per device
print(result.verify_traceability())      # chain-of-custody check for every sample
print(capacity_limit(devices, workflow)) # maximum samples per minute each device allows
```

Durations can be a number, `("exponential", mean)`, `("normal", mean, sd)` (truncated at zero), `("uniform", low, high)`, or a function that takes a NumPy random generator. Time units are the user's choice; the examples use minutes.

More examples:

```bash
python examples/sample_workflow.py     # one plate and its audit trail
python examples/throughput_demo.py     # 48 plates: throughput and bottleneck
```

---

## Case Studies

Four reproducible case studies are described in [`examples/CASE_STUDIES.md`](examples/CASE_STUDIES.md):

1. **Validation.** The engine reproduces the exact makespan of deterministic flow lines and matches queueing theory (M/M/1) for utilization and waiting time to within 4%.
2. **Bottleneck.** In an illustrative screening workcell, the simulation and the capacity calculation both identify the incubator as the limit, and the run reaches 92% of its theoretical throughput.
3. **What-if.** Of three equipment changes, only one combination removes all waiting; a second liquid handler alone saves 7 of 419 minutes.
4. **Traceability.** With variable times, all 48 plates have a complete, ordered chain of custody, and a deleted record is detected.

---

## Core Concepts

**Device.** A workcell station with a name, a number of slots and a processing time. A sample that arrives when all slots are busy waits in a first-in, first-out queue of unlimited length.

**Workflow.** An ordered list of device names. A sample visits each in turn; a device may appear more than once (for example, storage at the start and end).

**Simulation.** Holds the devices, the transport time and a random seed. Samples are added with their workflow and arrival time, and `run()` returns a result.

**Result.** `audit_log` (every event with its time), `samples` (arrival, completion, turnaround, waiting, processing and transport time per sample), `devices` (utilization, samples processed, mean wait, maximum queue), `metrics()`, `bottleneck` and `verify_traceability()`.

---

## Testing

```bash
pip install ".[test]"
python -m pytest
```

The tests check exact makespans of deterministic flow lines, first-in, first-out ordering, parallel slots, M/M/1 utilization and waiting time against theory, throughput against the capacity limit, repeat visits, traceability (including detection of a deleted record), reproducibility with a seed, input validation, and that every example runs. They run on Linux, macOS and Windows for every push.

---

## Project Structure

```text
lab-automation-digital-twin/
├── lab_digital_twin/
│   ├── components.py      Device, Workflow, durations
│   └── simulation.py      event-driven engine, results, capacity limits
├── examples/
│   ├── sample_workflow.py
│   ├── throughput_demo.py
│   ├── case_study_1_validation.py ... case_study_4_traceability.py
│   ├── CASE_STUDIES.md
│   └── case_study_results/
├── tests/
├── paper.md, paper.bib
├── CITATION.cff, CHANGELOG.md
└── pyproject.toml
```

---

## Related Software

The [Automation Readiness Assessment Framework](https://github.com/Oluwaseun-O-Ajayi/automation-readiness-framework) scores whether a workflow is ready to automate. This framework then simulates how the automated workflow would perform.

---

## Limitations

This is a computational model for simulation, education and workflow design. Queues are unlimited, devices do not fail, and there are no shift patterns, so results describe an idealized workcell. Validate any conclusion against real operating data before using it for operational decisions.

## License

MIT License

## Citation

If you use this software in research, education, workflow modeling, or laboratory automation studies, please cite:

```text
Ajayi, O. O. (2026). Laboratory Automation Digital Twin Framework (Version 2.0.0) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.21689198
```

### BibTeX

```bibtex
@software{digital_twin_framework_2026,
  author = {Ajayi, Oluwaseun O.},
  title = {Laboratory Automation Digital Twin Framework},
  year = {2026},
  version = {2.0.0},
  publisher = {Zenodo},
  doi = {10.5281/zenodo.21689198},
  url = {https://doi.org/10.5281/zenodo.21689198}
}
```
