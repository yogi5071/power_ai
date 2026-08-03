"""
classification/matcher/matcher.py

Metadata Driven Matcher

Pipeline

Question
    │
Normalizer
    │
Tokenizer
    │
Matcher
    │
ClassificationResult

Matcher hanya bertugas melakukan
proses pencocokan metadata.

Tidak melakukan:

- SQL
- Planner
- Validator
- Intent Detection
"""

from __future__ import annotations

from collections import defaultdict

from classification.classification_item import ClassificationItem
from classification.classification_result import ClassificationResult

from metadata.context import MetadataContext


class Matcher:

    """
    Metadata matcher.

    Priority

    Runtime
        ↓

    Enum
        ↓

    Alias
        ↓

    Exact

    Runtime mempunyai prioritas
    tertinggi karena berasal dari
    database aktual.
    """

    # ---------------------------------------------

    RUNTIME_CONFIDENCE = 1.00

    ENUM_CONFIDENCE = 0.98

    ALIAS_CONFIDENCE = 0.95

    EXACT_CONFIDENCE = 0.92

    # ---------------------------------------------

    def __init__(
        self,
        context: MetadataContext
    ) -> None:

        self.context = context

    # ==========================================================
    # PUBLIC
    # ==========================================================

    def match(
        self,
        tokens: list[str]
    ) -> ClassificationResult:

        result = ClassificationResult()

        if not tokens:

            return result

        candidates = self._build_candidates(tokens)

        consumed: set[str] = set()

        self._match_runtime(
            candidates,
            consumed,
            result
        )

        self._match_enum(
            candidates,
            consumed,
            result
        )

        self._match_alias(
            candidates,
            consumed,
            result
        )

        self._match_exact(
            candidates,
            consumed,
            result
        )

        self._collect_unknown(
            tokens,
            consumed,
            result
        )

        return result

    # ==========================================================
    # NGRAM
    # ==========================================================

    def _build_candidates(
        self,
        tokens: list[str]
    ) -> list[str]:

        """
        Build ngram.

        Example

        battery
        lead
        acid
        sidoarjo

        →

        battery lead acid

        lead acid

        battery lead

        acid sidoarjo

        battery

        lead

        acid

        sidoarjo
        """

        candidates: list[str] = []

        total = len(tokens)

        for size in (3, 2, 1):

            if total < size:

                continue

            for start in range(

                total - size + 1

            ):

                phrase = " ".join(

                    tokens[start:start + size]

                ).strip()

                if phrase:

                    candidates.append(

                        phrase

                    )

        return candidates

    # ==========================================================
    # DUPLICATE
    # ==========================================================

    def _exists(
        self,
        result: ClassificationResult,
        field: str,
        value
    ) -> bool:

        for entity in result.entities:

            if (

                entity.field == field

                and

                entity.value == value

            ):

                return True

        return False

    # ==========================================================
    # ADD RESULT
    # ==========================================================

    def _add(

        self,

        result: ClassificationResult,

        field: str,

        value,

        source: str,

        confidence: float

    ) -> None:

        if self._exists(

            result,

            field,

            value

        ):

            return

        result.add(

            ClassificationItem(

                field=field,

                value=value,

                source=source,

                confidence=confidence

            )

        )
    # ==========================================================
    # ENUM MATCHER
    # ==========================================================

    def _match_enum(
        self,
        candidates: list[str],
        consumed: set[str],
        result: ClassificationResult
    ) -> None:

        """
        Enum Matcher.

        Match terhadap values yang sudah
        didefinisikan pada metadata.

        Contoh

        values =

        [
            "VRLA",
            "Lithium"
        ]
        """

        for field in self.context.fields():

            if not field.values:

                continue

            # ------------------------------------------
            # Build lookup
            # ------------------------------------------

            lookup: dict[str, object] = {}

            for value in field.values:

                if value is None:

                    continue

                text = str(value).strip()

                if not text:

                    continue

                lookup[text.lower()] = value

            # ------------------------------------------
            # Matching
            # ------------------------------------------

            for candidate in candidates:

                key = candidate.lower()

                if key not in lookup:

                    continue

                normalized_value = lookup[key]

                if self._exists(

                    result,

                    field.name,

                    normalized_value

                ):

                    consumed.add(candidate)

                    continue

                self._add(

                    result=result,

                    field=field.name,

                    value=normalized_value,

                    source="enum",

                    confidence=self.ENUM_CONFIDENCE

                )

                consumed.add(candidate)

    # ==========================================================
    # END ENUM
    # ==========================================================
        # ==========================================================
    # ENUM MATCHER
    # ==========================================================

    def _match_enum(
        self,
        candidates: list[str],
        consumed: set[str],
        result: ClassificationResult
    ) -> None:

        """
        Enum Matcher.

        Match terhadap values yang sudah
        didefinisikan pada metadata.

        Contoh

        values =

        [
            "VRLA",
            "Lithium"
        ]
        """

        for field in self.context.fields():

            if not field.values:

                continue

            # ------------------------------------------
            # Build lookup
            # ------------------------------------------

            lookup: dict[str, object] = {}

            for value in field.values:

                if value is None:

                    continue

                text = str(value).strip()

                if not text:

                    continue

                lookup[text.lower()] = value

            # ------------------------------------------
            # Matching
            # ------------------------------------------

            for candidate in candidates:

                key = candidate.lower()

                if key not in lookup:

                    continue

                normalized_value = lookup[key]

                if self._exists(

                    result,

                    field.name,

                    normalized_value

                ):

                    consumed.add(candidate)

                    continue

                self._add(

                    result=result,

                    field=field.name,

                    value=normalized_value,

                    source="enum",

                    confidence=self.ENUM_CONFIDENCE

                )

                consumed.add(candidate)

    # ==========================================================
    # END ENUM
    # ==========================================================
    # ==========================================================
    # ENUM MATCHER
    # ==========================================================

    def _match_enum(
        self,
        candidates: list[str],
        consumed: set[str],
        result: ClassificationResult
    ) -> None:

        """
        Enum Matcher.

        Match terhadap values yang sudah
        didefinisikan pada metadata.

        Contoh

        values =

        [
            "VRLA",
            "Lithium"
        ]
        """

        for field in self.context.fields():

            if not field.values:

                continue

            # ------------------------------------------
            # Build lookup
            # ------------------------------------------

            lookup: dict[str, object] = {}

            for value in field.values:

                if value is None:

                    continue

                text = str(value).strip()

                if not text:

                    continue

                lookup[text.lower()] = value

            # ------------------------------------------
            # Matching
            # ------------------------------------------

            for candidate in candidates:

                key = candidate.lower()

                if key not in lookup:

                    continue

                normalized_value = lookup[key]

                if self._exists(

                    result,

                    field.name,

                    normalized_value

                ):

                    consumed.add(candidate)

                    continue

                self._add(

                    result=result,

                    field=field.name,

                    value=normalized_value,

                    source="enum",

                    confidence=self.ENUM_CONFIDENCE

                )

                consumed.add(candidate)

    # ==========================================================
    # END ENUM
    # ==========================================================
    # ==========================================================
    # NORMALIZER
    # ==========================================================

    def _normalize_text(
        self,
        value
    ) -> str:

        """
        Internal text normalizer.

        Semua proses matching HARUS
        menggunakan helper ini.
        """

        if value is None:

            return ""

        text = str(value).lower()

        for ch in (

            "-",
            "_",
            "/",
            ".",
            ","

        ):

            text = text.replace(ch, " ")

        return " ".join(
            text.split()
        )

    # ==========================================================
    # EXACT MATCHER
    # ==========================================================

    def _match_exact(
        self,
        candidates: list[str],
        consumed: set[str],
        result: ClassificationResult
    ) -> None:

        """
        Exact Match.

        Field name

        contoh

        kabupaten

        cluster

        nop

        site_id

        Digunakan apabila user
        menyebut nama field secara
        langsung.
        """

        for field in self.context.fields():

            normalized_field = self._normalize_text(

                field.name

            )

            normalized_label = self._normalize_text(

                field.label

            )

            for candidate in candidates:

                normalized_candidate = self._normalize_text(

                    candidate

                )

                if (

                    normalized_candidate

                    != normalized_field

                    and

                    normalized_candidate

                    != normalized_label

                ):

                    continue

                if self._exists(

                    result,

                    "__field__",

                    field.name

                ):

                    consumed.add(candidate)

                    continue

                self._add(

                    result=result,

                    field="__field__",

                    value=field.name,

                    source="exact",

                    confidence=self.EXACT_CONFIDENCE

                )

                consumed.add(candidate)

    # ==========================================================
    # UNKNOWN TOKEN
    # ==========================================================

    def _collect_unknown(
        self,
        tokens: list[str],
        consumed: set[str],
        result: ClassificationResult
    ) -> None:

        """
        Token yang belum pernah
        berhasil di-match.
        """

        consumed_token = set()

        for phrase in consumed:

            for token in phrase.split():

                consumed_token.add(

                    self._normalize_text(

                        token

                    )

                )

        for token in tokens:

            normalized = self._normalize_text(

                token

            )

            if not normalized:

                continue

            if normalized in consumed_token:

                continue

            result.add_unknown(

                token

            )
    # ==========================================================
    # EXPORT
    # ==========================================================

    def to_dict(
        self,
        result: ClassificationResult
    ) -> dict:

        return result.to_dict()

    # ==========================================================
    # DEBUG
    # ==========================================================

    def summary(
        self,
        result: ClassificationResult
    ) -> str:

        lines = []

        lines.append(
            f"Intent      : {result.intent}"
        )

        lines.append(
            f"Confidence  : {result.confidence:.2f}"
        )

        lines.append(
            f"Entities    : {len(result.entities)}"
        )

        if result.entities:

            lines.append("")

            for entity in result.entities:

                lines.append(

                    f"- {entity.field}"

                    f" = {entity.value}"

                    f" ({entity.source})"

                )

        if result.unknown_tokens:

            lines.append("")

            lines.append(

                "Unknown : "

                +

                ", ".join(

                    result.unknown_tokens

                )

            )

        return "\n".join(lines)

    # ==========================================================
    # CALL
    # ==========================================================

    def __call__(
        self,
        tokens: list[str]
    ) -> ClassificationResult:

        return self.match(
            tokens
        )

    # ==========================================================
    # REPR
    # ==========================================================

    def __repr__(
        self
    ) -> str:

        return (

            "Matcher("

            f"table='{self.context.table.table_name}'"

            ")"

        )    