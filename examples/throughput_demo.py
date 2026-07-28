from src.sample import Sample
from src.device import Device
from src.workflow import Workflow
from src.digital_twin import DigitalTwinEngine


engine = DigitalTwinEngine()

engine.add_device(Device("Storage"))
engine.add_device(Device("LiquidHandler"))
engine.add_device(Device("Incubator"))
engine.add_device(Device("PlateReader"))

workflow = Workflow(
    "Throughput Test",
    [
        "Storage",
        "LiquidHandler",
        "Incubator",
        "PlateReader",
        "Storage",
    ],
)

for i in range(100):

    sample = Sample(f"SAMPLE_{i:03d}")

    engine.add_sample(sample)

    engine.run_workflow(sample.sample_id, workflow)

engine.print_metrics()
