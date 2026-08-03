"""
classification/tokenizer.py

Tokenizer for Power AI Copilot.
"""

from __future__ import annotations


class Tokenizer:

    @classmethod
    def tokenize(
        cls,
        text: str
    ) -> list[str]:

        if not text:
            return []

        return text.split()