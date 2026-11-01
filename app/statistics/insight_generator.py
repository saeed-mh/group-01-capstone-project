import json


class InsightGenerator:
    """Creates a short AI summary from aggregated statistics."""

    def __init__(self, openai_client):
        self.openai_client = openai_client

    @property
    def openai_client(self):
        return self._openai_client

    @openai_client.setter
    def openai_client(self, value):
        if not callable(getattr(value, "chat", None)):
            raise TypeError("openai_client must have a chat(prompt) method")
        self._openai_client = value

    def summarize(self, stats):
        if not isinstance(stats, dict) or "total" not in stats:
            raise ValueError("stats must be a dictionary containing total")
        if stats["total"] == 0:
            return "No data yet"
        keys = (
            "total", "by_category", "per_day",
            "recycling_rate", "accuracy", "reviewed",
        )
        aggregated = {key: stats[key] for key in keys if key in stats}
        prompt = (
            "Summarize these waste classification statistics in at most "
            "3 short, simple sentences. Use only the supplied numbers. "
            "These are classifications recorded in the app. "
            "Rates are percentages. Accuracy uses only results with user feedback. "
            "If reviewed is zero, say accuracy is not available.\n\n"
            f"Statistics:\n{json.dumps(aggregated)}"
        )
        return self.openai_client.chat(prompt)
