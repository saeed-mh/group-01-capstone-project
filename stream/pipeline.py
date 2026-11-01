class Pipeline:
    """A chain of StreamProcessor steps that every event passes through in order."""

    def __init__(self, steps):
        self.steps = list(steps)

    def run(self, events):
        """Send each event through all steps; yield only the events that survive."""
        for event in events:
            for step in self.steps:
                event = step.process(event)
                if event is None:
                    break
            if event is not None:
                yield event

    def __or__(self, other):
        """pipeline | step  ->  a new Pipeline with the step added at the end."""
        return Pipeline(self.steps + [other])
