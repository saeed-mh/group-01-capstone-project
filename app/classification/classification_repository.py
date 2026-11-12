
import sqlite3
from datetime import datetime


class ClassificationRepository:
    """Stores and retrieves waste classifications using SQLite"""

    def __init__(self, db_path):
        # Store the database file path
        self.db_path = db_path

    def init_db(self):
        """Create the classification table if it does not exist"""
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

        # Generate a timestamp for the new record
        created_at = datetime.now().isoformat(timespec="seconds")

        # Insert the classification using parameterized SQL        
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

            # Return the automatically generated database ID
            return cursor.lastrowid

    def get_recent(self, limit=10):
        """Return the latest classification records."""

        with sqlite3.connect(self.db_path) as conn:
            # Allow database rows to be accessed by column names
            conn.row_factory = sqlite3.Row

            rows = conn.execute("""
                SELECT * FROM classification
                ORDER BY created_at DESC, id DESC
                LIMIT ?
            """, (limit,)).fetchall()

        # Convert the returned rows into dictionaries
        return [dict(row) for row in rows]

    
    def update_feedback(self, classification_id, is_correct):
        """Update Correct/Wrong feedback for a saved classification"""

        if not isinstance(is_correct, bool):
            raise ValueError("Feedback must be True or False")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                UPDATE classification
                SET is_correct = ?
                WHERE id = ?
            """, (int(is_correct), classification_id))

            # Return True if at least one record was updated
            return cursor.rowcount > 0

    
    def load_seed(self):
        """Insert demo classifications if the table is empty"""

        with sqlite3.connect(self.db_path) as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM classification"
            ).fetchone()[0]

        # Avoid inserting duplicate demo data
        if count > 0:
            return

        
        demo_data = [
            ("Plastic bottle", "packaging", "Dortmund",
             "Gelbe Tonne", "Plastic packaging",
             "text", True),

            ("Newspaper", "paper", "Dortmund",
             "Blaue Tonne", "Paper waste",
             "text", True),

            ("Glass bottle", "glass", "Dortmund",
             "Glascontainer", "Glass waste",
             "image", True),

            ("Banana peel", "organic", "Dortmund",
             "Biotonne", "Organic food waste",
             "text", True),

            ("Used tissue", "residual", "Dortmund",
             "Graue Tonne", "Residual waste",
             "image", None),

            ("Battery", "hazardous", "Dortmund",
             "Wertstoffhof / Schadstoffmobil", "Hazardous waste",
             "text", None)
        ]


        for item in demo_data:
            self.add(*item)
