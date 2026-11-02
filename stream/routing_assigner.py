from stream.processor import StreamProcessor


class RoutingAssigner(StreamProcessor):
    """Assigns a conveyor route to each waste category."""

    ROUTES = {
        "packaging": "R1",
        "paper": "R2",
        "glass": "R3",
        "organic": "R4",
        "residual": "R5",
        "hazardous": "R6",
    }

    def process(self, event):
        event.route = self.ROUTES.get(event.material)
        if event.route is None:
            return None
        return event
