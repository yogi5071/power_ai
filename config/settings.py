"""
Application Settings
Power AI Copilot
"""

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)


class Settings:

    # ==========================================================
    # Gemini
    # ==========================================================

    GEMINI_API_KEY = os.getenv(
        "GEMINI_API_KEY",
        ""
    )

    GEMINI_MODEL = os.getenv(
        "GEMINI_MODEL",
        "gemini-flash-latest"
    )

    TEMPERATURE = float(
        os.getenv(
            "TEMPERATURE",
            "0.2"
        )
    )

    MAX_OUTPUT_TOKENS = int(
        os.getenv(
            "MAX_OUTPUT_TOKENS",
            "2048"
        )
    )

    # ==========================================================
    # Telegram
    # ==========================================================

    BOT_TOKEN = os.getenv(
        "BOT_TOKEN",
        ""
    )

    # ==========================================================
    # Debug
    # ==========================================================

    DEBUG = os.getenv(
        "DEBUG",
        "False"
    ).lower() == "true"

    # ==========================================================
    # Validation
    # ==========================================================

    @classmethod
    def validate(cls):

        if not cls.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY tidak ditemukan pada file .env"
            )

        if not cls.BOT_TOKEN:
            raise ValueError(
                "BOT_TOKEN tidak ditemukan pada file .env"
            )