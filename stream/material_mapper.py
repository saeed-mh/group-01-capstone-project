from stream.processor import StreamProcessor


class MaterialMapper(StreamProcessor):
    """Maps detected tags to the six waste categories."""

    MATERIALS = {
        "packaging": "packaging",
        "plastic": "packaging",
        "metal": "packaging",
        "paper": "paper",
        "glass": "glass",
        "organic": "organic",
        "residual": "residual",
        "hazardous": "hazardous",
    }

    def process(self, event):
        # bbox contains [x1, y1, x2, y2].
        x1, y1, x2, y2 = event.bbox
        width = x2 - x1
        height = y2 - y1
        if width <= 0 or height <= 0:
            return None
        event.bbox_area = width * height

        for tag in event.tags:
            material = self.MATERIALS.get(tag.strip().lower())
            if material is not None:
                event.material = material
                return event
        return None
