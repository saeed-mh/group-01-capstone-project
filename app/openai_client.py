
import os
import json
import base64
from openai import OpenAI
from dotenv import load_dotenv

class OpenAIClient:
    """Handles communication with the OpenAI API."""

    def __init__(self, api_key=None, model="gpt-4.1-mini"):
        load_dotenv()

        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")

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

        self._client = OpenAI(api_key=self.api_key)

    def chat(self, prompt):
        if self._client is None:
            self.initialize()

        response = self._client.responses.create(
            model=self.model,
            input=prompt
        )

        return response.output_text

    def analyze_text(self, text):
        prompt = self._classification_prompt() + text
        answer = self.chat(prompt)

        return json.loads(answer)

    def analyze_image(self, image):
        if self._client is None:
            self.initialize()

        encoded_image = base64.b64encode(image).decode("utf-8")

        response = self._client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": self._classification_prompt()
                        },
                        {
                            "type": "input_image",
                            "image_url": "data:image/jpeg;base64," + encoded_image
                        }
                    ]
                }
            ]
        )

        return json.loads(response.output_text)

    def _classification_prompt(self):
        return (
            "Identify this waste item. "
            "Choose one category: packaging, paper, glass, "
            "organic, residual, or hazardous. "
            "Return only valid JSON with these keys: "
            "item_name, category, explanation. "
            "Waste item: "
        )
