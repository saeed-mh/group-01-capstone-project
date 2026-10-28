from app.rules_coach.rule_service import RuleService


class SustainabilityCoach:
    """Answers recycling questions with OpenAI, using only the selected city's rules."""

    def __init__(self, openai_client, rule_service, max_sentences=4):
        self.openai_client = openai_client
        self.rule_service = rule_service
        self.max_sentences = max_sentences

    def _build_prompt(self, region):
        """Build the instructions for OpenAI with only this city's rules."""
        lines = [
            f"- {rule.category}: {rule.bin_name}. {rule.instructions} Examples: {rule.examples}"
            for rule in self.rule_service.get_rules(region)
        ]
        rules_text = "\n".join(lines)
        return (
            f"You are a recycling coach for {region}.\n"
            f"Use only these rules:\n{rules_text}\n"
            f"Answer in at most {self.max_sentences} short, simple sentences.\n"
            "Only answer questions about waste and recycling. "
            "For any other topic, politely say you can only help with recycling."
        )

    def ask(self, question, region):
        """Answer a recycling question using this city's rules."""
        if not question or not question.strip():
            raise ValueError("question cannot be empty")
        prompt = f"{self._build_prompt(region)}\n\nQuestion: {question.strip()}"
        return self.openai_client.chat(prompt)

    def tip_of_the_day(self, region):
        """Ask OpenAI for one short, practical recycling tip for this city."""
        prompt = (
            f"{self._build_prompt(region)}\n\n"
            "Give one short, practical recycling tip of the day for this city, "
            "in one sentence."
        )
        return self.openai_client.chat(prompt)

    @property
    def openai_client(self):
        return self._openai_client

    @openai_client.setter
    def openai_client(self, value):
        if not hasattr(value, "chat"):
            raise TypeError("openai_client must have a chat(prompt) method")
        self._openai_client = value

    @property
    def rule_service(self):
        return self._rule_service

    @rule_service.setter
    def rule_service(self, value):
        if not isinstance(value, RuleService):
            raise TypeError("rule_service must be a RuleService")
        self._rule_service = value

    @property
    def max_sentences(self):
        return self._max_sentences

    @max_sentences.setter
    def max_sentences(self, value):
        if not isinstance(value, int) or value < 1:
            raise ValueError("max_sentences must be a whole number of at least 1")
        self._max_sentences = value
