"""Forty-eight plates arriving every five minutes: throughput, waiting and the bottleneck."""

from _common import screening_devices, screening_workflow
from lab_digital_twin import Simulation

sim = Simulation(screening_devices(), transport_time=1.5)
sim.add_samples(screening_workflow(), n=48, interarrival=5.0)
result = sim.run()

for key, value in result.metrics().items():
    print(f"{key:18} {value:.3f}" if isinstance(value, float) else f"{key:18} {value}")
print()
print(result.devices.round(3).to_string())
