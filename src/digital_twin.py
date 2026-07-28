from datetime import datetime

from src.metrics import WorkflowMetrics


class DigitalTwinEngine:
    """
    Main digital twin execution engine.
    """

    def __init__(self):
        self.samples = {}
        self.devices = {}

        self.audit_log = []

        self.metrics = WorkflowMetrics()

    def add_sample(self, sample):
        self.samples[sample.sample_id] = sample

    def add_device(self, device):
        self.devices[device.name] = device

    def log_event(self, event_type, details):
        self.audit_log.append(
            {
                "timestamp": datetime.now().isoformat(),
                "event": event_type,
                "details": details,
            }
        )

    def run_workflow(self, sample_id, workflow):

        sample = self.samples[sample_id]

        for step in workflow.steps:

            sample.update_location(step)

            self.log_event(
                "transport",
                {
                    "sample": sample_id,
                    "destination": step,
                },
            )

            self.metrics.transport_events += 1

        sample.update_status("completed")

        self.metrics.samples_completed += 1

    def print_audit_log(self):
        for event in self.audit_log:
            print(event)

    def print_metrics(self):
        print(self.metrics.report())
