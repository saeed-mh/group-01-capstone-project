from datetime import date, datetime


class DateFilter:
    """Stores an optional start and end date."""

    def __init__(self, start=None, end=None):  # Initialise checked date boundaries; returns None.
        self._start = None
        self._end = None  # Initialise both values before the setters compare them.
        self.start = start  # Use the setter instead of writing _start directly.
        self.end = end

    @property  # Getter: return the start date, or None for no lower limit.
    def start(self):
        return self._start

    @start.setter  # Setter: parse and check the start date; returns None.
    def start(self, value):
        value = self._parse_date(value)
        if value is not None and self._end is not None and value > self._end:  # Reject a start date later than an existing end date.
            raise ValueError("start date cannot be after end date")
        self._start = value

    @property  # Getter: return the end date, or None for no upper limit.
    def end(self):
        return self._end

    @end.setter  # Setter: parse and check the end date; returns None.
    def end(self, value):
        value = self._parse_date(value)
        if value is not None and self._start is not None and value < self._start:  # Reject an end date earlier than the start date.
            raise ValueError("end date cannot be before start date")
        self._end = value

    @staticmethod  # Static helper: needs neither self nor a class object.
    def _parse_date(value):  # Return a date or None; invalid input raises ValueError or TypeError.
        if value is None:
            return None
        if isinstance(value, str):
            value = value.strip()
            return date.fromisoformat(value) if value else None  # Empty text means no boundary; otherwise parse YYYY-MM-DD.
        if isinstance(value, datetime):  # Check datetime first because it is also a subclass of date.
            return value.date()  # Discard the time and keep the date.
        if not isinstance(value, date):
            raise TypeError("date must be a date object or YYYY-MM-DD string")
        return value
