"""Laboratory Automation Digital Twin Framework.

A discrete-event model of samples moving through laboratory devices, with device
capacity, processing and transport times, queues, an audit trail, and workflow
metrics (throughput, turnaround, waiting, utilization and bottlenecks).
"""

from .components import Device, Workflow, draw, mean_duration
from .simulation import Simulation, SimulationResult, capacity_limit

__version__ = "2.0.0"

__all__ = ["Device", "Workflow", "Simulation", "SimulationResult", "capacity_limit",
           "draw", "mean_duration", "__version__"]
