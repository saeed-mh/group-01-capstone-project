from stream.processor import StreamProcessor


class MaterialMapper(StreamProcessor):  # Inherit the shared StreamProcessor interface.
    """Maps detected tags to the six waste categories."""

    MATERIALS = {  # Class mapping: tags become one of the six team categories.
        "packaging": "packaging",
        "plastic": "packaging",
        "metal": "packaging",
        "paper": "paper",
        "glass": "glass",
        "organic": "organic",
        "residual": "residual",
        "hazardous": "hazardous",
    }

    def process(self, event):  # Override process: return the mapped event, or None to discard it.
        # bbox contains [x1, y1, x2, y2].
        x1, y1, x2, y2 = event.bbox
        width = x2 - x1
        height = y2 - y1
        if width <= 0 or height <= 0:  # Zero or negative box dimensions are invalid.
            return None
        event.bbox_area = width * height  # Save the bounding-box area on the event.

        for tag in event.tags:
            material = self.MATERIALS.get(tag.strip().lower())  # Normalise the tag and look up its category; unknown tags give None.
            if material is not None:
                event.material = material
                return event  # Keep the event after the first recognised tag.
        return None  # Drop events with no recognised tag.
