# Changelog

## 2.0.0 (2026-10)

Version 2 replaces the prototype engine with a discrete-event simulation. The
`src/` modules were replaced by the installable package `lab_digital_twin`;
code written for version 1 needs its imports and calls updated (see the README).

### Added
- Simulation clock: events are processed in time order, and all times in the
  audit log are simulated times, so runs are reproducible.
- Device capacity (parallel slots) and first-in, first-out queues now affect results.
- Fixed or random processing, transport and arrival times (exponential, normal,
  uniform, or a user function), with a seed for reproducibility.
- Metrics: makespan, throughput, mean and 95th-percentile turnaround, waiting
  time, utilization and maximum queue length per device, and the bottleneck.
- `capacity_limit()`: the theoretical throughput ceiling of each device.
- `verify_traceability()`: checks each sample's recorded chain of custody against
  its workflow.
- Test suite (exact flow-line makespans, M/M/1 queueing theory, capacity limits,
  traceability) with continuous integration on Linux, macOS and Windows.
- Four reproducible case studies (`examples/CASE_STUDIES.md`).
- MIT license file.

### Removed
- `Sample`, `DigitalTwinEngine` and `WorkflowMetrics` from version 1, and the
  wall-clock time stamps they produced.

## 1.0.1 (2026-07)

- Metadata and citation updates for archiving on Zenodo.

## 1.0.0 (2026-07)

- Initial release: samples, devices, ordered workflows, transport counting and an
  audit log.
