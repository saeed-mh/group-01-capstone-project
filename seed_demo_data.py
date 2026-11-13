# Add 1,000 sample classifications once while keeping existing records.
from contextlib import closing
from datetime import datetime, timedelta
import os
from pathlib import Path
import sqlite3

from dotenv import load_dotenv

from app.classification.classification_repository import ClassificationRepository
from app.rules_coach.rule_repository import RuleRepository


def main():  # Add 1,000 demo rows once, keep existing data and print the outcome; returns None.
    load_dotenv()
    db_path = os.getenv("DATABASE_PATH", "data/app.db")  # Read the configured database path; use data/app.db by default.
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    ClassificationRepository(db_path).init_db()
    repository = RuleRepository(db_path)
    repository.init_db()
    repository.load_seed("data/rules.csv")
    rules = {(rule.region, rule.category): rule for rule in repository.get_all()}  # Dictionary keyed by (city, category), pointing to each recycling rule.
    cities = sorted({region for region, category in rules})  # Set removes duplicate cities; sorted gives a predictable order.
    items = [
        ("Plastic bottle", "packaging"),
        ("Newspaper", "paper"),
        ("Glass bottle", "glass"),
        ("Banana peel", "organic"),
        ("Used tissue", "residual"),
        ("Battery", "hazardous"),
    ]
    explanation = "Demo classification for the presentation."  # This marker identifies rows inserted by this script.
    with closing(sqlite3.connect(db_path)) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM classification WHERE explanation = ?",
            (explanation,),  # One-element tuple containing the SQL parameter.
        ).fetchone()[0]
        if count:  # Skip insertion if the demo marker already exists.
            print("Demo data already exists. No records added.")
            return

        rows = []
        now = datetime.now()
        for index in range(1000):
            item_name, category = items[index % len(items)]  # Remainder cycles through the six sample items.
            city = cities[(index // len(items)) % len(cities)]  # Whole-number division changes city after each group of six items.
            rule = rules.get((city, category))
            feedback = (True, True, False, None)[(index // len(items)) % 4]  # Include Correct, Wrong and unanswered feedback.
            created_at = (now - timedelta(days=index % 30)).isoformat(timespec="seconds")  # Spread records over the last 30 days, formatted as ISO date-time text.
            rows.append((
                item_name, category, city, rule.bin_name if rule else "",
                explanation, "text", feedback, created_at,
            ))
        conn.executemany(  # Execute the same parameterized INSERT for each prepared row.
            "INSERT INTO classification "
            "(item_name, category, region, bin_name, explanation, input_type, "
            "is_correct, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            rows,
        )
        conn.commit()  # Save all inserted records to SQLite.
    print("Added 1,000 demo classifications. Existing records were kept.")


if __name__ == "__main__":  # Run main only when this file is executed as a script.
    main()
