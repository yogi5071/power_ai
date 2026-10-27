"""
classification/classification_result.py

Classification Result

Contract object yang dihasilkan oleh
ClassificationEngine.

Object ini akan menjadi input untuk:

- Planner
- Validator
- SQL Builder
- Explanation Engine
- AIRouter
"""

from __future__ import annotations

from dataclasses import dataclass, field

from classification.classification_item import ClassificationItem


@dataclass(slots=True)
class ClassificationResult:
    """
    Hasil akhir proses klasifikasi.
    """

    # =====================================================
    # Intent
    # =====================================================

    intent: str = "general"

    # =====================================================
    # Entities
    # =====================================================

    entities: list[ClassificationItem] = field(
        default_factory=list
    )

    # =====================================================
    # Operators
    #
    # contoh:
    #
    # umur >
    # voltage <
    # capacity >=
    #
    # nanti berisi object Operator
    # =====================================================

    operators: list = field(
        default_factory=list
    )

    # =====================================================
    # Unknown Tokens
    # =====================================================

    unknown_tokens: list[str] = field(
        default_factory=list
    )

    # =====================================================
    # Warning
    # =====================================================

    warnings: list[str] = field(
        default_factory=list
    )

    # =====================================================
    # Overall Confidence
    # =====================================================

    confidence: float = 0.0

    # =====================================================
    # Status
    # =====================================================

    found: bool = False

    # =====================================================
    # Entity
    # =====================================================

    def add(
        self,
        item: ClassificationItem
    ) -> None:

        self.entities.append(item)

        self.found = True

        self._recalculate_confidence()

    # =====================================================
    # Operator
    # =====================================================

    def add_operator(
        self,
        operator
    ) -> None:

        self.operators.append(operator)

    # =====================================================
    # Warning
    # =====================================================

    def add_warning(
        self,
        warning: str
    ) -> None:

        if warning not in self.warnings:

            self.warnings.append(warning)

    # =====================================================
    # Unknown Token
    # =====================================================

    def add_unknown(
        self,
        token: str
    ) -> None:

        if token not in self.unknown_tokens:

            self.unknown_tokens.append(token)

    # =====================================================
    # Query
    # =====================================================

    def has(
        self,
        field_name: str
    ) -> bool:

        return any(

            item.field == field_name

            for item in self.entities

        )

    def get(
        self,
        field_name: str
    ):

        for item in self.entities:

            if item.field == field_name:

                return item.value

        return None

    def get_item(
        self,
        field_name: str
    ) -> ClassificationItem | None:

        for item in self.entities:

            if item.field == field_name:

                return item

        return None

    # =====================================================
    # Confidence
    # =====================================================

    def _recalculate_confidence(
        self
    ) -> None:

        if not self.entities:

            self.confidence = 0.0

            return

        total = sum(

            item.confidence

            for item in self.entities

        )

        self.confidence = (

            total /

            len(self.entities)

        )

    # =====================================================
    # Export
    # =====================================================

    def to_dict(
        self
    ) -> dict:

        return {

            "intent": self.intent,

            "found": self.found,

            "confidence": self.confidence,

            "entities": [

                item.to_dict()

                for item

                in self.entities

            ],

            "operators": self.operators,

            "warnings": self.warnings,

            "unknown_tokens": self.unknown_tokens

        }

    # =====================================================
    # Debug
    # =====================================================

    def __len__(
        self
    ) -> int:

        return len(
            self.entities
        )

    def __contains__(
        self,
        field_name: str
    ) -> bool:

        return self.has(
            field_name
        )

    def __repr__(
        self
    ) -> str:

        return (

            "ClassificationResult("

            f"intent='{self.intent}', "

            f"entities={len(self.entities)}, "

            f"confidence={self.confidence:.2f}"

            ")"

        )