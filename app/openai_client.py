import base64
import json
import os

from dotenv import load_dotenv
from openai import OpenAI


class OpenAIClient:
    """Handles communication with an OpenAI-compatible API (OpenAI or Gemini)."""

    def __init__(self, api_key=None, model=None):
        load_dotenv()

        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")

        if model is None:
            model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

        self.api_key = api_key
        self.model = model
        self._client = None

    @property
    def api_key(self):
        return self._api_key

    @api_key.setter
    def api_key(self, value):
        self._api_key = value

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        if not value:
            raise ValueError("Model name cannot be empty")
        self._model = value

    def initialize(self):
        if not self.api_key:
            raise ValueError("OpenAI API key is missing")

        self._client = OpenAI(
            api_key=self.api_key, base_url=os.getenv("OPENAI_BASE_URL")
        )

    def chat(self, prompt):
        if self._client is None:
            self.initialize()

        response = self._client.chat.completions.create(
            model=self.model, messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def analyze_text(self, text):
        prompt = self._classification_prompt() + text
        answer = self.chat(prompt)

        return self._parse_classification(answer)

    def analyze_image(self, image):
        if not image:
            raise ValueError("Image cannot be empty")

        if image.startswith(b"\xff\xd8\xff"):
            mime_type = "image/jpeg"
        elif image.startswith(b"\x89PNG\r\n\x1a\n"):
            mime_type = "image/png"
        else:
            raise ValueError("Only JPG and PNG images are supported")

        if self._client is None:
            self.initialize()

        encoded_image = base64.b64encode(image).decode("utf-8")

        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": self._classification_prompt()},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{encoded_image}"
                            },
                        },
                    ],
                }
            ],
        )

        return self._parse_classification(response.choices[0].message.content)

    def _parse_classification(self, answer):
        """Parse and validate the AI classification response."""
        if isinstance(answer, str):
            answer = (
                answer.strip()
                .removeprefix("```json")
                .removeprefix("```")
                .removesuffix("```")
                .strip()
            )

        try:
            result = json.loads(answer)
        except (json.JSONDecodeError, TypeError):
            raise ValueError("Not recognised, please try again")

        if not isinstance(result, dict):
            raise ValueError("Not recognised, please try again")

        required_keys = ("item_name", "category", "explanation")

        if not all(key in result for key in required_keys):
            raise ValueError("Not recognised, please try again")

        return result

    def _classification_prompt(self):
        return (
            "Identify this waste item. "
            "Choose one category: packaging, paper, glass, "
            "organic, residual, or hazardous. "
            "If the item cannot be identified reliably, "
            "use category 'unknown'. "
            "Return only valid JSON with these keys: "
            "item_name, category, explanation. "
            "Keep the explanation short and clear. "
            "Waste item: "
        )
