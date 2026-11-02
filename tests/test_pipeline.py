
from stream.event import Event
from stream.stream_source import StreamSource
from stream.confidence_filter import ConfidenceFilter
from stream.material_mapper import MaterialMapper
from stream.routing_assigner import RoutingAssigner


events = [
    Event(1, ["plastic"], 0.95, [10, 20, 50, 60]),
    Event(2, ["metal"], 0.40, [20, 30, 60, 70]),
    Event(3, ["glass"], 0.85, [30, 40, 70, 80])
]

source = StreamSource(events)

pipeline = ConfidenceFilter(0.7) | MaterialMapper() | RoutingAssigner()

for event in pipeline.run(source):
    print(event)
