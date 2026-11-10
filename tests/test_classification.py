
import pytest
import sqlite3
from io import BytesIO

from app.classification.classification_service import ClassificationService



class FakeOpenAIClient:
    """Simulates OpenAI without making real API calls."""

    def analyze_text(self, text):
        return {
            "item_name": text,
            "category": "paper",
            "explanation": "This belongs in paper recycling."
        }

    def analyze_image(self, image):
        return {
            "item_name": "Glass bottle",
            "category": "glass",
            "explanation": "This belongs in glass recycling."
        }


# Test 1: Classify valid text
def test_classify_valid_text():
    service = ClassificationService(FakeOpenAIClient())
    result = service.classify_text("Newspaper", "Dortmund")

    assert result.item_name == "Newspaper"
    assert result.category == "paper"
    assert result.region == "Dortmund"
    assert result.input_type == "text"


# Test 2: Classify valid image
def test_classify_valid_image():
    service = ClassificationService(FakeOpenAIClient())
    result = service.classify_image(b"fake image data", "Berlin")

    assert result.item_name == "Glass bottle"
    assert result.category == "glass"
    assert result.region == "Berlin"
    assert result.input_type == "image"


# Test 3: Reject empty text
def test_classify_rejects_empty_text():
    service = ClassificationService(FakeOpenAIClient())

    with pytest.raises(ValueError, match="Item name cannot be empty"):
        service.classify_text("   ", "Dortmund")


# Test 4: Reject empty image
def test_classify_rejects_empty_image():
    service = ClassificationService(FakeOpenAIClient())

    with pytest.raises(ValueError, match="Image cannot be empty"):
        service.classify_image(b"", "Dortmund")



# Test 5: Check JSON error response when database fails
def test_classification_error_returns_json(client, monkeypatch):
    repository = client.application.config["CLASSIFICATION_REPOSITORY"]

    def fake_database_error(limit):
        raise sqlite3.OperationalError("Database unavailable")

    monkeypatch.setattr(repository, "get_recent", fake_database_error)

    response = client.get("/api/classifications")

    assert response.status_code == 500
    assert response.get_json() == {
        "error": "Could not load classifications."
    }


# Final Capstone Project - Subsystem 1 Tests


# Test 6: Successful text classification through Flask API
def test_api_classify_text(client, monkeypatch):
    service = client.application.config["CLASSIFICATION_SERVICE"]
    monkeypatch.setattr(service, "ai_client", FakeOpenAIClient())

    response = client.post("/api/classify", data={
        "region": "Dortmund",
        "text": "Newspaper"
    })

    assert response.status_code == 201

    data = response.get_json()

    assert data["item_name"] == "Newspaper"
    assert data["category"] == "paper"
    assert data["region"] == "Dortmund"
    assert data["input_type"] == "text"
    assert data["id"] is not None
    assert data["bin_name"]
    assert data["bin_color"]
    assert data["tip"]


# Test 7: Classification is saved in the database
def test_api_classification_saved(client, monkeypatch):
    service = client.application.config["CLASSIFICATION_SERVICE"]
    monkeypatch.setattr(service, "ai_client", FakeOpenAIClient())

    response = client.post("/api/classify", data={
        "region": "Dortmund",
        "text": "Newspaper"
    })

    assert response.status_code == 201

    classification_id = response.get_json()["id"]

    repository = client.application.config[
        "CLASSIFICATION_REPOSITORY"
    ]

    records = repository.get_recent(20)

    assert any(
        record["id"] == classification_id
        and record["item_name"] == "Newspaper"
        for record in records
    )


# Test 8: Reject missing classification input
def test_api_classify_missing_input(client):
    response = client.post("/api/classify", data={
        "region": "Dortmund"
    })

    assert response.status_code == 400
    assert "error" in response.get_json()


# Test 9: Reject text and image provided together
def test_api_classify_both_inputs(client):
    response = client.post("/api/classify", data={
        "region": "Dortmund",
        "text": "Newspaper",
        "image": (BytesIO(b"fake image"), "photo.jpg")
    })

    assert response.status_code == 400
    assert "error" in response.get_json()


# Test 10: Reject invalid city
def test_api_classify_invalid_city(client):
    response = client.post("/api/classify", data={
        "region": "InvalidCity123",
        "text": "Newspaper"
    })

    assert response.status_code == 400
    assert "error" in response.get_json()


# Test 11: Reject unsupported image format
def test_api_classify_invalid_image_type(client):
    response = client.post("/api/classify", data={
        "region": "Dortmund",
        "image": (BytesIO(b"fake image"), "photo.gif")
    })

    assert response.status_code == 400
    assert "error" in response.get_json()


# Test 12: Reject images larger than 5 MB
def test_api_classify_large_image(client):
    large_image = b"\xff\xd8\xff" + b"0" * (
        5 * 1024 * 1024
    )

    response = client.post("/api/classify", data={
        "region": "Dortmund",
        "image": (BytesIO(large_image), "large.jpg")
    })

    assert response.status_code == 413
    assert "error" in response.get_json()


# Test 13: Successful JPG upload
def test_api_classify_jpg(client, monkeypatch):
    service = client.application.config["CLASSIFICATION_SERVICE"]
    monkeypatch.setattr(service, "ai_client", FakeOpenAIClient())

    image = b"\xff\xd8\xff" + b"fake jpg content"

    response = client.post("/api/classify", data={
        "region": "Dortmund",
        "image": (BytesIO(image), "photo.jpg")
    })

    assert response.status_code == 201

    data = response.get_json()

    assert data["category"] == "glass"
    assert data["input_type"] == "image"
    assert data["id"] is not None


# Test 14: Successful PNG upload
def test_api_classify_png(client, monkeypatch):
    service = client.application.config["CLASSIFICATION_SERVICE"]
    monkeypatch.setattr(service, "ai_client", FakeOpenAIClient())

    image = b"\x89PNG\r\n\x1a\n" + b"fake png content"

    response = client.post("/api/classify", data={
        "region": "Dortmund",
        "image": (BytesIO(image), "photo.png")
    })

    assert response.status_code == 201
    assert response.get_json()["input_type"] == "image"


# Test 15: Correct feedback is saved
def test_api_feedback_correct(client):
    repository = client.application.config[
        "CLASSIFICATION_REPOSITORY"
    ]

    classification_id = repository.add(
        "Newspaper", "paper", "Dortmund",
        "Blue Bin", "Paper recycling", "text"
    )

    response = client.post(
        f"/api/classifications/{classification_id}/feedback",
        json={"is_correct": True}
    )

    assert response.status_code == 200

    with sqlite3.connect(repository.db_path) as conn:
        value = conn.execute(
            "SELECT is_correct FROM classification WHERE id = ?",
            (classification_id,)
        ).fetchone()[0]

    assert value == 1


# Test 16: Wrong feedback is saved
def test_api_feedback_wrong(client):
    repository = client.application.config[
        "CLASSIFICATION_REPOSITORY"
    ]

    classification_id = repository.add(
        "Newspaper", "paper", "Dortmund",
        "Blue Bin", "Paper recycling", "text"
    )

    response = client.post(
        f"/api/classifications/{classification_id}/feedback",
        json={"is_correct": False}
    )

    assert response.status_code == 200

    with sqlite3.connect(repository.db_path) as conn:
        value = conn.execute(
            "SELECT is_correct FROM classification WHERE id = ?",
            (classification_id,)
        ).fetchone()[0]

    assert value == 0


# Test 17: Reject invalid feedback
def test_api_feedback_invalid(client):
    response = client.post(
        "/api/classifications/1/feedback",
        json={"is_correct": "yes"}
    )

    assert response.status_code == 400


# Test 18: Reject feedback for nonexistent classification
def test_api_feedback_not_found(client):
    response = client.post(
        "/api/classifications/999999/feedback",
        json={"is_correct": True}
    )

    assert response.status_code == 404


# Test 19: Reject unrecognised classification
def test_unrecognised_item():
    class UnknownAIClient:
        def analyze_text(self, text):
            return {
                "item_name": text,
                "category": "unknown",
                "explanation": "Item not recognised."
            }

    service = ClassificationService(UnknownAIClient())

    with pytest.raises(
        ValueError,
        match="Not recognised, please try again"
    ):
        service.classify_text("Unknown object", "Dortmund")

