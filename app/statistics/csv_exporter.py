from io import BytesIO

from app.statistics.statistics_service import StatisticsService


class CsvExporter:
    """Exports selected classifications as a CSV file in memory."""

    def __init__(self, statistics_service):
        self.statistics_service = statistics_service

    @property
    def statistics_service(self):
        return self._statistics_service

    @statistics_service.setter
    def statistics_service(self, value):
        if not isinstance(value, StatisticsService):
            raise TypeError("statistics_service must be a StatisticsService")
        self._statistics_service = value

    def export(self, date_filter=None, region=None):
        data = self.statistics_service.load_data(date_filter, region)
        csv_text = data.to_csv(index=False)
        return BytesIO(csv_text.encode("utf-8"))
