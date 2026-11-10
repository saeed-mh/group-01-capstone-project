import os
import sqlite3
from io import BytesIO
from werkzeug.exceptions import RequestEntityTooLarge


from dotenv import load_dotenv
from flask import Flask, jsonify, request
from PIL import Image, UnidentifiedImageError

from app.classification.classification_repository import ClassificationRepository
from app.classification.classification_service import ClassificationService
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
    app.config["MAX_CONTENT_LENGTH"] = 6 * 1024 * 1024

    
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

    classification_service = ClassificationService(
        ai_client=ai_client,
        rule_service=app.config["RULE_SERVICE"],
        repository=classification_repo,
    )

    app.config["CLASSIFICATION_SERVICE"] = classification_service

    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify(error.to_dict()), error.status_code

    
    @app.errorhandler(RequestEntityTooLarge)
    def handle_large_request(error):
        return jsonify({
            "error": "Request too large. Image must not exceed 5 MB."
        }), 413

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

    @app.route("/coach")
    def coach_page():
        return app.send_static_file("coach.html")

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

    @app.route("/api/tip")
    def api_tip():
        region = request.args.get("region", "Dortmund")
        try:
            tip = app.config["COACH"].tip_of_the_day(region)
        except Exception as error:
            raise RulesCoachError("The tip is not available right now.", 503) from error
        return jsonify({"tip": tip})

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

    @app.route("/api/classify", methods=["POST"])
    def api_classify():
        """Classify waste from text or an uploaded image."""

        data = request.get_json(silent=True) if request.is_json else request.form
        data = data or {}

        region = (data.get("region") or "").strip()
        text = (data.get("text") or "").strip()
        image = request.files.get("image")

        if region not in app.config["RULE_SERVICE"].get_regions():
            raise ClassificationError("Please select a valid city.", 400)

        if image is not None and text:
            raise ClassificationError("Please provide either text or an image.", 400)

        if image is None and not text:
            raise ClassificationError("Please enter an item or upload an image.", 400)

        service = app.config["CLASSIFICATION_SERVICE"]

        try:
            if image is not None:
                filename = image.filename or ""
                extension = os.path.splitext(filename)[1].lower()

                if extension not in (".jpg", ".jpeg", ".png"):
                    raise ClassificationError(
                        "Only JPG and PNG images are supported.", 400
                    )

                image_data = image.read(5 * 1024 * 1024 + 1)

                if len(image_data) > 5 * 1024 * 1024:
                    raise ClassificationError("Image must not exceed 5 MB.", 413)

                is_jpeg = image_data.startswith(b"\xff\xd8\xff")
                is_png = image_data.startswith(b"\x89PNG\r\n\x1a\n")

                if not (
                    (extension in (".jpg", ".jpeg") and is_jpeg)
                    or (extension == ".png" and is_png)
                ):
                    raise ClassificationError("Invalid JPG or PNG image.", 400)

                # Verify that the image is genuine and readable.
                try:
                    with Image.open(BytesIO(image_data)) as img:
                        expected_format = "JPEG" if is_jpeg else "PNG"

                        if img.format != expected_format:
                            raise ClassificationError("Invalid JPG or PNG image.", 400)

                        img.verify()

                    # Decode the image to detect corrupt image data.
                    with Image.open(BytesIO(image_data)) as img:
                        img.load()

                except (
                    UnidentifiedImageError,
                    OSError,
                    ValueError,
                    Image.DecompressionBombError,
                ) as error:
                    raise ClassificationError(
                        "Invalid or corrupted image.", 400
                    ) from error

                result = service.classify_image(image_data, region)

            else:
                result = service.classify_text(text, region)

            return jsonify(
                {
                    "id": result.id,
                    "item_name": result.item_name,
                    "category": result.category.value,
                    "region": result.region,
                    "bin_name": result.bin_name,
                    "bin_color": result.bin_color,
                    "tip": result.tip,
                    "explanation": result.explanation,
                    "input_type": result.input_type,
                    "is_correct": result.is_correct,
                }
            ), 201

        except ClassificationError:
            raise
        except ValueError as error:
            raise ClassificationError(str(error), 400) from error
        except sqlite3.Error as error:
            raise ClassificationError("Could not save classification.", 500) from error
        except Exception as error:
            raise ClassificationError(
                "Classification service is unavailable.", 503
            ) from error

    @app.route(
        "/api/classifications/<int:classification_id>/feedback", methods=["POST"]
    )
    def api_classification_feedback(classification_id):
        """Save Correct/Wrong feedback for a classification."""

        data = request.get_json(silent=True)

        if not isinstance(data, dict) or not isinstance(data.get("is_correct"), bool):
            raise ClassificationError("Feedback must be true or false.", 400)

        try:
            updated = app.config["CLASSIFICATION_REPOSITORY"].update_feedback(
                classification_id, data["is_correct"]
            )

            if not updated:
                raise ClassificationError("Classification not found.", 404)

            return jsonify(
                {
                    "id": classification_id,
                    "is_correct": data["is_correct"],
                    "message": "Feedback saved successfully.",
                }
            ), 200

        except ClassificationError:
            raise
        except sqlite3.Error as error:
            raise ClassificationError("Could not save feedback.", 500) from error

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
