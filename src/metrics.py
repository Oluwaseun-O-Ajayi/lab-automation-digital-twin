class WorkflowMetrics:
    """
    Stores workflow execution metrics.
    """

    def __init__(self):
        self.transport_events = 0
        self.samples_completed = 0

    def report(self):
        return {
            "transport_events": self.transport_events,
            "samples_completed": self.samples_completed,
        }
