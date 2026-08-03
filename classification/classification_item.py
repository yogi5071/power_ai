"""
classification/classification_item.py

Classification Entity

Representasi satu hasil klasifikasi
yang ditemukan dari pertanyaan user.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ClassificationItem:
    """
    Representasi satu entity hasil klasifikasi.

    Contoh

    User:
        battery vrla di sidoarjo

    Entity 1

        field = "jenis_battery"
        value = "VRLA"

    Entity 2

        field = "kabupaten"
        value = "SIDOARJO"
    """

    # =====================================================
    # Business Field
    # =====================================================

    field: str

    # =====================================================
    # Normalized Value
    # =====================================================

    value: Any

    # =====================================================
    # Source
    #
    # exact
    # runtime
    # alias
    # enum
    # fuzzy
    # manual
    # =====================================================

    source: str

    # =====================================================
    # Confidence
    # =====================================================

    confidence: float = 1.0

    # =====================================================
    # Helper
    # =====================================================

    def is_exact(self) -> bool:

        return self.source == "exact"

    def is_runtime(self) -> bool:

        return self.source == "runtime"

    def is_alias(self) -> bool:

        return self.source == "alias"

    def is_enum(self) -> bool:

        return self.source == "enum"

    def is_fuzzy(self) -> bool:

        return self.source == "fuzzy"

    def is_manual(self) -> bool:

        return self.source == "manual"

    # =====================================================
    # Export
    # =====================================================

    def to_dict(self) -> dict:

        return {

            "field": self.field,

            "value": self.value,

            "source": self.source,

            "confidence": self.confidence

        }

    # =====================================================
    # Debug
    # =====================================================

    def __repr__(self) -> str:

        return (

            "ClassificationItem("

            f"field='{self.field}', "

            f"value='{self.value}', "

            f"source='{self.source}', "

            f"confidence={self.confidence:.2f}"

            ")"

        )