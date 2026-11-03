import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from app.rules_coach.rule_repository import RuleRepository
from app.rules_coach.rule_service import RuleService


def create_app():
    """Create and configure the Flask app."""
    load_dotenv()
    app = Flask(__name__, static_folder="../static")

    db_path = os.getenv("DATABASE_PATH", "data/app.db")
    repository = RuleRepository(db_path)
    repository.init_db()
    repository.load_seed("data/rules.csv")
    app.config["RULE_SERVICE"] = RuleService(repository)

    @app.route("/")
    def home():
        return "Waste Sorting Assistant is running"

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
        return jsonify([rule.to_dict() for rule in rules])

    return app
