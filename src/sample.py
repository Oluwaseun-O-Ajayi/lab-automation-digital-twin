from datetime import datetime


class Sample:
    """
    Represents a laboratory sample within the digital twin.
    """

    def __init__(self, sample_id, metadata=None):
        self.sample_id = sample_id
        self.metadata = metadata or {}
        self.status = "registered"
        self.location = None
        self.history = []

    def update_location(self, location):
        self.location = location

        self.history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "event": "location_update",
                "location": location,
            }
        )

    def update_status(self, status):
        self.status = status

        self.history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "event": "status_update",
                "status": status,
            }
        )

    def __repr__(self):
        return f"Sample({self.sample_id}, status={self.status}, location={self.location})"
