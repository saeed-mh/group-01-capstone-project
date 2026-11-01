
from datetime import datetime


class ClassificationResult:
    """Stores the result of a waste classification."""

    def __init__(self, id, item_name, category, region, bin_name,
                 explanation, input_type, is_correct=None):

        self._id = id
        self.item_name = item_name
        self.category = category
        self.region = region
        self.bin_name = bin_name
        self.explanation = explanation
        self.input_type = input_type
        self.is_correct = is_correct
        self._created_at = datetime.now()

    @property
    def id(self):
        return self._id

    @property
    def item_name(self):
        return self._item_name

    @item_name.setter
    def item_name(self, value):
        if not value or not value.strip():
            raise ValueError("Item name cannot be empty")
        self._item_name = value.strip()

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        if value not in ["packaging", "paper", "glass",
                         "organic", "residual", "hazardous"]:
            raise ValueError("Invalid waste category")
        self._category = value

    @property
    def region(self):
        return self._region

    @region.setter
    def region(self, value):
        if not value or not value.strip():
            raise ValueError("Region cannot be empty")
        self._region = value.strip()

    @property
    def bin_name(self):
        return self._bin_name

    @bin_name.setter
    def bin_name(self, value):
        self._bin_name = value

    @property
    def explanation(self):
        return self._explanation

    @explanation.setter
    def explanation(self, value):
        self._explanation = value

    @property
    def input_type(self):
        return self._input_type

    @input_type.setter
    def input_type(self, value):
        if value not in ["image", "text"]:
            raise ValueError("Input type must be image or text")
        self._input_type = value

    @property
    def is_correct(self):
        return self._is_correct

    @is_correct.setter
    def is_correct(self, value):
        if value is not None and not isinstance(value, bool):
            raise ValueError("Feedback must be True, False or None")
        self._is_correct = value

    @property
    def created_at(self):
        return self._created_at
