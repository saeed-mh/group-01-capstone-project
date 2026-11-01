from abc import ABC, abstractmethod

from stream.pipeline import Pipeline


class StreamProcessor(ABC):
    """Base class for every pipeline step. Each step must implement process()."""

    @abstractmethod
    def process(self, event):
        """Take one Event. Return the (changed) Event, or None to drop it."""

    def __or__(self, other):
        """step | step  ->  a new Pipeline with both steps."""
        return Pipeline([self, other])
