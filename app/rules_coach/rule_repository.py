import csv
import sqlite3

from app.rules_coach.recycling_rule import RecyclingRule


class RuleRepository:
    """Saves and loads recycling rules in the SQLite database."""

    def __init__(self, db_path):
        self.db_path = db_path

    def init_db(self):
        """Create the recycling_rule table if it does not exist yet."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS recycling_rule (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    region TEXT NOT NULL,
                    category TEXT NOT NULL,
                    bin_name TEXT NOT NULL,
                    bin_color TEXT NOT NULL,
                    instructions TEXT NOT NULL,
                    examples TEXT NOT NULL
                )
                """
            )

    def get_all(self):
        """Return all rules as a list of RecyclingRule objects."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT id, region, category, bin_name, bin_color, instructions, examples "
                "FROM recycling_rule"
            ).fetchall()
        return [RecyclingRule(*row) for row in rows]

    def add(self, rule):
        """Insert a new rule and return its new id."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO recycling_rule "
                "(region, category, bin_name, bin_color, instructions, examples) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    rule.region,
                    rule.category,
                    rule.bin_name,
                    rule.bin_color,
                    rule.instructions,
                    rule.examples,
                ),
            )
            return cursor.lastrowid

    def update(self, rule):
        """Save changes to an existing rule (found by its id)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE recycling_rule "
                "SET region = ?, category = ?, bin_name = ?, bin_color = ?, "
                "instructions = ?, examples = ? "
                "WHERE id = ?",
                (
                    rule.region,
                    rule.category,
                    rule.bin_name,
                    rule.bin_color,
                    rule.instructions,
                    rule.examples,
                    rule.id,
                ),
            )

    def delete(self, rule_id):
        """Remove the rule with this id."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM recycling_rule WHERE id = ?", (rule_id,))

    def load_seed(self, csv_path):
        """Load rules from a CSV file, but only if the table is still empty."""
        if self.get_all():
            return
        with open(csv_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                rule = RecyclingRule(
                    None,
                    row["region"],
                    row["category"],
                    row["bin_name"],
                    row["bin_color"],
                    row["instructions"],
                    row["examples"],
                )
                self.add(rule)

    @property
    def db_path(self):
        return self._db_path

    @db_path.setter
    def db_path(self, value):
        if not value or not value.strip():
            raise ValueError("db_path cannot be empty")
        self._db_path = value.strip()
