# Laboratory Automation Digital Twin Framework

**A modular Python framework for modeling material transport, device coordination, workflow execution, and sample traceability in automated laboratory workflows.**

---
## DOI and Archival Record

This software is archived on Zenodo to support long-term preservation, reproducibility, and scholarly citation.

**Current Version:** 1.0.1

**DOI:** https://doi.org/10.5281/zenodo.21689198

## Overview

Laboratory Automation Digital Twin Framework is an open-source software framework for simulating and analyzing automated laboratory workflows.

The framework models laboratory devices, samples, transport events, workflow steps, and audit trails within a single digital representation of a laboratory automation system. It is designed to support research, education, and early-stage design of automated laboratory workflows.

This project builds on general laboratory automation concepts such as:

- device state tracking
- sample lifecycle management
- material transport between workcell stations
- workflow execution
- event logging
- traceability and audit records
- throughput and utilization analysis

The framework is intended for non-proprietary, educational, and research-oriented laboratory automation modeling.

---

## What This Framework Does

- Models laboratory samples and their lifecycle states
- Represents automated devices such as storage units, liquid handlers, incubators, plate readers, and transport robots
- Simulates sample movement between devices
- Tracks workflow execution step-by-step
- Records traceability events and audit logs
- Computes workflow-level metrics such as transfer counts, device utilization, completion time, and bottlenecks
- Provides example workflows for automated laboratory material flow

---

## What This Framework Does Not Do

- It does not control real laboratory robots or instruments
- It does not connect to proprietary automation systems
- It does not include confidential industrial workflows
- It does not replace validated LIMS, MES, or instrument control software
- It does not simulate physical robot kinematics or collision detection at industrial fidelity

---

## Intended Use

This framework is intended for:

- laboratory automation education
- early-stage automated workflow design
- digital twin concept demonstration
- sample traceability modeling
- workcell coordination studies
- reproducible simulation of automated laboratory processes

---

## Core Concepts

### Samples

Samples are represented as trackable entities with:

- unique identifiers
- metadata
- current location
- lifecycle status
- event history

### Devices

Devices represent laboratory workcell components such as:

- storage units
- liquid handlers
- incubators
- centrifuges
- plate readers
- transport robots

Each device can have a state, capacity, queue, and processing duration.

### Workflows

Workflows define ordered or semi-ordered steps that move samples through devices and processing stages.

### Digital Twin Engine

The digital twin engine coordinates:

- sample movement
- device state updates
- workflow execution
- event logging
- metric collection

### Metrics

The framework can compute:

- total workflow duration
- number of transport events
- device utilization
- queue time
- bottleneck device
- traceability completeness

---

## Example Use Case

A cell culture screening workflow can be modeled as:

```text
Storage
  ↓
Liquid Handler
  ↓
Incubator
  ↓
Plate Reader
  ↓
Storage
```
## Project Structure

lab-automation-digital-twin/
├── README.md
├── paper.md
├── paper.bib
├── CITATION.cff
├── CHANGELOG.md
├── pyproject.toml
├── src/
│   ├── sample.py
│   ├── device.py
│   ├── workflow.py
│   ├── digital_twin.py
│   └── metrics.py
├── examples/
│   ├── sample_workflow.py
│   └── throughput_demo.py
├── docs/
└── figures/

## Installation

```bash
git clone https://github.com/Oluwaseun-O-Ajayi/lab-automation-digital-twin.git
cd lab-automation-digital-twin
pip install -e .
```

## Quick Start

```python
from src.sample import Sample
from src.device import Device
from src.workflow import Workflow
from src.digital_twin import DigitalTwinEngine

sample = Sample(
    sample_id="SAMPLE_001",
    metadata={"type": "cell_culture"}
)

storage = Device("Storage", capacity=10)
liquid_handler = Device(
    "LiquidHandler",
    capacity=1,
    process_time=5
)

plate_reader = Device(
    "PlateReader",
    capacity=1,
    process_time=3
)

workflow = Workflow(
    name="Example Screening Workflow",
    steps=[
        "Storage",
        "LiquidHandler",
        "PlateReader",
        "Storage"
    ]
)

engine = DigitalTwinEngine()

engine.add_sample(sample)
engine.add_device(storage)
engine.add_device(liquid_handler)
engine.add_device(plate_reader)

engine.run_workflow(
    sample.sample_id,
    workflow
)

engine.print_audit_log()
engine.print_metrics()
```

## Publication Framing
This repository is designed as a research software framework for modeling laboratory automation workflows.

The intended manuscript framing is:

Laboratory Automation Digital Twin Framework: Modeling Material Transport, Device Coordination, and Sample Traceability in Automated Laboratory Workflows

## Scientific Contribution

The Laboratory Automation Digital Twin Framework provides a modular and extensible software environment for modeling automated laboratory workflows through digital twin concepts.

The framework integrates sample traceability, device-state management, workflow execution, material transport simulation, event logging, and workflow performance metrics into a single reproducible platform. By combining these capabilities, the framework supports educational activities, workflow analysis, automation planning, and research in laboratory digital transformation.

Rather than controlling physical automation systems, the framework focuses on providing a transparent computational representation of laboratory operations that can be used to explore workflow behavior, evaluate system design concepts, and investigate traceability and throughput characteristics.

## Limitations

This is a conceptual and computational framework. It does not interface with real robots, instruments, LIMS systems, or manufacturing execution systems. It is intended for simulation, education, and research workflow modeling.

## License

MIT License

## Citation

If you use this software in research, education, workflow modeling, or laboratory automation studies, please cite:

```text
Ajayi, O. O. (2026).

Laboratory Automation Digital Twin Framework
(Version 1.0.1) [Computer software].

Zenodo.

DOI: 10.5281/zenodo.21689198
```

### BibTeX

```bibtex
@software{digital_twin_framework_2026,
  author = {Ajayi, Oluwaseun O.},
  title = {Laboratory Automation Digital Twin Framework},
  year = {2026},
  version = {1.0.1},
  publisher = {Zenodo},
  doi = {10.5281/zenodo.21689198},
  url = {https://doi.org/10.5281/zenodo.21689198}
}
```









