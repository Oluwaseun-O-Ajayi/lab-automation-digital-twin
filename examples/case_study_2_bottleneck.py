"""Case study 2: finding the bottleneck of a screening workcell.

Question: which device limits throughput, and does the simulation agree with
the capacity calculation?
Workcell: storage (10 slots, 0.5 min, visited twice), liquid handler (1, 6 min),
incubator (8, 60 min), plate reader (1, 4 min), 1.5 min transport.
Load: 96 plates all queued at time 0, so the workcell runs at full capacity.
Output: examples/case_study_results/case2_bottleneck.csv
"""

import pandas as pd
from _common import RESULTS, screening_devices, screening_workflow
from lab_digital_twin import Simulation, capacity_limit

devices, wf = screening_devices(), screening_workflow()
limits = capacity_limit(devices, wf)

sim = Simulation(devices, transport_time=1.5)
sim.add_samples(wf, 96)
result = sim.run()

table = result.devices[["capacity", "utilization", "mean_wait", "max_queue_length"]].copy()
table["max_plates_per_hour"] = [60 * limits[name] for name in table.index]
table = table.round(3)
table.to_csv(RESULTS / "case2_bottleneck.csv")
print(table.to_string())
m = result.metrics()
ceiling = 60 * min(limits.values())
print(f"\nPredicted bottleneck: {min(limits, key=limits.get)} (ceiling {ceiling:.2f} plates/hour)")
print(f"Simulated bottleneck: {result.bottleneck}; achieved {60 * m['throughput']:.2f} plates/hour "
      f"over {m['makespan']:.0f} min ({100 * m['throughput'] * 60 / ceiling:.1f}% of the ceiling)")
