

from .classification_result import ClassificationResult


class ClassificationService:
    """Handles waste classification using the OpenAI client."""

    def __init__(self, ai_client, rule_service=None, repository=None):
        self.ai_client = ai_client
        self.rule_service = rule_service
        self.repository = repository

    @property
    def ai_client(self):
        return self._ai_client

    @ai_client.setter
    def ai_client(self, value):
        if value is None:
            raise ValueError("AI client cannot be empty")
        self._ai_client = value

    @property
    def rule_service(self):
        return self._rule_service

    @rule_service.setter
    def rule_service(self, value):
        self._rule_service = value

    @property
    def repository(self):
        return self._repository

    @repository.setter
    def repository(self, value):
        self._repository = value

    def classify_image(self, image, region):
        if not image:
            raise ValueError("Image cannot be empty")

        ai_result = self.ai_client.analyze_image(image)
        return self._create_result(ai_result, region, "image")

    def classify_text(self, text, region):
        if not text or not text.strip():
            raise ValueError("Item name cannot be empty")

        ai_result = self.ai_client.analyze_text(text)
        return self._create_result(ai_result, region, "text")

    def _create_result(self, ai_result, region, input_type):
        category = ai_result["category"]
        bin_name = ""

        if self.rule_service is not None:
            rule = self.rule_service.get_rule(category, region)

            if rule is not None:
                bin_name = rule.bin_name

        result = ClassificationResult(
            id=None,
            item_name=ai_result["item_name"],
            category=category,
            region=region,
            bin_name=bin_name,
            explanation=ai_result["explanation"],
            input_type=input_type
        )

        return result

    def save_feedback(self, id, is_correct):
        if not isinstance(is_correct, bool):
            raise ValueError("Feedback must be True or False")

        if self.repository is None:
            raise ValueError("Database repository is not configured")

        self.repository.update_feedback(id, is_correct)


