"""
Entity Extractor

Power AI Copilot
"""

import re
from difflib import get_close_matches

from models.entity import Entity


class EntityExtractor:

    # ==========================================================
    # SITE
    # ==========================================================

    SITE_PATTERN = r"\b[A-Z]{3}\d{3}\b"

    # ==========================================================
    # SCOPE PATTERNS
    # ==========================================================

    KABUPATEN_PATTERN = (
        r"\bKABUPATEN\s+(.+?)"
        r"(?=\s*(?:\?|,|\.|$|"
        r"\b(?:\d{1,2})\s+bulan))"
    )

    KECAMATAN_PATTERN = (
        r"\bKECAMATAN\s+(.+?)"
        r"(?=\s*(?:\?|,|\.|$|"
        r"\b(?:\d{1,2})\s+bulan))"
    )

    NOP_PATTERN = (
        r"\bNOP\s+(.+?)"
        r"(?=\s*(?:\?|,|\.|$|"
        r"\b(?:\d{1,2})\s+bulan|"
        r"\b(?:PADA\s+)?BULAN\b))"
    )

    CLUSTER_PATTERN = (
        r"\bCLUSTER\s+(.+?)"
        r"(?=\s*(?:\?|,|\.|$|"
        r"\b(?:\d{1,2})\s+bulan))"
    )

    # ==========================================================
    # PROVINCE
    #
    # Dataset Power AI saat ini mencakup Jawa Timur.
    #
    # Semua alias berikut dipetakan menjadi:
    #
    # scope_type  = province
    # scope_value = Jawa Timur
    # ==========================================================

    PROVINCE_ALIASES = (
        "PROVINSI JAWA TIMUR",
        "PROVINSI JATIM",
        "JAWA TIMUR",
        "JATIM",
    )

    # ==========================================================
    # CITIES
    # ==========================================================

    CITIES = [
        "SURABAYA",
        "SIDOARJO",
        "MALANG",
        "GRESIK",
        "PASURUAN",
        "MOJOKERTO",
        "JEMBER",
        "MADIUN",
        "KEDIRI",
        "BLITAR",
        "PROBOLINGGO",
    ]

    # ==========================================================
    # TECHNOLOGIES
    # ==========================================================

    TECHNOLOGIES = [
        "VRLA",
        "LITHIUM",
    ]

    # ==========================================================
    # VENDORS
    # ==========================================================

    VENDORS = [
        "HUAWEI",
        "ZTE",
        "ERICSSON",
        "NOKIA",
    ]

    # ==========================================================
    # BATTERY STATUS
    # ==========================================================

    BATTERY_STATUS = [
        "OUT OF WARRANTY",
        "OLD",
        "CRITICAL",
        "WARNING",
        "HEALTHY",
    ]

    # ==========================================================
    # ALARMS
    # ==========================================================

    ALARMS = [
        "MAINS FAIL",
        "LOW VOLTAGE",
        "RECTIFIER FAIL",
        "GENSET RUNNING",
        "HIGH TEMPERATURE",
        "BATTERY DISCONNECT",
    ]

    # ==========================================================
    # MAIN EXTRACT
    # ==========================================================

    @classmethod
    def extract(cls, message: str) -> Entity:

        entity = Entity()

        text = (
            message or ""
        ).upper()

        # ======================================================
        # ENTITY EXTRACTION
        # ======================================================

        cls._extract_site(
            text,
            entity
        )

        cls._extract_city(
            text,
            entity
        )

        cls._extract_vendor(
            text,
            entity
        )

        cls._extract_technology(
            text,
            entity
        )

        cls._extract_battery_status(
            text,
            entity
        )

        cls._extract_alarm(
            text,
            entity
        )

        # ======================================================
        # SCOPE
        # ======================================================

        (
            entity.scope_type,
            entity.scope_value,
        ) = cls.extract_scope(
            message
        )

        # ======================================================
        # PERIOD
        # ======================================================

        entity.period_months = (
            cls.extract_period_months(
                message
            )
        )

        return entity

    # ==========================================================
    # SITE ID
    # ==========================================================

    @classmethod
    def extract_site_id(
        cls,
        message: str
    ):

        match = re.search(
            cls.SITE_PATTERN,
            (
                message or ""
            ).upper()
        )

        return (
            match.group()
            if match
            else None
        )

    # ==========================================================
    # SCOPE
    # ==========================================================

    @classmethod
    def extract_scope(
        cls,
        message: str
    ):

        text = (
            message or ""
        ).upper().strip()

        # ======================================================
        # 1. SITE
        #
        # Site harus memiliki prioritas tertinggi.
        # ======================================================

        site_id = cls.extract_site_id(
            text
        )

        if site_id:

            return (
                "siteid",
                site_id
            )

        # ======================================================
        # 2. KECAMATAN
        # ======================================================

        match = re.search(
            cls.KECAMATAN_PATTERN,
            text
        )

        if match:

            value = cls._clean_scope_value(
                match.group(1)
            )

            if value:

                return (
                    "kecamatan",
                    value
                )

        # ======================================================
        # 3. KABUPATEN
        # ======================================================

        match = re.search(
            cls.KABUPATEN_PATTERN,
            text
        )

        if match:

            value = cls._clean_scope_value(
                match.group(1)
            )

            if value:

                return (
                    "kabupaten",
                    value
                )

        # ======================================================
        # 4. EXPLICIT PROVINCE
        #
        # Contoh:
        #
        # "provinsi jawa timur"
        # "jawa timur"
        # "jatim"
        # ======================================================

        for alias in sorted(
            cls.PROVINCE_ALIASES,
            key=len,
            reverse=True
        ):

            if alias in text:

                return (
                    "province",
                    "Jawa Timur"
                )

        # ======================================================
        # 5. NOP
        # ======================================================

        match = re.search(
            cls.NOP_PATTERN,
            text
        )

        if match:

            value = cls._clean_scope_value(
                match.group(1)
            )

            if value:

                return (
                    "nop",
                    value
                )

        # ======================================================
        # 6. CLUSTER
        # ======================================================

        match = re.search(
            cls.CLUSTER_PATTERN,
            text
        )

        if match:

            value = cls._clean_scope_value(
                match.group(1)
            )

            if value:

                return (
                    "cluster",
                    value
                )

        # ======================================================
        # 7. "KESELURUHAN"
        #
        # Karena dataset Power AI adalah Jawa Timur,
        # "keseluruhan" berarti seluruh data Jawa Timur.
        #
        # Kita sengaja TIDAK menjadikan "semua" sebagai
        # province karena:
        #
        # "semua site di Kecamatan Waru"
        #
        # harus tetap mengikuti scope Kecamatan Waru.
        # ======================================================

        if cls._is_whole_province_request(
            text
        ):

            return (
                "province",
                "Jawa Timur"
            )

        return (
            None,
            None
        )

    # ==========================================================
    # WHOLE PROVINCE DETECTION
    # ==========================================================

    @staticmethod
    def _is_whole_province_request(
        text: str
    ):

        whole_keywords = (
            "KESELURUHAN",
            "SELURUH SITE",
            "SEMUA SITE",
            "SELURUH WILAYAH",
            "SELURUH JAWA TIMUR",
            "SELURUH JATIM",
            "SEMUA WILAYAH",
            "SEMUA JAWA TIMUR",
            "SEMUA JATIM",
        )

        return any(
            keyword in text
            for keyword in whole_keywords
        )

    # ==========================================================
    # KABUPATEN
    # ==========================================================

    @classmethod
    def extract_kabupaten(
        cls,
        message: str
    ):

        scope, value = cls.extract_scope(
            message
        )

        return (
            value
            if scope == "kabupaten"
            else None
        )

    # ==========================================================
    # KECAMATAN
    # ==========================================================

    @classmethod
    def extract_kecamatan(
        cls,
        message: str
    ):

        scope, value = cls.extract_scope(
            message
        )

        return (
            value
            if scope == "kecamatan"
            else None
        )

    # ==========================================================
    # PERIOD
    # ==========================================================

    @classmethod
    def extract_period_months(
        cls,
        message: str
    ):

        text = (
            message or ""
        ).lower().strip()

        # ======================================================
        # CURRENT MONTH
        # ======================================================

        if (
            "bulan ini" in text
            or "bulan berjalan" in text
            or "bulan sekarang" in text
        ):

            return 1

        # ======================================================
        # N MONTHS
        #
        # Examples:
        #
        # 2 bulan
        # 2 bulan terakhir
        # 3 bulan terakhir
        # 4 bulan kebelakang
        # 4 bulan ke belakang
        # 6 bulan sebelumnya
        # ======================================================

        match = re.search(
            r"\b(\d{1,2})\s+bulan"
            r"(?:\s+"
            r"(?:terakhir|"
            r"kebelakang|"
            r"ke\s+belakang|"
            r"sebelumnya)"
            r")?\b",
            text
        )

        if match:

            months = int(
                match.group(1)
            )

            return max(
                1,
                min(
                    months,
                    12
                )
            )

        # ======================================================
        # ONE YEAR
        # ======================================================

        if (
            "setahun" in text
            or "1 tahun" in text
            or "12 bulan" in text
        ):

            return 12

        # ======================================================
        # DEFAULT
        # ======================================================

        return 1

    # ==========================================================
    # CLEAN SCOPE VALUE
    # ==========================================================

    @staticmethod
    def _clean_scope_value(
        value: str
    ):

        value = value.strip(
            " -"
        )

        stop_markers = (
            " BAGAIMANA ",
            " BERAPA ",
            " APA ",
            " UNTUK ",
            " DENGAN ",
            " BULAN INI ",
            " BULAN BERJALAN ",
            " TERAKHIR ",
            " KEBELAKANG ",
            " KE BELAKANG ",
            " SEBELUMNYA ",
        )

        padded = (
            f" {value} "
        )

        for marker in stop_markers:

            if marker in padded:

                value = (
                    padded
                    .split(
                        marker,
                        1
                    )[0]
                    .strip()
                )

                padded = (
                    f" {value} "
                )

        if value in {
            "",
            "INI",
            "TERSEBUT",
            "SANA",
            "TERSEBUT?",
        }:

            return None

        return " ".join(
            word.capitalize()
            for word in value.split()
        )

    # ==========================================================
    # SITE ENTITY
    # ==========================================================

    @classmethod
    def _extract_site(
        cls,
        text,
        entity
    ):

        entity.site_id = (
            cls.extract_site_id(
                text
            )
        )

    # ==========================================================
    # CITY
    # ==========================================================

    @classmethod
    def _extract_city(
        cls,
        text,
        entity
    ):

        city = cls._find_best_match(
            text,
            cls.CITIES
        )

        if city:

            entity.city = (
                city.title()
            )

    # ==========================================================
    # VENDOR
    # ==========================================================

    @classmethod
    def _extract_vendor(
        cls,
        text,
        entity
    ):

        vendor = cls._find_best_match(
            text,
            cls.VENDORS
        )

        if vendor:

            entity.vendor = (
                vendor.title()
            )

    # ==========================================================
    # TECHNOLOGY
    # ==========================================================

    @classmethod
    def _extract_technology(
        cls,
        text,
        entity
    ):

        technology = (
            cls._find_best_match(
                text,
                cls.TECHNOLOGIES
            )
        )

        if technology:

            entity.technology = (
                technology.title()
            )

    # ==========================================================
    # BATTERY STATUS
    # ==========================================================

    @classmethod
    def _extract_battery_status(
        cls,
        text,
        entity
    ):

        status = cls._find_best_match(
            text,
            cls.BATTERY_STATUS
        )

        if status:

            entity.battery_status = (
                status.title()
            )

    # ==========================================================
    # ALARM
    # ==========================================================

    @classmethod
    def _extract_alarm(
        cls,
        text,
        entity
    ):

        alarm = cls._find_best_match(
            text,
            cls.ALARMS
        )

        if alarm:

            entity.alarm = (
                alarm.title()
            )

    # ==========================================================
    # FUZZY MATCH
    # ==========================================================

    @staticmethod
    def _find_best_match(
        text,
        candidates
    ):

        # ======================================================
        # EXACT CONTAINMENT
        # ======================================================

        for item in candidates:

            if item in text:

                return item

        # ======================================================
        # FUZZY MATCH
        # ======================================================

        matches = get_close_matches(
            " ".join(
                text.split()
            ),
            candidates,
            n=1,
            cutoff=0.75
        )

        return (
            matches[0]
            if matches
            else None
        )
