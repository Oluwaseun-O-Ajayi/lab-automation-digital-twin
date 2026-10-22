"""Case study 1: validating the simulation engine against theory.

Question: does the engine reproduce results that are known exactly?
(a) Flow line, all samples present at time 0, one slot per device, fixed times:
    makespan = sum of times + (n - 1) x the longest time.
(b) M/M/1 queue (random arrivals at rate lambda, exponential service at rate mu):
    utilization = rho = lambda / mu, mean wait in queue = rho / (mu - lambda).
Output: examples/case_study_results/case1_flow_line.csv, case1_mm1.csv
"""

import pandas as pd
from _common import RESULTS
from lab_digital_twin import Device, Simulation, Workflow

rows = []
for times, n in [([2, 5, 3, 1], 20), ([4, 4, 4], 10), ([1, 7], 50), ([3, 1, 6, 2, 2], 100)]:
    devices = [Device(f"D{i}", 1, t) for i, t in enumerate(times)]
    sim = Simulation(devices)
    sim.add_samples(Workflow("line", [d.name for d in devices]), n)
    rows.append({"process_times": str(times), "samples": n, "theory": sum(times) + (n - 1) * max(times),
                 "simulated": sim.run().makespan})
flow = pd.DataFrame(rows)
flow.to_csv(RESULTS / "case1_flow_line.csv", index=False)
print("(a) Flow-line makespan")
print(flow.to_string(index=False))

rows = []
mu = 1.0
for rho in (0.5, 0.7, 0.9):
    lam = rho * mu
    sim = Simulation([Device("Server", 1, ("exponential", 1 / mu))], seed=11)
    sim.add_samples(Workflow("mm1", ["Server"]), 100000, ("exponential", 1 / lam))
    dev = sim.run().devices.loc["Server"]
    rows.append({"rho": rho, "utilization_theory": rho, "utilization_sim": round(dev["utilization"], 3),
                 "mean_wait_theory": round(rho / (mu - lam), 3), "mean_wait_sim": round(dev["mean_wait"], 3)})
mm1 = pd.DataFrame(rows)
mm1["wait_error_pct"] = (100 * (mm1["mean_wait_sim"] / mm1["mean_wait_theory"] - 1)).round(1)
mm1.to_csv(RESULTS / "case1_mm1.csv", index=False)
print("\n(b) M/M/1 queue, 100,000 samples each")
print(mm1.to_string(index=False))
