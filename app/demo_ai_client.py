class DemoAIClient:
    """Stand-in for OpenAIClient when no API key is set. Returns fixed text."""

    def chat(self, prompt):
        return (
            "This is a demo answer. Add an API key to .env "
            "to get real answers from the coach."
        )

    
    def analyze_text(self, text):
        """Return a sample classification without calling OpenAI."""

        item = text.strip()
        name = item.lower()

        categories = {
            "bottle": "packaging",
            "plastic": "packaging",
            "newspaper": "paper",
            "paper": "paper",
            "cardboard": "paper",
            "glass": "glass",
            "banana": "organic",
            "food": "organic",
            "battery": "hazardous",
            "tissue": "residual"
        }

        category = "unknown"

        for keyword, value in categories.items():
            if keyword in name:
                category = value
                break

        return {
            "item_name": item,
            "category": category,
            "explanation": (
                "This is a demonstration classification."
                if category != "unknown"
                else "The item was not recognised in demo mode."
            )
        }

    def analyze_image(self, image):
        """Image classification requires an OpenAI API key."""
        raise ValueError(
            "Image classification requires an OpenAI API key."
        )
