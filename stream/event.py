class Event:
    """One message from the optical sorter: a single item on the conveyor belt."""

    def __init__(self, item_id, tags, confidence, bbox):
        self.item_id = item_id
        self.tags = tags
        self.confidence = confidence
        self.bbox = bbox
        # the camera doesn't know them. The pipeline steps work them out later. None means "not decided yet".
        self.material = None  # filled in by Amin's MaterialMapper
        self.route = None  # filled in by Amin's RoutingAssigner

    def __repr__(self):
        return (
            f"Event(item_id={self.item_id}, tags={self.tags}, "
            f"confidence={self.confidence}, material={self.material}, route={self.route})"
        )
