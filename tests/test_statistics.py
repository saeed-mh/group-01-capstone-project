from collections import Counter
from contextlib import closing
import csv
from io import StringIO
from time import perf_counter
import sqlite3

import pandas as pd
import pytest

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
        "wrong_results": [],
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

@pytest.fixture
def filtered_client(client):
    repository = client.application.config["CLASSIFICATION_REPOSITORY"]
    with closing(sqlite3.connect(repository.db_path)) as conn:
        conn.execute("DELETE FROM classification")
        conn.executemany(
            "INSERT INTO classification "
            "(item_name, category, region, is_correct, created_at, input_type) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            [
                ("Newspaper", "paper", "Berlin", True, "2026-11-05T09:00:00", "text"),
                ("Battery", "hazardous", "Berlin", False, "2026-11-06T09:00:00", "text"),
                ("Glass bottle", "glass", "Dortmund", None, "2026-11-05T09:00:00", "image"),
                ("Private item name", "packaging", "Berlin", False, "2026-11-05T15:00:00", "text"),
            ],
        )
        conn.commit()
    return client


def test_stats_api_applies_date_and_city_to_all_results(filtered_client):
    response = filtered_client.get(
        "/api/stats?start=2026-11-05&end=2026-11-05&region=Berlin"
    )
    stats = response.get_json()

    assert response.status_code == 200
    assert stats["total"] == 2
    assert stats["by_category"] == {"paper": 1, "packaging": 1}
    assert stats["per_day"] == {"2026-11-05": 2}
    assert stats["recycling_rate"] == 100.0
    assert stats["accuracy"] == 50.0
    assert stats["reviewed"] == 2
    assert sum(item["count"] for item in stats["top_items"]) == 2
    assert [item["item_name"] for item in stats["wrong_results"]] == ["Private item name"]


def test_csv_matches_filtered_dashboard(filtered_client):
    query = "?start=2026-11-05&end=2026-11-05&region=Berlin"
    stats = filtered_client.get("/api/stats" + query).get_json()
    response = filtered_client.get("/api/stats/export" + query)
    rows = list(csv.DictReader(StringIO(response.get_data(as_text=True))))

    assert response.status_code == 200
    assert "attachment" in response.headers["Content-Disposition"]
    assert len(rows) == stats["total"]
    assert {row["region"] for row in rows} == {"Berlin"}
    assert {row["created_at"][:10] for row in rows} == {"2026-11-05"}
    assert dict(Counter(row["category"] for row in rows)) == stats["by_category"]
    assert sum(float(row["is_correct"]) for row in rows) / len(rows) * 100 == stats["accuracy"]


@pytest.mark.parametrize("query", [
    "?start=not-a-date",
    "?start=2026-11-06&end=2026-11-05",
])
def test_statistics_routes_reject_invalid_dates(client, query):
    assert client.get("/api/stats" + query).status_code == 400
    assert client.get("/api/stats/export" + query).status_code == 400
    assert client.post("/api/stats/summary" + query).status_code == 400


def test_summary_uses_filtered_aggregates_only(filtered_client, monkeypatch):
    monkeypatch.setitem(
        filtered_client.application.config, "AI_CLIENT", FakeOpenAIClient()
    )
    response = filtered_client.post(
        "/api/stats/summary?start=2026-11-05&end=2026-11-05&region=Berlin"
    )
    summary = response.get_json()["summary"]

    assert response.status_code == 200
    assert '"total": 2' in summary
    assert '"accuracy": 50.0' in summary
    assert "Private item name" not in summary
    assert "Newspaper" not in summary
    assert "top_items" not in summary


def test_summary_returns_error_when_ai_fails(client, monkeypatch):
    class BrokenClient:
        def chat(self, prompt):
            raise RuntimeError("AI unavailable")

    monkeypatch.setitem(client.application.config, "AI_CLIENT", BrokenClient())
    response = client.post("/api/stats/summary")

    assert response.status_code == 503
    assert response.get_json() == {"error": "The summary is not available right now."}


def test_empty_summary_does_not_call_ai(client, monkeypatch):
    class UnusedClient:
        def chat(self, prompt):
            raise AssertionError("Empty statistics must not be sent to AI")

    monkeypatch.setitem(client.application.config, "AI_CLIENT", UnusedClient())
    repository = client.application.config["CLASSIFICATION_REPOSITORY"]
    with closing(sqlite3.connect(repository.db_path)) as conn:
        conn.execute("DELETE FROM classification")
        conn.commit()

    response = client.post("/api/stats/summary")
    assert response.status_code == 200
    assert response.get_json() == {"summary": "No data yet"}


def test_demo_data_is_added_once_and_keeps_existing_records(client):
    from seed_demo_data import main

    repository = client.application.config["CLASSIFICATION_REPOSITORY"]
    before = client.get("/api/stats").get_json()["total"]
    main()
    first = client.get("/api/stats").get_json()
    main()
    second = client.get("/api/stats").get_json()

    assert first["total"] == before + 1000
    assert second["total"] == first["total"]
    assert len(first["per_day"]) == 30
    assert first["wrong_results"]
    with closing(sqlite3.connect(repository.db_path)) as conn:
        assert conn.execute("SELECT COUNT(DISTINCT region) FROM classification").fetchone()[0] > 1
        assert conn.execute(
            "SELECT COUNT(*) FROM classification WHERE explanation != ?",
            ("Demo classification for the presentation.",),
        ).fetchone()[0] == before


def test_statistics_for_1000_records_load_within_three_seconds(client):
    repository = client.application.config["CLASSIFICATION_REPOSITORY"]
    with closing(sqlite3.connect(repository.db_path)) as conn:
        conn.execute("DELETE FROM classification")
        conn.executemany(
            "INSERT INTO classification "
            "(item_name, category, region, is_correct, created_at, input_type) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            [("Newspaper", "paper", "Berlin", True, "2026-11-05T12:00:00", "text")] * 1000,
        )
        conn.commit()

    started = perf_counter()
    response = client.get("/api/stats")
    elapsed = perf_counter() - started

    assert response.status_code == 200
    assert response.get_json()["total"] == 1000
    assert elapsed < 3
