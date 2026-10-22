"""Case study 3: what-if analysis before buying equipment.

Question: for 48 plates arriving every 5 minutes, which change shortens the run
most: more incubator slots, a second liquid handler, or both?
Output: examples/case_study_results/case3_what_if.csv
"""

import pandas as pd
from _common import RESULTS, screening_devices, screening_workflow
from lab_digital_twin import Simulation

scenarios = {
    "Baseline (8 incubator slots, 1 liquid handler)": dict(),
    "12 incubator slots": dict(incubator_slots=12),
    "2 liquid handlers": dict(liquid_handlers=2),
    "12 incubator slots and 2 liquid handlers": dict(incubator_slots=12, liquid_handlers=2),
}
rows = []
for name, kwargs in scenarios.items():
    sim = Simulation(screening_devices(**kwargs), transport_time=1.5)
    sim.add_samples(screening_workflow(), n=48, interarrival=5.0)
    r = sim.run()
    m = r.metrics()
    rows.append({"scenario": name, "makespan_min": m["makespan"], "mean_turnaround_min": m["mean_turnaround"],
                 "p95_turnaround_min": m["p95_turnaround"], "mean_wait_min": m["mean_wait"],
                 "bottleneck": m["bottleneck"],
                 "bottleneck_utilization": r.devices.loc[m["bottleneck"], "utilization"]})
table = pd.DataFrame(rows).round(2)
table.to_csv(RESULTS / "case3_what_if.csv", index=False)
print(table.to_string(index=False))
print("\nThe lower bound for any scenario is the last arrival (235 min) plus one plate's "
      "processing and transport (77 min) = 312 min.")
