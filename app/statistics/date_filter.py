from datetime import date, datetime


class DateFilter:
    """Stores an optional start and end date."""

    def __init__(self, start=None, end=None):
        self._start = None
        self._end = None
        self.start = start
        self.end = end

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, value):
        value = self._parse_date(value)
        if value is not None and self._end is not None and value > self._end:
            raise ValueError("start date cannot be after end date")
        self._start = value

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, value):
        value = self._parse_date(value)
        if value is not None and self._start is not None and value < self._start:
            raise ValueError("end date cannot be before start date")
        self._end = value

    @staticmethod
    def _parse_date(value):
        if value is None:
            return None
        if isinstance(value, str):
            value = value.strip()
            return date.fromisoformat(value) if value else None
        if isinstance(value, datetime):
            return value.date()
        if not isinstance(value, date):
            raise TypeError("date must be a date object or YYYY-MM-DD string")
        return value
