from stream.processor import StreamProcessor


class RoutingAssigner(StreamProcessor):  # Inherit the same process(event) interface as the other processors.
    """Assigns a conveyor route to each waste category."""

    ROUTES = {  # Class mapping: each waste category has one conveyor route code.
        "packaging": "R1",
        "paper": "R2",
        "glass": "R3",
        "organic": "R4",
        "residual": "R5",
        "hazardous": "R6",
    }

    def process(self, event):  # Override process: return the routed event, or None if no route matches.
        event.route = self.ROUTES.get(event.material)  # Look up the route using the category set by MaterialMapper.
        if event.route is None:
            return None
        return event
