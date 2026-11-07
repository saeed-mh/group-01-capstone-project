
import pytest
import sqlite3

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

