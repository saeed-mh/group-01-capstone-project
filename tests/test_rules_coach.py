import pytest

from app.rules_coach.recycling_rule import RecyclingRule
from app.rules_coach.rule_repository import RuleRepository
from app.rules_coach.sustainability_coach import SustainabilityCoach


class FakeOpenAIClient:
    def chat(self, prompt):
        return prompt


class BrokenAIClient:
    def chat(self, prompt):
        raise RuntimeError("AI is not reachable")


def test_bins_returns_rules_for_known_city(client):
    response = client.get("/api/bins?region=Berlin")

    assert response.status_code == 200
    assert len(response.get_json()) == 6


def test_bins_returns_404_for_unknown_city(client):
    response = client.get("/api/bins?region=Paris")

    assert response.status_code == 404
    assert response.get_json() == {"error": "No rules found for Paris"}


def test_recycling_rule_rejects_empty_region():
    with pytest.raises(ValueError):
        RecyclingRule(
            None,
            "   ",
            "paper",
            "Blaue Tonne",
            "#1F5FAD",
            "Flatten boxes.",
            "newspaper",
        )


def test_coach_prompt_uses_only_selected_city(client):
    rule_service = client.application.config["RULE_SERVICE"]
    coach = SustainabilityCoach(FakeOpenAIClient(), rule_service)

    prompt = coach.ask("Where do batteries go?", "Berlin")

    assert "Schadstoffsammelstelle" in prompt
    assert "Wertstoffhof" not in prompt


def test_repository_update_changes_the_rule(tmp_path):
    repository = RuleRepository(str(tmp_path / "rules.db"))
    repository.init_db()
    rule_id = repository.add(
        RecyclingRule(
            None,
            "Berlin",
            "paper",
            "Blaue Tonne",
            "#1F5FAD",
            "Flatten boxes.",
            "newspaper",
        )
    )

    repository.update(
        RecyclingRule(
            rule_id,
            "Berlin",
            "paper",
            "Papiertonne",
            "#1F5FAD",
            "Flatten boxes.",
            "newspaper",
        )
    )

    rules = repository.get_all()
    assert len(rules) == 1
    assert rules[0].bin_name == "Papiertonne"


def test_search_finds_singular_for_plural_example(client):
    response = client.get("/api/search?q=battery&region=Berlin")

    assert response.status_code == 200
    rules = response.get_json()
    assert len(rules) == 1
    assert rules[0]["category"] == "hazardous"


def test_search_finds_plural_for_singular_example(client):
    response = client.get("/api/search?q=bottles&region=Dortmund")

    assert response.status_code == 200
    categories = {rule["category"] for rule in response.get_json()}
    assert categories == {"packaging", "glass"}


def test_search_returns_empty_list_when_nothing_matches(client):
    response = client.get("/api/search?q=xyz&region=Dortmund")

    assert response.status_code == 200
    assert response.get_json() == []


def test_search_rejects_empty_text(client):
    response = client.get("/api/search?q=&region=Dortmund")

    assert response.status_code == 400
    assert response.get_json() == {"error": "Please type an item to search."}


def test_coach_route_answers_with_city_rules(client, monkeypatch):
    coach = client.application.config["COACH"]
    monkeypatch.setattr(coach, "openai_client", FakeOpenAIClient())

    response = client.post(
        "/api/coach", json={"question": "Where do batteries go?", "region": "Dortmund"}
    )

    assert response.status_code == 200
    answer = response.get_json()["answer"]
    assert "Where do batteries go?" in answer
    assert "Wertstoffhof" in answer


def test_coach_route_rejects_empty_question(client):
    response = client.post("/api/coach", json={"question": "   ", "region": "Dortmund"})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Please type a question."}


def test_coach_route_returns_503_when_ai_fails(client, monkeypatch):
    coach = client.application.config["COACH"]
    monkeypatch.setattr(coach, "openai_client", BrokenAIClient())

    response = client.post(
        "/api/coach", json={"question": "Where do batteries go?", "region": "Dortmund"}
    )

    assert response.status_code == 503
    assert response.get_json() == {"error": "The coach is not available right now."}


def test_tip_route_uses_only_selected_city(client, monkeypatch):
    coach = client.application.config["COACH"]
    monkeypatch.setattr(coach, "openai_client", FakeOpenAIClient())

    response = client.get("/api/tip?region=Berlin")

    assert response.status_code == 200
    tip = response.get_json()["tip"]
    assert "recycling coach for Berlin" in tip
    assert "Wertstoffhof" not in tip


@pytest.fixture
def admin_headers(monkeypatch):
    """Set a known admin password for the test and return the matching header."""
    monkeypatch.setenv("ADMIN_PASSWORD", "test-password")
    return {"X-Admin-Password": "test-password"}


NEW_RULE = {
    "region": "Hamburg",
    "category": "glass",
    "bin_name": "Glascontainer",
    "bin_color": "#2E8B57",
    "instructions": "Sort by colour.",
    "examples": "wine bottle",
}


def test_admin_rejects_wrong_password(client, admin_headers):
    response = client.post(
        "/api/rules", json=NEW_RULE, headers={"X-Admin-Password": "wrong"}
    )

    assert response.status_code == 401
    assert response.get_json() == {"error": "Wrong admin password."}


def test_admin_can_add_rule(client, admin_headers):
    response = client.post("/api/rules", json=NEW_RULE, headers=admin_headers)

    assert response.status_code == 201
    assert "Hamburg" in client.get("/api/regions").get_json()


def test_admin_rejects_empty_field(client, admin_headers):
    rule = {**NEW_RULE, "bin_name": "  "}

    response = client.post("/api/rules", json=rule, headers=admin_headers)

    assert response.status_code == 400
    assert response.get_json() == {"error": "bin name cannot be empty"}


def test_admin_can_update_rule(client, admin_headers):
    rule_id = client.post(
        "/api/rules", json=NEW_RULE, headers=admin_headers
    ).get_json()["id"]
    changed = {**NEW_RULE, "bin_name": "Altglascontainer"}

    response = client.put(f"/api/rules/{rule_id}", json=changed, headers=admin_headers)

    assert response.status_code == 200
    rules = client.get("/api/bins?region=Hamburg").get_json()
    assert rules[0]["bin_name"] == "Altglascontainer"


def test_admin_can_delete_rule_only_once(client, admin_headers):
    rule_id = client.post(
        "/api/rules", json=NEW_RULE, headers=admin_headers
    ).get_json()["id"]

    first = client.delete(f"/api/rules/{rule_id}", headers=admin_headers)
    second = client.delete(f"/api/rules/{rule_id}", headers=admin_headers)

    assert first.status_code == 200
    assert second.status_code == 404


def test_admin_update_missing_rule_returns_404(client, admin_headers):
    response = client.put("/api/rules/999", json=NEW_RULE, headers=admin_headers)

    assert response.status_code == 404
    assert response.get_json() == {"error": "Rule not found."}
