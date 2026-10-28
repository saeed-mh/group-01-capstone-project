class RecyclingRule:
    """One recycling rule: which bin a waste category goes to in a city."""

    def __init__(
        self, id, region, category, bin_name, bin_color, instructions, examples
    ):
        self._id = id
        self.region = region
        self.category = category
        self.bin_name = bin_name
        self.bin_color = bin_color
        self.instructions = instructions
        self.examples = examples

    @property
    def id(self):
        return self._id

    @property
    def region(self):
        return self._region

    @region.setter
    def region(self, value):
        if not value or not value.strip():
            raise ValueError("region cannot be empty")
        self._region = value.strip()

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        if not value or not value.strip():
            raise ValueError("category cannot be empty")
        self._category = value.strip()

    @property
    def bin_name(self):
        return self._bin_name

    @bin_name.setter
    def bin_name(self, value):
        if not value or not value.strip():
            raise ValueError("bin name cannot be empty")
        self._bin_name = value.strip()

    @property
    def bin_color(self):
        return self._bin_color

    @bin_color.setter
    def bin_color(self, value):
        if not value or not value.strip():
            raise ValueError("bin color cannot be empty")
        self._bin_color = value.strip()

    @property
    def instructions(self):
        return self._instructions

    @instructions.setter
    def instructions(self, value):
        if not value or not value.strip():
            raise ValueError("instructions cannot be empty")
        self._instructions = value.strip()

    @property
    def examples(self):
        return self._examples

    @examples.setter
    def examples(self, value):
        if not value or not value.strip():
            raise ValueError("examples cannot be empty")
        self._examples = value.strip()
