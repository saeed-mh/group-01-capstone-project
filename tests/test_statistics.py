from contextlib import closing
import sqlite3

import pandas as pd

from app.statistics.date_filter import DateFilter
from app.statistics.insight_generator import InsightGenerator
from app.statistics.statistics_service import StatisticsService


class FakeOpenAIClient:
    def chat(self, prompt):
        return prompt


def test_stats_returns_dashboard_values(client):
    response = client.get("/api/stats")

    assert response.status_code == 200
    stats = response.get_json()
    assert stats["total"] == 6
    assert stats["by_category"] == {
        "packaging": 1, "paper": 1, "glass": 1,
        "organic": 1, "residual": 1, "hazardous": 1,
    }
    assert sum(stats["per_day"].values()) == 6
    assert stats["recycling_rate"] == 66.67
    assert stats["accuracy"] == 100.0
    assert stats["reviewed"] == 4
    assert len(stats["top_items"]) == 5


def test_stats_returns_zero_values_for_empty_database(client):
    repository = client.application.config["CLASSIFICATION_REPOSITORY"]
    with closing(sqlite3.connect(repository.db_path)) as conn:
        conn.execute("DELETE FROM classification")
        conn.commit()

    response = client.get("/api/stats")

    assert response.status_code == 200
    assert response.get_json() == {
        "total": 0,
        "by_category": {},
        "per_day": {},
        "recycling_rate": 0.0,
        "accuracy": 0.0,
        "reviewed": 0,
        "top_items": [],
    }


def test_stats_returns_json_error_when_database_cannot_be_read(client, monkeypatch):
    def fail_to_load(self):
        raise sqlite3.OperationalError("unable to open database file")

    monkeypatch.setattr(StatisticsService, "load_data", fail_to_load)

    response = client.get("/api/stats")

    assert response.status_code == 500
    assert response.get_json() == {"error": "Could not load statistics."}


def test_statistics_filters_by_date_and_city():
    statistics = StatisticsService()
    statistics.df = pd.DataFrame([
        {"item_name": "Newspaper", "category": "paper", "region": "Berlin",
         "is_correct": True, "created_at": "2026-11-05"},
        {"item_name": "Battery", "category": "hazardous", "region": "Berlin",
         "is_correct": False, "created_at": "2026-11-06"},
        {"item_name": "Glass bottle", "category": "glass", "region": "Dortmund",
         "is_correct": None, "created_at": "2026-11-05"},
    ])
    date_filter = DateFilter("2026-11-05", "2026-11-05")

    assert statistics.total(date_filter, "Berlin") == 1
    assert statistics.by_category(date_filter, "Berlin") == {"paper": 1}
    assert statistics.recycling_rate() == 66.67
    assert statistics.accuracy() == 50.0


def test_insight_uses_aggregated_statistics_only():
    generator = InsightGenerator(FakeOpenAIClient())

    prompt = generator.summarize({
        "total": 1,
        "by_category": {"paper": 1},
        "accuracy": 100.0,
        "reviewed": 1,
        "top_items": [{"item_name": "Private item name", "count": 1}],
    })

    assert '"total": 1' in prompt
    assert '"paper": 1' in prompt
    assert "top_items" not in prompt
    assert "Private item name" not in prompt
