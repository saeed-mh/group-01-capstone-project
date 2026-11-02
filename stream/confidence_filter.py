
from stream.processor import StreamProcessor


class ConfidenceFilter(StreamProcessor):
    """Removes events with confidence below the threshold."""

    def __init__(self, threshold=0.7):
        self.threshold = threshold

    def process(self, event):
        if event.confidence >= self.threshold:
            return event

        return None

