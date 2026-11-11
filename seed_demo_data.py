from contextlib import closing
from datetime import datetime, timedelta
import os
from pathlib import Path
import sqlite3

from dotenv import load_dotenv

from app.classification.classification_repository import ClassificationRepository
from app.rules_coach.rule_repository import RuleRepository


def main():
    load_dotenv()
    db_path = os.getenv("DATABASE_PATH", "data/app.db")
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    ClassificationRepository(db_path).init_db()
    repository = RuleRepository(db_path)
    repository.init_db()
    repository.load_seed("data/rules.csv")
    rules = {(rule.region, rule.category): rule for rule in repository.get_all()}
    cities = sorted({region for region, category in rules})
    items = [
        ("Plastic bottle", "packaging"),
        ("Newspaper", "paper"),
        ("Glass bottle", "glass"),
        ("Banana peel", "organic"),
        ("Used tissue", "residual"),
        ("Battery", "hazardous"),
    ]
    explanation = "Demo classification for the presentation."
    with closing(sqlite3.connect(db_path)) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM classification WHERE explanation = ?",
            (explanation,),
        ).fetchone()[0]
        if count:
            print("Demo data already exists. No records added.")
            return

        rows = []
        now = datetime.now()
        for index in range(1000):
            item_name, category = items[index % len(items)]
            city = cities[(index // len(items)) % len(cities)]
            rule = rules.get((city, category))
            feedback = (True, True, False, None)[(index // len(items)) % 4]
            created_at = (now - timedelta(days=index % 30)).isoformat(timespec="seconds")
            rows.append((
                item_name, category, city, rule.bin_name if rule else "",
                explanation, "text", feedback, created_at,
            ))
        conn.executemany(
            "INSERT INTO classification "
            "(item_name, category, region, bin_name, explanation, input_type, "
            "is_correct, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            rows,
        )
        conn.commit()
    print("Added 1,000 demo classifications. Existing records were kept.")


if __name__ == "__main__":
    main()
