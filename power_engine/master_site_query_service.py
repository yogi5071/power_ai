"""Deterministic natural-language query service for master_site.

This service owns intent-to-query translation. It never calls an LLM and only
uses whitelisted fields from metadata.master_site through the repository.
"""

from __future__ import annotations

import re

from classification.normalizer import Normalizer
from metadata.master_site import MASTER_SITE


class MasterSiteQueryService:
    """Translate common Indonesian data questions into safe read-only queries."""

    # ==========================================================
    # RUNTIME FILTERS
    # ==========================================================

    RUNTIME_FILTERS = (
        "kabupaten",
        "kecamatan",
        "cluster",
        "nop",
        "kategori_umur",
        "status_warranty",
        "kategori_rectifier",
    )

    # ==========================================================
    # FILTER CUES
    # ==========================================================

    FILTER_CUES = {
        "kabupaten": (
            "kabupaten",
        ),
        "kecamatan": (
            "kecamatan",
        ),
        "cluster": (
            "cluster",
        ),
        "nop": (
            "nop",
        ),
        "kategori_umur": (
            "kategori umur",
            "umur",
            "tua",
        ),
        "status_warranty": (
            "warranty",
            "garansi",
        ),
        "kategori_rectifier": (
            "kategori rectifier",
            "rectifier",
        ),
    }

    # ==========================================================
    # FIELD WORDS
    # ==========================================================

    FIELD_WORDS = {
        "site_id": (
            "site id",
            "site",
        ),
        "jenis_battery": (
            "jenis battery",
            "jenis baterai",
            "battery",
            "baterai",
        ),
        "total_vrla": (
            "total vrla",
            "jumlah vrla",
            "battery vrla",
            "baterai vrla",
        ),
        "total_lithium": (
            "total lithium",
            "jumlah lithium",
            "battery lithium",
            "baterai lithium",
        ),
        "total_bank": (
            "total bank",
            "jumlah bank",
        ),
        "umur_battery": (
            "umur battery",
            "umur baterai",
        ),
        "jumlah_rectifier": (
            "jumlah rectifier",
            "total rectifier",
        ),
        "jumlah_modul": (
            "jumlah modul",
            "total modul",
        ),
        "target_availability": (
            "target availability",
            "availability",
        ),
        "jumlah_rectifier_obsolete": (
            "rectifier obsolete",
            "jumlah obsolete",
        ),
    }

    # ==========================================================
    # FIELD LABELS
    # ==========================================================

    FIELD_LABELS = {
        "site_id": "site",
        "jenis_battery": "jenis battery",
        "total_vrla": "unit VRLA",
        "total_lithium": "unit Lithium",
        "total_bank": "bank battery",
        "umur_battery": "umur battery",
        "jumlah_rectifier": "rectifier",
        "jumlah_modul": "modul",
        "target_availability": "target availability",
        "jumlah_rectifier_obsolete": "rectifier obsolete",
    }

    # ==========================================================
    # INIT
    # ==========================================================

    def __init__(self, repository):
        self.repository = repository

    # ==========================================================
    # EXECUTE
    # ==========================================================

    def execute(self, question: str):
        """
        Return a factual response string, or None when this is not
        a data query.
        """

        text = Normalizer.normalize(question)

        # ------------------------------------------------------
        # RECTIFIER SPECIAL CASE
        #
        # Rectifier condition / summary membutuhkan aggregate
        # khusus agar dapat membedakan:
        #
        # 1. Site classification
        #    kategori_rectifier
        #
        # 2. Unit composition
        #    jumlah_rectifier
        #    jumlah_rectifier_non_obsolete
        #    jumlah_rectifier_obsolete
        #
        # ------------------------------------------------------

        if self._is_rectifier_question(text):

            rectifier_response = self._execute_rectifier(
                text
            )

            if rectifier_response is not None:
                return rectifier_response

        operation = self._operation(text)
        metric = self._metric(
            text,
            operation
        )

        if operation is None:
            return None

        group_by = self._group_by(text)

        filters = [
            item
            for item in self._filters(text)
            if item[0] != group_by
        ]

        if self._requires_location_value(
            text,
            filters
        ):
            return (
                "Sebutkan nilai filternya, misalnya: "
                "Kabupaten Sidoarjo atau Cluster ABC."
            )

        if operation == "list":

            rows = self.repository.list_sites(
                filters,
                self._limit(text)
            )

            return self._format_list(
                rows,
                filters
            )

        rows = self.repository.query_aggregate(
            operation=operation,
            metric_field=metric,
            filters=filters,
            group_by=group_by,
            limit=self._limit(text),
        )

        return self._format_aggregate(
            operation,
            metric,
            rows,
            filters,
            group_by
        )

    # ==========================================================
    # RECTIFIER QUESTION DETECTION
    # ==========================================================

    @staticmethod
    def _is_rectifier_question(text):
        """
        Detect questions specifically related to Rectifier.

        Examples:
        - bagaimana kondisi rectifier jawa timur
        - kondisi rectifier sidoarjo
        - berapa rectifier obsolete
        - berapa site rectifier obsolete
        - berapa rectifier di jawa timur
        """

        return "rectifier" in text

    # ==========================================================
    # RECTIFIER EXECUTION
    # ==========================================================

    def _execute_rectifier(self, text):
        """
        Execute deterministic Rectifier query.

        This method is intentionally handled separately from the
        generic aggregate engine because Rectifier has two levels:

        SITE LEVEL
            kategori_rectifier

        UNIT LEVEL
            jumlah_rectifier
            jumlah_rectifier_non_obsolete
            jumlah_rectifier_obsolete
        """

        scope_field, scope_value = (
            self._rectifier_scope(text)
        )

        # ------------------------------------------------------
        # LIST OBSOLETE SITE
        # ------------------------------------------------------

        if self._is_rectifier_list_question(text):

            rows = self.repository.get_rectifier_obsolete(
                scope_field=scope_field,
                scope_value=scope_value,
            )

            return self._format_rectifier_obsolete_list(
                rows,
                scope_field,
                scope_value,
            )

        # ------------------------------------------------------
        # STATISTICS
        # ------------------------------------------------------

        statistics = self.repository.get_rectifier_statistics(
            scope_field=scope_field,
            scope_value=scope_value,
        )

        # ------------------------------------------------------
        # EXPLICIT UNIT METRIC
        # ------------------------------------------------------

        if self._is_rectifier_non_obsolete_unit_question(text):

            value = statistics.get(
                "total_non_obsolete",
                0
            )

            return (
                f"Jumlah rectifier non-obsolete"
                f"{self._rectifier_scope_text(scope_field, scope_value)}"
                f": {self._number(value)} unit"
            )

        if self._is_rectifier_obsolete_unit_question(text):

            value = statistics.get(
                "total_obsolete",
                0
            )

            return (
                f"Jumlah rectifier obsolete"
                f"{self._rectifier_scope_text(scope_field, scope_value)}"
                f": {self._number(value)} unit"
            )

        if self._is_rectifier_total_unit_question(text):

            value = statistics.get(
                "total_rectifier",
                0
            )

            return (
                f"Jumlah seluruh rectifier"
                f"{self._rectifier_scope_text(scope_field, scope_value)}"
                f": {self._number(value)} unit"
            )

        # ------------------------------------------------------
        # EXPLICIT SITE METRIC
        # ------------------------------------------------------

        if self._is_rectifier_obsolete_site_question(text):

            value = statistics.get(
                "obsolete_site",
                0
            )

            return (
                f"Jumlah site rectifier obsolete"
                f"{self._rectifier_scope_text(scope_field, scope_value)}"
                f": {self._number(value)} site"
            )

        if self._is_rectifier_non_obsolete_site_question(text):

            value = statistics.get(
                "non_obsolete_site",
                0
            )

            return (
                f"Jumlah site rectifier non-obsolete"
                f"{self._rectifier_scope_text(scope_field, scope_value)}"
                f": {self._number(value)} site"
            )

        # ------------------------------------------------------
        # GENERAL CONDITION / SUMMARY
        # ------------------------------------------------------

        if self._is_rectifier_condition_question(text):

            return self._format_rectifier_summary(
                statistics,
                scope_field,
                scope_value,
            )

        # ------------------------------------------------------
        # Generic "berapa rectifier"
        # ------------------------------------------------------

        if any(
            phrase in text
            for phrase in (
                "berapa rectifier",
                "jumlah rectifier",
                "total rectifier",
            )
        ):

            value = statistics.get(
                "total_rectifier",
                0
            )

            return (
                f"Jumlah rectifier"
                f"{self._rectifier_scope_text(scope_field, scope_value)}"
                f": {self._number(value)} unit"
            )

        return None

    # ==========================================================
    # RECTIFIER SCOPE
    # ==========================================================

    def _rectifier_scope(self, text):
        """
        Resolve Rectifier scope.

        Province / Jatim:
            seluruh master_site

        Site:
            siteid

        Kabupaten:
            kabupaten

        Kecamatan:
            kecamatan

        NOP:
            nop_name

        Cluster:
            cluster
        """

        # ------------------------------------------------------
        # SITE ID
        # ------------------------------------------------------

        site_match = re.search(
            r"\b[a-z]{3}\d{3}\b",
            text
        )

        if site_match:

            return (
                "siteid",
                site_match.group().upper()
            )

        # ------------------------------------------------------
        # PROVINCE
        #
        # master_site = dataset Jawa Timur
        # ------------------------------------------------------

        if any(
            phrase in text
            for phrase in (
                "jawa timur",
                "jatim",
                "provinsi jawa timur",
                "provinsi jatim",
                "keseluruhan",
                "seluruh jatim",
                "seluruh jawa timur",
            )
        ):

            return (
                "province",
                "Jawa Timur"
            )

        # ------------------------------------------------------
        # KABUPATEN
        # ------------------------------------------------------

        kabupaten = self._extract_distinct_scope_value(
            "kabupaten",
            text
        )

        if kabupaten is not None:

            return (
                "kabupaten",
                kabupaten
            )

        # ------------------------------------------------------
        # KECAMATAN
        # ------------------------------------------------------

        kecamatan = self._extract_distinct_scope_value(
            "kecamatan",
            text
        )

        if kecamatan is not None:

            return (
                "kecamatan",
                kecamatan
            )

        # ------------------------------------------------------
        # NOP
        # ------------------------------------------------------

        nop = self._extract_distinct_scope_value(
            "nop",
            text
        )

        if nop is not None:

            return (
                "nop_name",
                nop
            )

        # ------------------------------------------------------
        # CLUSTER
        # ------------------------------------------------------

        cluster = self._extract_distinct_scope_value(
            "cluster",
            text
        )

        if cluster is not None:

            return (
                "cluster",
                cluster
            )

        # ------------------------------------------------------
        # DEFAULT
        #
        # Dataset = Jawa Timur
        # ------------------------------------------------------

        return (
            "province",
            "Jawa Timur"
        )

    # ==========================================================
    # EXTRACT DISTINCT SCOPE VALUE
    # ==========================================================

    def _extract_distinct_scope_value(
        self,
        field_name,
        text
    ):
        """
        Find an actual database value inside the question.
        """

        try:

            values = self.repository.get_distinct_values(
                field_name
            )

        except Exception:
            return None

        normalized_values = sorted(
            (
                (
                    Normalizer.normalize(
                        str(value)
                    ),
                    value
                )
                for value in values
                if value is not None
            ),
            key=lambda item: len(item[0]),
            reverse=True,
        )

        for normalized_value, value in normalized_values:

            if (
                normalized_value
                and self._contains_phrase(
                    text,
                    normalized_value
                )
            ):

                return value

        return None

    # ==========================================================
    # RECTIFIER QUESTION TYPES
    # ==========================================================

    @staticmethod
    def _is_rectifier_condition_question(text):

        return any(
            phrase in text
            for phrase in (
                "kondisi rectifier",
                "bagaimana kondisi rectifier",
                "status rectifier",
                "kondisi perangkat rectifier",
            )
        )

    @staticmethod
    def _is_rectifier_list_question(text):

        return any(
            phrase in text
            for phrase in (
                "site mana",
                "site mana saja",
                "daftar site",
                "tampilkan site",
                "list site",
            )
        ) and "obsolete" in text and not (
            "non obsolete" in text
            or "non-obsolete" in text
            or "nonobsolete" in text
        )

    @staticmethod
    def _is_rectifier_obsolete_unit_question(text):

        # "non obsolete" contains the word "obsolete".
        # Always exclude it before detecting obsolete.
        if (
            "non obsolete" in text
            or "non-obsolete" in text
            or "nonobsolete" in text
        ):
            return False

        if "obsolete" not in text:
            return False

        return any(
            phrase in text
            for phrase in (
                "berapa rectifier",
                "jumlah rectifier",
                "total rectifier",
                "jumlah obsolete",
                "total obsolete",
            )
        ) and not any(
            phrase in text
            for phrase in (
                "site",
                "situs",
            )
        )

    @staticmethod
    def _is_rectifier_non_obsolete_unit_question(text):

        return (
            (
                "non obsolete" in text
                or "non-obsolete" in text
                or "nonobsolete" in text
            )
            and "rectifier" in text
            and not any(
                phrase in text
                for phrase in (
                    "site",
                    "situs",
                )
            )
        )

    @staticmethod
    def _is_rectifier_total_unit_question(text):

        return any(
            phrase in text
            for phrase in (
                "jumlah seluruh rectifier",
                "total seluruh rectifier",
                "total rectifier",
                "jumlah rectifier",
            )
        ) and "obsolete" not in text

    @staticmethod
    def _is_rectifier_obsolete_site_question(text):

        # "non obsolete" must never be classified as obsolete.
        if (
            "non obsolete" in text
            or "non-obsolete" in text
            or "nonobsolete" in text
        ):
            return False

        return (
            "obsolete" in text
            and any(
                phrase in text
                for phrase in (
                    "berapa site",
                    "jumlah site",
                    "total site",
                    "site obsolete",
                    "site yang obsolete",
                )
            )
        )

    @staticmethod
    def _is_rectifier_non_obsolete_site_question(text):

        return (
            (
                "non obsolete" in text
                or "non-obsolete" in text
                or "nonobsolete" in text
            )
            and any(
                phrase in text
                for phrase in (
                    "berapa site",
                    "jumlah site",
                    "total site",
                    "site",
                )
            )
        )

    # ==========================================================
    # RECTIFIER SCOPE TEXT
    # ==========================================================

    @staticmethod
    def _rectifier_scope_text(
        scope_field,
        scope_value
    ):

        if not scope_field:
            return ""

        labels = {
            "province": " Provinsi",
            "kabupaten": " Kabupaten",
            "kecamatan": " Kecamatan",
            "siteid": " Site",
            "nop_name": " NOP",
            "cluster": " Cluster",
        }

        label = labels.get(
            scope_field,
            ""
        )

        if scope_value is None:
            return ""

        return (
            f" untuk{label} "
            f"{scope_value}"
        )

    # ==========================================================
    # RECTIFIER SUMMARY FORMAT
    # ==========================================================

    def _format_rectifier_summary(
        self,
        statistics,
        scope_field,
        scope_value
    ):

        total_site = int(
            statistics.get(
                "total_site",
                0
            ) or 0
        )

        obsolete_site = int(
            statistics.get(
                "obsolete_site",
                0
            ) or 0
        )

        non_obsolete_site = int(
            statistics.get(
                "non_obsolete_site",
                0
            ) or 0
        )

        total_rectifier = int(
            statistics.get(
                "total_rectifier",
                0
            ) or 0
        )

        total_non_obsolete = int(
            statistics.get(
                "total_non_obsolete",
                0
            ) or 0
        )

        total_obsolete = int(
            statistics.get(
                "total_obsolete",
                0
            ) or 0
        )

        obsolete_site_percentage = (
            (
                obsolete_site
                / total_site
            ) * 100
            if total_site
            else 0
        )

        obsolete_unit_percentage = (
            (
                total_obsolete
                / total_rectifier
            ) * 100
            if total_rectifier
            else 0
        )

        scope_text = (
            self._rectifier_scope_text(
                scope_field,
                scope_value
            )
            .replace(
                " untuk",
                ""
            )
        )

        return (
            "Rectifier Summary\n\n"
            f"Scope :{scope_text}\n\n"

            "Site\n"
            f"- Total Site       : "
            f"{self._number(total_site)}\n"
            f"- Non Obsolete     : "
            f"{self._number(non_obsolete_site)} site\n"
            f"- Obsolete         : "
            f"{self._number(obsolete_site)} site\n"
            f"- Obsolete Site Rate: "
            f"{obsolete_site_percentage:.2f}%\n\n"

            "Unit Rectifier\n"
            f"- Total Rectifier  : "
            f"{self._number(total_rectifier)} unit\n"
            f"- Non Obsolete     : "
            f"{self._number(total_non_obsolete)} unit\n"
            f"- Obsolete         : "
            f"{self._number(total_obsolete)} unit\n"
            f"- Obsolete Unit Rate: "
            f"{obsolete_unit_percentage:.2f}%"
        )

    # ==========================================================
    # RECTIFIER OBSOLETE LIST
    # ==========================================================

    def _format_rectifier_obsolete_list(
        self,
        rows,
        scope_field,
        scope_value
    ):

        scope_text = self._rectifier_scope_text(
            scope_field,
            scope_value
        )

        if not rows:

            return (
                "Tidak ada site dengan rectifier obsolete"
                f"{scope_text}."
            )

        lines = []

        for row in rows:

            lines.append(
                f"- {row['siteid']} | "
                f"{row['site_name']} | "
                f"{row.get('kabupaten') or '-'} | "
                f"{row.get('kecamatan') or '-'} | "
                f"Obsolete: "
                f"{self._number(row.get('jumlah_rectifier_obsolete'))} unit"
            )

        return (
            "Daftar site dengan rectifier obsolete"
            f"{scope_text} "
            f"({len(rows)} data):\n"
            + "\n".join(lines)
        )

    # ==========================================================
    # GENERIC OPERATION
    # ==========================================================

    def _operation(self, text):

        if any(
            word in text
            for word in (
                "tampilkan",
                "daftar",
                "list",
                "site mana",
            )
        ):

            return "list"

        if any(
            word in text
            for word in (
                "rata rata",
                "rerata",
                "average",
            )
        ):

            return "average"

        if any(
            word in text
            for word in (
                "total",
                "jumlah seluruh",
                "berapa unit",
                "berapa bank",
            )
        ):

            return "sum"

        if any(
            word in text
            for word in (
                "berapa",
                "jumlah",
                "count",
                "banyak",
            )
        ):

            return "count"

        return None

    # ==========================================================
    # GENERIC METRIC
    # ==========================================================

    def _metric(
        self,
        text,
        operation
    ):

        if operation == "count":
            return None

        # Match explicit numeric metrics before broad terms
        # such as "battery".

        metric_fields = (
            "total_vrla",
            "total_lithium",
            "total_bank",
            "umur_battery",
            "jumlah_rectifier_obsolete",
            "jumlah_rectifier",
            "jumlah_modul",
            "target_availability",
        )

        for field_name in metric_fields:

            phrases = self.FIELD_WORDS[
                field_name
            ]

            if any(
                phrase in text
                for phrase in phrases
            ):

                return field_name

        # A bare "total battery" is ambiguous;
        # count sites is safer than inventing units.

        return None

    # ==========================================================
    # GENERIC FILTERS
    # ==========================================================

    def _filters(self, text):

        matches = []

        battery_value = (
            MASTER_SITE.find_value_alias(
                "jenis_battery",
                self._battery_word(text)
            )
        )

        if battery_value in {
            "VRLA",
            "Lithium",
        }:

            matches.append(
                (
                    "jenis_battery",
                    battery_value
                )
            )

        for field_name in self.RUNTIME_FILTERS:

            # --------------------------------------------------
            # Rectifier obsolete is handled by dedicated logic.
            # Do not turn it into kategori_rectifier filter here.
            # --------------------------------------------------

            if (
                field_name == "kategori_rectifier"
                and "rectifier obsolete" in text
            ):

                continue

            if not self._field_is_requested(
                field_name,
                text
            ):

                continue

            values = (
                self.repository.get_distinct_values(
                    field_name
                )
            )

            normalized_values = sorted(
                (
                    (
                        Normalizer.normalize(
                            str(value)
                        ),
                        value
                    )
                    for value in values
                ),
                key=lambda item: len(
                    item[0]
                ),
                reverse=True,
            )

            for normalized_value, value in normalized_values:

                if (
                    normalized_value
                    and self._contains_phrase(
                        text,
                        normalized_value
                    )
                ):

                    matches.append(
                        (
                            field_name,
                            value
                        )
                    )

                    break

        site_match = re.search(
            r"\b[a-z]{3}\d{3}\b",
            text
        )

        if site_match:

            matches.append(
                (
                    "site_id",
                    site_match.group().upper()
                )
            )

        return matches

    # ==========================================================
    # FIELD REQUEST
    # ==========================================================

    def _field_is_requested(
        self,
        field_name,
        text
    ):

        return any(
            cue in text
            for cue in self.FILTER_CUES[
                field_name
            ]
        )

    # ==========================================================
    # BATTERY WORD
    # ==========================================================

    @staticmethod
    def _battery_word(text):

        if any(
            word in text
            for word in (
                "vrla",
                "aki",
                "lead acid",
            )
        ):

            return "vrla"

        if any(
            word in text
            for word in (
                "lithium",
                "li ion",
            )
        ):

            return "lithium"

        return ""

    # ==========================================================
    # CONTAINS PHRASE
    # ==========================================================

    @staticmethod
    def _contains_phrase(
        text,
        phrase
    ):

        return (
            re.search(
                rf"(?<!\w)"
                rf"{re.escape(phrase)}"
                rf"(?!\w)",
                text
            )
            is not None
        )

    # ==========================================================
    # LIMIT
    # ==========================================================

    @staticmethod
    def _limit(text):

        match = re.search(
            r"\b(\d{1,3})\s+(?:site|data)\b",
            text
        )

        return (
            int(match.group(1))
            if match
            else 10
        )

    # ==========================================================
    # GROUP BY
    # ==========================================================

    @staticmethod
    def _group_by(text):

        for field_name in (
            "kabupaten",
            "kecamatan",
            "cluster",
            "nop",
            "jenis_battery",
        ):

            phrases = (
                f"per {field_name}",
                f"per {field_name.replace('_', ' ')}",
            )

            if any(
                phrase in text
                for phrase in phrases
            ):

                return field_name

        return None

    # ==========================================================
    # LOCATION VALUE REQUIRED
    # ==========================================================

    @staticmethod
    def _requires_location_value(
        text,
        filters
    ):

        requested = any(
            word in text
            for word in (
                "kabupaten",
                "kecamatan",
                "cluster",
                "nop",
            )
        )

        has_value = any(
            field in {
                "kabupaten",
                "kecamatan",
                "cluster",
                "nop",
            }
            for field, _ in filters
        )

        return (
            requested
            and not has_value
            and "per " not in text
        )

    # ==========================================================
    # GENERIC AGGREGATE FORMAT
    # ==========================================================

    def _format_aggregate(
        self,
        operation,
        metric,
        rows,
        filters,
        group_by
    ):

        metric_label = self.FIELD_LABELS.get(
            metric,
            "site"
        )

        filter_text = self._filter_text(
            filters
        )

        if group_by:

            group_label = (
                MASTER_SITE.get(
                    group_by
                ).label
            )

            lines = [
                f"{row['group_value'] or '-'}: "
                f"{self._number(row['value'])}"
                for row in rows
            ]

            return (
                f"{operation.title()} "
                f"{metric_label} "
                f"per {group_label}"
                f"{filter_text}:\n"
                + "\n".join(lines)
            )

        value = (
            rows[0]["value"]
            if rows
            else 0
        )

        verb = {
            "count": "Jumlah",
            "sum": "Total",
            "average": "Rata-rata",
        }[
            operation
        ]

        return (
            f"{verb} "
            f"{metric_label}"
            f"{filter_text}: "
            f"{self._number(value)}"
        )

    # ==========================================================
    # GENERIC LIST FORMAT
    # ==========================================================

    def _format_list(
        self,
        rows,
        filters
    ):

        if not rows:

            return (
                f"Tidak ada site yang sesuai"
                f"{self._filter_text(filters)}."
            )

        lines = []

        for row in rows:

            lines.append(
                f"- {row['siteid']} | "
                f"{row['site_name']} | "
                f"{row['kabupaten'] or '-'} | "
                f"{row['cluster'] or '-'} | "
                f"{row['battery'] or '-'}"
            )

        return (
            f"Daftar site"
            f"{self._filter_text(filters)} "
            f"({len(rows)} data):\n"
            + "\n".join(lines)
        )

    # ==========================================================
    # NUMBER FORMAT
    # ==========================================================

    @staticmethod
    def _number(value):

        if value is None:
            return "0"

        if isinstance(
            value,
            float
        ):

            return (
                f"{value:,.2f}"
                .replace(",", "_")
                .replace(".", ",")
                .replace("_", ".")
            )

        try:

            return f"{value:,}".replace(
                ",",
                "."
            )

        except (
            TypeError,
            ValueError,
        ):

            return str(value)

    # ==========================================================
    # FILTER TEXT
    # ==========================================================

    def _filter_text(
        self,
        filters
    ):

        if not filters:
            return ""

        labels = [
            (
                f"{MASTER_SITE.get(field).label} "
                f"{value}"
            )
            for field, value in filters
        ]

        return (
            " untuk "
            + ", ".join(labels)
        )