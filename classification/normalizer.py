"""
classification/normalizer.py

Normalize user question.

Responsibilities
----------------
- Lowercase
- Remove duplicate spaces
- Remove punctuation (except comparison operators)
- Trim whitespace
"""

from __future__ import annotations

import re


class Normalizer:

    _MULTIPLE_SPACE = re.compile(r"\s+")

    _REMOVE_SYMBOL = re.compile(
        r"[^\w\s><=]"
    )

    @classmethod
    def normalize(
        cls,
        text: str
    ) -> str:

        if not text:
            return ""

        text = text.lower()

        text = cls._REMOVE_SYMBOL.sub(
            " ",
            text
        )

        text = cls._MULTIPLE_SPACE.sub(
            " ",
            text
        )

        return text.strip()