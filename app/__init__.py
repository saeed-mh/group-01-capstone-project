import os
import sqlite3

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from app.classification.classification_repository import ClassificationRepository
from app.classification.errors import ClassificationError
from app.demo_ai_client import DemoAIClient
from app.errors import AppError
from app.openai_client import OpenAIClient
from app.rules_coach.errors import RulesCoachError
from app.rules_coach.rule_repository import RuleRepository
from app.rules_coach.rule_service import RuleService
from app.rules_coach.sustainability_coach import SustainabilityCoach
from app.statistics.errors import StatisticsError
from app.statistics.statistics_service import StatisticsService


def create_app():
    """Create and configure the Flask app."""
    load_dotenv()
    app = Flask(__name__, static_folder="../static")

    db_path = os.getenv("DATABASE_PATH", "data/app.db")
    repository = RuleRepository(db_path)
    repository.init_db()
    repository.load_seed("data/rules.csv")
    app.config["RULE_SERVICE"] = RuleService(repository)
    if os.getenv("OPENAI_API_KEY"):
        ai_client = OpenAIClient()
    else:
        ai_client = DemoAIClient()
    app.config["AI_CLIENT"] = ai_client
    app.config["COACH"] = SustainabilityCoach(ai_client, app.config["RULE_SERVICE"])

    classification_repo = ClassificationRepository(db_path)
    classification_repo.init_db()
    classification_repo.load_seed()
    app.config["CLASSIFICATION_REPOSITORY"] = classification_repo

    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify(error.to_dict()), error.status_code

    @app.route("/")
    def home():
        return app.send_static_file("index.html")

    @app.route("/bins")
    def bins_page():
        return app.send_static_file("bins.html")

    @app.route("/api/regions")
    def api_regions():
        return jsonify(app.config["RULE_SERVICE"].get_regions())

    @app.route("/api/bins")
    def api_bins():
        region = request.args.get("region", "Dortmund")
        rules = app.config["RULE_SERVICE"].get_rules(region)
        if not rules:
            raise RulesCoachError(f"No rules found for {region}", 404)
        return jsonify([rule.to_dict() for rule in rules])

    @app.route("/api/coach", methods=["POST"])
    def api_coach():
        data = request.get_json(silent=True) or {}
        question = (data.get("question") or "").strip()
        region = data.get("region", "Dortmund")
        if not question:
            raise RulesCoachError("Please type a question.", 400)
        try:
            answer = app.config["COACH"].ask(question, region)
        except Exception as error:
            raise RulesCoachError(
                "The coach is not available right now.", 503
            ) from error
        return jsonify({"answer": answer})

    @app.route("/classify")
    def classify_page():
        return app.send_static_file("classify.html")

    @app.route("/api/classifications")
    def api_classifications():
        try:
            records = app.config["CLASSIFICATION_REPOSITORY"].get_recent(10)
            return jsonify(records)
        except sqlite3.Error as error:
            raise ClassificationError("Could not load classifications.", 500) from error

    @app.route("/dashboard")
    def dashboard_page():
        return app.send_static_file("dashboard.html")

    @app.route("/api/stats")
    def api_stats():
        try:
            statistics = StatisticsService(db_path)
            statistics.load_data()
            return jsonify(statistics.chart_data())
        except sqlite3.Error as error:
            raise StatisticsError("Could not load statistics.", 500) from error

    return app
