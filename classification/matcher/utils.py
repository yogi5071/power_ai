"""
classification/matcher/utils.py
"""

from __future__ import annotations


def normalize_string(value: str) -> str:
    """
    Normalize string for comparison.
    """

    if value is None:
        return ""

    return value.strip().lower()


def token_equals(
    token: str,
    value: str
) -> bool:
    """
    Exact comparison after normalization.
    """

    return normalize_string(token) == normalize_string(value)