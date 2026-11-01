from contextlib import closing
from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd

from app.statistics.date_filter import DateFilter


class StatisticsService:
    """Calculates statistics from loaded waste classifications."""

    COLUMNS = [
        "id", "item_name", "category", "region", "bin_name",
        "explanation", "input_type", "is_correct", "created_at",
    ]

    def __init__(self, db_path=None):
        self.db_path = db_path
        self.df = pd.DataFrame(columns=self.COLUMNS)

    @property
    def db_path(self):
        return self._db_path

    @db_path.setter
    def db_path(self, value):
        if value is not None:
            if not isinstance(value, str) or not value.strip():
                raise ValueError("db_path must be a non-empty string or None")
            value = value.strip()
        self._db_path = value

    @property
    def df(self):
        return self._df.copy()

    @df.setter
    def df(self, value):
        if not isinstance(value, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame")
        required = {"item_name", "category", "region", "is_correct", "created_at"}
        if not required.issubset(value.columns):
            raise ValueError("df is missing required classification columns")
        frame = value.copy()
        frame["created_at"] = pd.to_datetime(frame["created_at"], format="ISO8601")
        feedback = frame["is_correct"].dropna()
        if not feedback.isin([True, False]).all():
            raise ValueError("feedback must be True, False or empty")
        self._df = frame

    def load_data(self, date_filter=None, region=None):
        """Read the classification table, or use data assigned through df."""
        if self.db_path is not None:
            db_uri = Path(self.db_path).resolve().as_uri() + "?mode=ro"
            with closing(sqlite3.connect(db_uri, uri=True)) as conn:
                table = conn.execute(
                    "SELECT name FROM sqlite_master "
                    "WHERE type = 'table' AND name = 'classification'"
                ).fetchone()
                if table is None:
                    self.df = pd.DataFrame(columns=self.COLUMNS)
                else:
                    self.df = pd.read_sql("SELECT * FROM classification", conn)
        return self._filtered_data(date_filter, region)

    def _filtered_data(self, date_filter=None, region=None):
        data = self._df
        if date_filter is not None:
            if not isinstance(date_filter, DateFilter):
                raise TypeError("date_filter must be a DateFilter")
            dates = data["created_at"].dt.date
            if date_filter.start is not None:
                data = data.loc[dates >= date_filter.start]
            if date_filter.end is not None:
                data = data.loc[data["created_at"].dt.date <= date_filter.end]
        if region is not None:
            if not isinstance(region, str) or not region.strip():
                raise ValueError("region cannot be empty")
            data = data.loc[data["region"].str.lower() == region.strip().lower()]
        return data.copy()

    def total(self, date_filter=None, region=None):
        return len(self._filtered_data(date_filter, region))

    def by_category(self, date_filter=None, region=None):
        data = self._filtered_data(date_filter, region)
        return data["category"].value_counts().to_dict()

    def per_day(self, date_filter=None, region=None):
        data = self._filtered_data(date_filter, region)
        days = data["created_at"].dt.strftime("%Y-%m-%d")
        return data.groupby(days).size().to_dict()

    def recycling_rate(self, date_filter=None, region=None):
        """Return the percentage of packaging, paper, glass and organic items."""
        data = self._filtered_data(date_filter, region)
        if data.empty:
            return 0.0
        recyclable = data["category"].isin(["packaging", "paper", "glass", "organic"])
        return round(float(np.mean(recyclable.to_numpy()) * 100), 2)

    def accuracy(self, date_filter=None, region=None):
        """Return the percentage correct among results with user feedback."""
        data = self._filtered_data(date_filter, region)
        feedback = data["is_correct"].dropna()
        if feedback.empty:
            return 0.0
        return round(float(feedback.eq(True).mean() * 100), 2)

    def top_items(self, n=5, date_filter=None, region=None):
        if not isinstance(n, int) or n < 1:
            raise ValueError("n must be a whole number of at least 1")
        data = self._filtered_data(date_filter, region)
        counts = data["item_name"].value_counts().head(n)
        return [
            {"item_name": item, "count": int(count)}
            for item, count in counts.items()
        ]

    def wrong_results(self, date_filter=None, region=None):
        data = self._filtered_data(date_filter, region)
        wrong = data.loc[data["is_correct"].eq(False)].copy()
        wrong["created_at"] = wrong["created_at"].dt.strftime("%Y-%m-%d %H:%M:%S")
        return wrong.to_dict("records")

    def chart_data(self, date_filter=None, region=None):
        """Return the dashboard numbers and chart values."""
        data = self._filtered_data(date_filter, region)
        return {
            "total": self.total(date_filter, region),
            "by_category": self.by_category(date_filter, region),
            "per_day": self.per_day(date_filter, region),
            "recycling_rate": self.recycling_rate(date_filter, region),
            "accuracy": self.accuracy(date_filter, region),
            "reviewed": int(data["is_correct"].notna().sum()),
            "top_items": self.top_items(5, date_filter, region),
        }
