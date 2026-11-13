from contextlib import closing
from pathlib import Path
import sqlite3

import numpy as np  # NumPy supplies the mean used for recycling rate.
import pandas as pd  # pandas supplies DataFrame tables, filtering and grouped counts.

from app.statistics.date_filter import DateFilter


class StatisticsService:
    """Calculates statistics from loaded waste classifications."""

    COLUMNS = [  # Class variable: column names shared by all service objects.
        "id", "item_name", "category", "region", "bin_name",
        "explanation", "input_type", "is_correct", "created_at",
    ]

    def __init__(self, db_path=None):  # Initialise the path and empty DataFrame; returns None.
        self.db_path = db_path  # Assignment calls the db_path setter for validation.
        self.df = pd.DataFrame(columns=self.COLUMNS)  # Assignment calls the df setter to initialise a valid empty table.

    @property  # Getter: return the saved database path (str or None).
    def db_path(self):
        return self._db_path

    @db_path.setter  # Setter: validate and store the path; returns None.
    def db_path(self, value):
        if value is not None:
            if not isinstance(value, str) or not value.strip():
                raise ValueError("db_path must be a non-empty string or None")
            value = value.strip()
        self._db_path = value

    @property  # Getter: return a copy of the DataFrame, protecting the stored table.
    def df(self):
        return self._df.copy()

    @df.setter  # Setter: validate columns, dates and feedback; store a copy; returns None.
    def df(self, value):
        if not isinstance(value, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame")
        required = {"item_name", "category", "region", "is_correct", "created_at"}  # These columns are required by the calculations.
        if not required.issubset(value.columns):
            raise ValueError("df is missing required classification columns")
        frame = value.copy()
        frame["created_at"] = pd.to_datetime(frame["created_at"], format="ISO8601")  # Convert ISO date-time strings into pandas date-time values.
        feedback = frame["is_correct"].dropna()  # Ignore missing feedback during validation.
        if not feedback.isin([True, False]).all():  # Allow True/False; SQLite values 1 and 0 compare equal too.
            raise ValueError("feedback must be True, False or empty")
        self._df = frame

    def load_data(self, date_filter=None, region=None):  # Load records and return a filtered DataFrame.
        """Read the classification table, or use data assigned through df."""
        if self.db_path is not None:
            db_uri = Path(self.db_path).resolve().as_uri() + "?mode=ro"  # Use an absolute SQLite URI with read-only access.
            with closing(sqlite3.connect(db_uri, uri=True)) as conn:  # closing ensures the connection closes, even after an error.
                table = conn.execute(
                    "SELECT name FROM sqlite_master "
                    "WHERE type = 'table' AND name = 'classification'"
                ).fetchone()  # fetchone returns one matching row, or None if the table is absent.
                if table is None:
                    self.df = pd.DataFrame(columns=self.COLUMNS)  # An absent classification table gives an empty result.
                else:
                    self.df = pd.read_sql("SELECT * FROM classification", conn)  # SELECT * reads all classification columns into pandas.
        return self._filtered_data(date_filter, region)

    def _filtered_data(self, date_filter=None, region=None):  # Return a copy of the rows matching optional dates and city.
        data = self._df
        if date_filter is not None:
            if not isinstance(date_filter, DateFilter):
                raise TypeError("date_filter must be a DateFilter")
            dates = data["created_at"].dt.date  # Use the date part, without the time.
            if date_filter.start is not None:
                data = data.loc[dates >= date_filter.start]  # Inclusive start: keep this day and later days.
            if date_filter.end is not None:
                data = data.loc[data["created_at"].dt.date <= date_filter.end]  # Inclusive end: keep this day and earlier days.
        if region is not None:
            if not isinstance(region, str) or not region.strip():
                raise ValueError("region cannot be empty")
            data = data.loc[data["region"].str.lower() == region.strip().lower()]  # Ignore letter case and trim spaces from the supplied city.
        return data.copy()

    def total(self, date_filter=None, region=None):  # Return the selected classification count (int).
        return len(self._filtered_data(date_filter, region))

    def by_category(self, date_filter=None, region=None):  # Return category counts as a dictionary, e.g. {"paper": 2}.
        data = self._filtered_data(date_filter, region)
        return data["category"].value_counts().to_dict()  # value_counts counts repeated category values.

    def per_day(self, date_filter=None, region=None):  # Return daily counts as a dictionary keyed by YYYY-MM-DD.
        data = self._filtered_data(date_filter, region)
        days = data["created_at"].dt.strftime("%Y-%m-%d")  # Format dates so times on the same day group together.
        return data.groupby(days).size().to_dict()  # Group by day, count each group, then convert to a dictionary.

    def recycling_rate(self, date_filter=None, region=None):  # Return the recyclable share as a percentage (float).
        """Return the percentage of packaging, paper, glass and organic items."""
        data = self._filtered_data(date_filter, region)
        if data.empty:
            return 0.0
        recyclable = data["category"].isin(["packaging", "paper", "glass", "organic"])  # Mark each record True if its category is recyclable.
        return round(float(np.mean(recyclable.to_numpy()) * 100), 2)  # True=1 and False=0: mean * 100 gives the percentage; round to 2 decimals.

    def accuracy(self, date_filter=None, region=None):  # Return the percentage Correct among reviewed results (float).
        """Return the percentage correct among results with user feedback."""
        data = self._filtered_data(date_filter, region)
        feedback = data["is_correct"].dropna()  # Exclude unanswered results from the accuracy denominator.
        if feedback.empty:
            return 0.0  # The page shows No feedback yet when reviewed is zero.
        return round(float(feedback.eq(True).mean() * 100), 2)  # Count True feedback as 1; average only the reviewed results.

    def top_items(self, n=5, date_filter=None, region=None):  # Return up to n frequent items as a list of item_name/count dictionaries.
        if not isinstance(n, int) or n < 1:
            raise ValueError("n must be a whole number of at least 1")
        data = self._filtered_data(date_filter, region)
        counts = data["item_name"].value_counts().head(n)  # head(n) keeps only the n most frequent names.
        return [
            {"item_name": item, "count": int(count)}
            for item, count in counts.items()  # List comprehension: build one dictionary for each item/count pair.
        ]

    def wrong_results(self, date_filter=None, region=None):  # Return a list of records explicitly marked Wrong.
        data = self._filtered_data(date_filter, region)
        wrong = data.loc[data["is_correct"].eq(False)].copy()  # False means Wrong; missing feedback does not match.
        wrong["created_at"] = wrong["created_at"].dt.strftime("%Y-%m-%d %H:%M:%S")  # Format dates as strings for consistent JSON output.
        return wrong.to_dict("records")  # records gives one dictionary per row.

    def chart_data(self, date_filter=None, region=None):  # Return a dashboard dictionary; the route adds wrong_results separately.
        """Return the dashboard numbers and chart values."""
        data = self._filtered_data(date_filter, region)
        return {
            "total": self.total(date_filter, region),
            "by_category": self.by_category(date_filter, region),
            "per_day": self.per_day(date_filter, region),
            "recycling_rate": self.recycling_rate(date_filter, region),
            "accuracy": self.accuracy(date_filter, region),
            "reviewed": int(data["is_correct"].notna().sum()),  # Count records that have feedback, including both Correct and Wrong.
            "top_items": self.top_items(5, date_filter, region),
        }
