class DemoAIClient:
    """Stand-in for OpenAIClient when no API key is set. Returns fixed text."""

    def chat(self, prompt):
        return (
            "This is a demo answer. Add an API key to .env "
            "to get real answers from the coach."
        )
