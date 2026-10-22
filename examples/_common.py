"""Shared set-up for the examples: an illustrative, generic plate-based screening
workcell. Device names, capacities and times are round numbers chosen for
demonstration; they do not describe any specific laboratory or vendor system.
Times are in minutes."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lab_digital_twin import Device, Workflow  # noqa: E402

RESULTS = Path(__file__).resolve().parent / "case_study_results"
RESULTS.mkdir(exist_ok=True)

SCREENING_STEPS = ["Storage", "Liquid handler", "Incubator", "Plate reader", "Storage"]


def screening_devices(incubator_slots=8, liquid_handlers=1, plate_readers=1):
    return [
        Device("Storage", capacity=10, process_time=0.5),        # retrieve or store a plate
        Device("Liquid handler", capacity=liquid_handlers, process_time=6.0),
        Device("Incubator", capacity=incubator_slots, process_time=60.0),
        Device("Plate reader", capacity=plate_readers, process_time=4.0),
    ]


def screening_workflow():
    return Workflow("Plate screening", SCREENING_STEPS)
