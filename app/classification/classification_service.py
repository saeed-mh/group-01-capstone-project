

from .classification_result import ClassificationResult


class ClassificationService:
    """Handles waste classification using the OpenAI client."""

    def __init__(self, ai_client, rule_service=None, repository=None):
        # Connect the AI client, recycling rules, and database repository
        self.ai_client = ai_client
        self.rule_service = rule_service
        self.repository = repository

    @property
    def ai_client(self):
        return self._ai_client

    @ai_client.setter
    def ai_client(self, value):
        # An AI client is required for classification
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
        # Check that image data was provided
        if not image:
            raise ValueError("Image cannot be empty")

        # Get the AI classification and create a result object
        ai_result = self.ai_client.analyze_image(image)
        return self._create_result(ai_result, region, "image")

    def classify_text(self, text, region):
        if not text or not text.strip():
            raise ValueError("Item name cannot be empty")

        ai_result = self.ai_client.analyze_text(text)
        return self._create_result(ai_result, region, "text")

 
    def _create_result(self, ai_result, region, input_type):
        # The AI response must contain classification data in a dictionary
        if not isinstance(ai_result, dict):
            raise ValueError("Not recognised, please try again")

        category = ai_result.get("category")
        item_name = ai_result.get("item_name")
        explanation = ai_result.get("explanation", "")

        # Validate the category and item name before creating the result
        if (
            not isinstance(category, str)
            or category.strip().lower() not in {
                "packaging", "paper", "glass",
                "organic", "residual", "hazardous"
            }
            or not isinstance(item_name, str)
            or not item_name.strip()
        ):
            raise ValueError("Not recognised, please try again")

        # Normalize the category for matching with recycling rules
        category = category.strip().lower()

        bin_name = ""
        bin_color = ""
        tip = ""

        if self.rule_service is not None:
            rule = self.rule_service.get_rule(category, region)

            if rule is not None:
                bin_name = rule.bin_name
                bin_color = rule.bin_color
                tip = rule.instructions

        # Create a classification result with the validated data
        result = ClassificationResult(
            id=None,
            item_name=item_name,
            category=category,
            region=region,
            bin_name=bin_name,
            explanation=explanation,
            input_type=input_type
        )

        result.bin_color = bin_color
        result.tip = tip

        # Save the classification if a database repository is available
        if self.repository is not None:
            result.id = self.repository.add(
                item_name=result.item_name,
                category=result.category.value,
                region=result.region,
                bin_name=result.bin_name,
                explanation=result.explanation,
                input_type=result.input_type
            )

        return result

    def save_feedback(self, result, is_correct):
        """Store user feedback on a classification result"""

        if not isinstance(is_correct, bool):
            raise ValueError("Feedback must be True or False")

        
        # Feedback can only be saved for an existing database record
        if self.repository is None or result.id is None:
            raise ValueError("Classification is not saved")

        updated = self.repository.update_feedback(
            result.id, is_correct
        )

        if not updated:
            raise ValueError("Classification not found")

        result.is_correct = is_correct
        return result

