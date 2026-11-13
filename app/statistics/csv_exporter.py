from io import BytesIO  # BytesIO is a file-like object held in memory.

from app.statistics.statistics_service import StatisticsService


class CsvExporter:
    """Exports selected classifications as a CSV file in memory."""

    def __init__(self, statistics_service):  # Receive a StatisticsService helper; returns None.
        self.statistics_service = statistics_service  # Dependency injection: the caller supplies the service.

    @property  # Getter: return the stored StatisticsService object.
    def statistics_service(self):
        return self._statistics_service

    @statistics_service.setter  # Setter: require and store a StatisticsService; returns None.
    def statistics_service(self, value):
        if not isinstance(value, StatisticsService):
            raise TypeError("statistics_service must be a StatisticsService")
        self._statistics_service = value

    def export(self, date_filter=None, region=None):  # Return selected records as a BytesIO CSV download.
        data = self.statistics_service.load_data(date_filter, region)  # Reuse the service for the same date and city filter rules.
        csv_text = data.to_csv(index=False)  # Omit the extra pandas row-number column.
        return BytesIO(csv_text.encode("utf-8"))  # Encode CSV text as UTF-8 bytes; no server file is written.
