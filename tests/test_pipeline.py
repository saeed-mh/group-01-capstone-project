
from stream.event import Event
from stream_source import StreamSource
from confidence_filter import ConfidenceFilter
from stream.pipeline import Pipeline

events = [
    Event(1, ["plastic"], 0.95, [10, 20, 50, 60]),
    Event(2, ["metal"], 0.40, [20, 30, 60, 70]),
    Event(3, ["glass"], 0.85, [30, 40, 70, 80])
]

source = StreamSource(events)

# pipeline = Pipeline([ConfidenceFilter(0.7)])
pipeline = ConfidenceFilter(0.7) | ConfidenceFilter(0.8)

for event in pipeline.run(source):
    print(event)
