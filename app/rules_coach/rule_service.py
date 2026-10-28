from app.rules_coach.rule_repository import RuleRepository


class RuleService:
    """Finds the right recycling rule for a category and city."""

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

    def get_rules(self, region):
        """Return all rules of one city."""
        return [
            rule
            for rule in self.repository.get_all()
            if rule.region.lower() == region.lower()
        ]

    def search(self, text, region):
        """Return all rules of this city whose category, bin or examples contain the text."""
        text = text.lower().strip()
        results = []
        for rule in self.repository.get_all():
            if rule.region.lower() != region.lower():
                continue
            searchable = f"{rule.category} {rule.bin_name} {rule.examples}".lower()
            if text in searchable:
                results.append(rule)
        return results
