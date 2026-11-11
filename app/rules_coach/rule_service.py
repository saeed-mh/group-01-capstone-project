from app.rules_coach.recycling_rule import RecyclingRule
from app.rules_coach.rule_repository import RuleRepository


class RuleService:
    """Finds the right recycling rule for a category and city."""

    FIELDS = ("region", "category", "bin_name", "bin_color", "instructions", "examples")

    def __init__(self, repository):
        self.repository = repository

    @property
    def repository(self):
        return self._repository

    @repository.setter
    def repository(self, value):
        if not isinstance(value, RuleRepository):
            raise TypeError("repository must be a RuleRepository")
        self._repository = value

    def get_rule(self, category, region):
        """Return the rule for this category in this city, or None if there is none."""
        for rule in self.repository.get_all():
            if (
                rule.category.lower() == category.lower()
                and rule.region.lower() == region.lower()
            ):
                return rule
        return None

    def _rule_from_data(self, rule_id, data):
        """Build a RecyclingRule from a dict (e.g. JSON from the admin page)."""
        values = [str(data.get(field) or "") for field in self.FIELDS]
        return RecyclingRule(rule_id, *values)

    def get_all_rules(self):
        """Return the rules of all cities."""
        return self.repository.get_all()

    def add_rule(self, data):
        """Check the data, save a new rule and return its id."""
        rule = self._rule_from_data(None, data)
        return self.repository.add(rule)

    def get_rules(self, region):
        """Return all rules of one city."""
        return [
            rule
            for rule in self.repository.get_all()
            if rule.region.lower() == region.lower()
        ]

    def update_rule(self, rule_id, data):
        """Check the data and save it over the rule with this id."""
        rule = self._rule_from_data(rule_id, data)
        return self.repository.update(rule)

    def delete_rule(self, rule_id):
        """Delete the rule with this id."""
        return self.repository.delete(rule_id)

    def get_regions(self):
        """Return all cities that have rules, sorted A–Z."""
        return sorted({rule.region for rule in self.repository.get_all()})

    def _normalize(self, text):
        """Lowercase the text and turn plural words into singular (batteries -> battery)."""
        words = []
        for word in text.lower().replace(",", " ").split():
            if word.endswith("ies"):
                word = word[:-3] + "y"
            elif word.endswith("s"):
                word = word[:-1]
            words.append(word)
        return " ".join(words)

    def search(self, text, region):
        """Return all rules of this city whose category, bin or examples contain the text."""
        text = self._normalize(text)
        if not text:
            return []

        results = []
        for rule in self.repository.get_all():
            if rule.region.lower() != region.lower():
                continue
            searchable = self._normalize(
                f"{rule.category} {rule.bin_name} {rule.examples}"
            )
            if text in searchable:
                results.append(rule)
        return results
