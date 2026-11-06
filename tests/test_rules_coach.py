import pytest

from app.rules_coach.recycling_rule import RecyclingRule
from app.rules_coach.rule_repository import RuleRepository
from app.rules_coach.sustainability_coach import SustainabilityCoach


class FakeOpenAIClient:
    def chat(self, prompt):
        return prompt


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
