class Device:
    """
    Represents a laboratory device.
    """

    def __init__(self, name, capacity=1, process_time=1):
        self.name = name
        self.capacity = capacity
        self.process_time = process_time

        self.state = "idle"

        self.queue = []

        self.samples_processed = 0

    def add_sample(self, sample_id):
        self.queue.append(sample_id)

    def process_sample(self, sample_id):
        self.state = "processing"

        self.samples_processed += 1

        self.state = "idle"

    def __repr__(self):
        return f"Device({self.name})"
