"""One plate through the screening workflow, with its full audit trail."""

from _common import screening_devices, screening_workflow
from lab_digital_twin import Simulation

sim = Simulation(screening_devices(), transport_time=1.5)
sim.add_sample("PLATE_001", screening_workflow())
result = sim.run()

print(result.audit_log[["time", "event", "device"]].to_string(index=False))
print("\nTurnaround:", result.samples.loc[0, "turnaround"], "min")
