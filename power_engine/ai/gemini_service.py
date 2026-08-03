"""
Gemini AI Service
Power AI Copilot
"""

from google import genai

from config.settings import Settings
from power_engine.ai.base_client import BaseClient


class GeminiService(BaseClient):
    """
    Gemini API wrapper.

    Responsibilities
    ----------------
    - Send prompt
    - Receive response
    - Handle API errors

    MUST NOT:
    - Execute business rules
    - Access database
    - Build prompts
    """

    MAX_RETRY = 2

    def __init__(self):

        Settings.validate()

        self.client = genai.Client(
            api_key=Settings.GEMINI_API_KEY
        )

        self.model = Settings.GEMINI_MODEL

    def generate(self, prompt: str) -> str:

        last_error = None

        for _ in range(self.MAX_RETRY):

            try:

                response = self.client.models.generate_content(

                    model=self.model,

                    contents=prompt

                )

                return (response.text or "").strip()

            except Exception as e:

                last_error = e

        raise RuntimeError(
            f"Gemini Error : {last_error}"
        )

    def chat(self, message: str) -> str:
        """
        Future chat interface.
        """

        return self.generate(message)