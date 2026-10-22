"""Case study 4: traceability under variable processing times.

Question: when processing and transport times vary from plate to plate, can every
plate's chain of custody be reconstructed and checked, and is a missing record
detected?
Set-up: the screening workcell with random times (liquid handler 6 +/- 1 min,
incubator 60 +/- 5 min, plate reader 3 to 5 min, exponential transport with mean
1.5 min), 48 plates arriving at random with a mean spacing of 5 min, seed 2026.
Output: examples/case_study_results/case4_chain_of_custody_P07.csv
        examples/case_study_results/case4_traceability_check.csv
"""

import pandas as pd
from _common import RESULTS, screening_workflow
from lab_digital_twin import Device, Simulation

devices = [Device("Storage", 10, 0.5), Device("Liquid handler", 1, ("normal", 6.0, 1.0)),
           Device("Incubator", 8, ("normal", 60.0, 5.0)), Device("Plate reader", 1, ("uniform", 3.0, 5.0))]
sim = Simulation(devices, transport_time=("exponential", 1.5), seed=2026)
sim.add_samples(screening_workflow(), n=48, interarrival=("exponential", 5.0), prefix="P")
result = sim.run()

custody = result.audit_log[result.audit_log["sample_id"] == "P07"][["time", "event", "device"]].round(2)
custody.to_csv(RESULTS / "case4_chain_of_custody_P07.csv", index=False)
print("Chain of custody for plate P07:")
print(custody.to_string(index=False))

check = result.verify_traceability()
print(f"\nPlates with a complete, ordered record: {int(check['trace_ok'].sum())} of {len(check)}")

# Simulate a lost record: delete plate P19's plate-reader entries and check again
log = result.audit_log
lost = log[(log["sample_id"] == "P19") & (log["device"] == "Plate reader")].index
result.audit_log = log.drop(lost)
check_after = result.verify_traceability()
flagged = check_after.loc[~check_after["trace_ok"], "sample_id"].tolist()
print(f"After deleting P19's plate-reader records, plates flagged: {flagged}")

summary = check.merge(check_after[["sample_id", "trace_ok"]].rename(columns={"trace_ok": "trace_ok_after_deletion"}))
summary.to_csv(RESULTS / "case4_traceability_check.csv", index=False)
m = result.metrics()
print(f"\nMean turnaround {m['mean_turnaround']:.1f} min, 95th percentile {m['p95_turnaround']:.1f} min")
