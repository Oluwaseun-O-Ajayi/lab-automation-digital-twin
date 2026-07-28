class Workflow:
    """
    Ordered workflow definition.
    """

    def __init__(self, name, steps):
        self.name = name
        self.steps = steps

    def __repr__(self):
        return f"Workflow({self.name})"
