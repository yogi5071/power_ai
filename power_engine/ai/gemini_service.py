"""
Gemini AI Service
Power AI Copilot
"""

import logging
import time

from google import genai

from config.settings import Settings
from power_engine.ai.base_client import BaseClient


logger = logging.getLogger(__name__)


class GeminiService(BaseClient):
    """
    Gemini API wrapper.

    Responsibilities
    ----------------
    - Send prompt
    - Receive response
    - Handle transient API errors

    MUST NOT:
    - Execute business rules
    - Access database
    - Build prompts
    """

    # Total attempts, including the first request.
    MAX_RETRY = 3

    # Exponential backoff between retries.
    RETRY_DELAYS = (2, 4)

    def __init__(self):

        Settings.validate()

        self.client = genai.Client(
            api_key=Settings.GEMINI_API_KEY
        )

        self.model = Settings.GEMINI_MODEL

    @staticmethod
    def _status_code(error):
        """
        Best-effort extraction of HTTP status code from the SDK exception.

        Different google-genai versions may expose the status differently,
        so this method intentionally checks several common locations.
        """

        code = getattr(error, "status_code", None)

        if code is None:
            code = getattr(error, "code", None)

        response = getattr(error, "response", None)

        if code is None and response is not None:
            code = getattr(response, "status_code", None)

        try:
            return int(code) if code is not None else None
        except (TypeError, ValueError):
            return None

    @classmethod
    def _is_transient_error(cls, error, status_code):
        """Return whether a failed request is safe to retry."""
        if status_code in {408, 429, 500, 502, 503, 504}:
            return True

        if isinstance(error, (ConnectionError, TimeoutError)):
            return True

        error_name = type(error).__name__.lower()
        return any(token in error_name for token in (
            "connection", "timeout", "unavailable", "temporary",
        ))

    def generate(self, prompt: str) -> str:

        last_error = None

        for attempt in range(1, self.MAX_RETRY + 1):

            try:

                logger.info(
                    "Gemini request attempt %d/%d | model=%s",
                    attempt,
                    self.MAX_RETRY,
                    self.model,
                )

                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )

                result = (response.text or "").strip()

                logger.info(
                    "Gemini request succeeded on attempt %d/%d",
                    attempt,
                    self.MAX_RETRY,
                )

                return result

            except Exception as error:

                last_error = error
                status_code = self._status_code(error)

                logger.warning(
                    "Gemini request failed | attempt=%d/%d | status=%s | error=%s",
                    attempt,
                    self.MAX_RETRY,
                    status_code,
                    error,
                )

                # Do not retry the final attempt.
                if attempt >= self.MAX_RETRY:
                    break

                if self._is_transient_error(error, status_code):
                    delay = self.RETRY_DELAYS[attempt - 1]

                    logger.warning(
                        "Gemini returned a transient error. "
                        "Retrying in %s seconds...",
                        delay,
                    )

                    time.sleep(delay)
                    continue

                # Unknown/non-transient errors should not be retried
                # repeatedly.
                break

        raise RuntimeError(
            f"Gemini Error : {last_error}"
        ) from last_error

    def chat(self, message: str) -> str:
        """
        Future chat interface.
        """

        return self.generate(message)
