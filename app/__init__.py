import os

from dotenv import load_dotenv
from flask import Flask

from app.rules_coach.rule_repository import RuleRepository
from app.rules_coach.rule_service import RuleService


def create_app():
    """Create and configure the Flask app."""
    load_dotenv()
    app = Flask(__name__)

    db_path = os.getenv("DATABASE_PATH", "data/app.db")
    repository = RuleRepository(db_path)
    repository.init_db()
    repository.load_seed("data/rules.csv")
    app.config["RULE_SERVICE"] = RuleService(repository)

    @app.route("/")
    def home():
        return "Waste Sorting Assistant is running"

    return app
