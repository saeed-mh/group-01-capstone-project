
import sqlite3
from datetime import datetime


class ClassificationRepository:
    """Stores and retrieves waste classifications using SQLite."""

    def __init__(self, db_path):
        self.db_path = db_path

    def init_db(self):
        """Create the classification table if it does not exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS classification (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    region TEXT NOT NULL,
                    bin_name TEXT,
                    explanation TEXT,
                    input_type TEXT NOT NULL,
                    is_correct INTEGER,
                    created_at TEXT NOT NULL
                )
            """)

    def add(self, item_name, category, region, bin_name,
            explanation, input_type, is_correct=None):
        """Add a new classification to the database."""

        created_at = datetime.now().isoformat(timespec="seconds")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO classification
                (item_name, category, region, bin_name,
                 explanation, input_type, is_correct, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item_name, category, region, bin_name,
                explanation, input_type, is_correct, created_at
            ))

            return cursor.lastrowid

    def get_recent(self, limit=10):
        """Return the latest classification records."""

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            rows = conn.execute("""
                SELECT * FROM classification
                ORDER BY created_at DESC, id DESC
                LIMIT ?
            """, (limit,)).fetchall()

        return [dict(row) for row in rows]

    def load_seed(self):
        """Insert demo classifications if the table is empty."""

        with sqlite3.connect(self.db_path) as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM classification"
            ).fetchone()[0]

        if count > 0:
            return

        demo_data = [
            ("Plastic bottle", "packaging", "Dortmund",
             "Yellow Bin", "Plastic packaging",
             "text", True),

            ("Newspaper", "paper", "Dortmund",
             "Blue Bin", "Paper waste",
             "text", True),

            ("Glass bottle", "glass", "Dortmund",
             "Glass Container", "Glass waste",
             "image", True),

            ("Banana peel", "organic", "Dortmund",
             "Brown Bin", "Organic food waste",
             "text", True),

            ("Used tissue", "residual", "Dortmund",
             "Black Bin", "Residual waste",
             "image", None),

            ("Battery", "hazardous", "Dortmund",
             "Collection Point", "Hazardous waste",
             "text", None)
        ]

        for item in demo_data:
            self.add(*item)
