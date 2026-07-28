from src.sample import Sample
from src.device import Device
from src.workflow import Workflow
from src.digital_twin import DigitalTwinEngine


sample = Sample(
    sample_id="SAMPLE_001",
    metadata={"type": "cell_culture"},
)

workflow = Workflow(
    name="Cell Screening",
    steps=[
        "Storage",
        "LiquidHandler",
        "Incubator",
        "PlateReader",
        "Storage",
    ],
)

engine = DigitalTwinEngine()

engine.add_sample(sample)

engine.add_device(Device("Storage"))
engine.add_device(Device("LiquidHandler"))
engine.add_device(Device("Incubator"))
engine.add_device(Device("PlateReader"))

engine.run_workflow(sample.sample_id, workflow)

engine.print_audit_log()

engine.print_metrics()
