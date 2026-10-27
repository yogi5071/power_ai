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

    KOTA_PATTERN = (
        r"\bKOTA\s+(.+?)"
        r"(?=\s*(?:\?|,|\.|$|"
        r"\bPADA\s+BULAN\b|"
        r"\bBULAN\b|"
        r"\b(?:\d{1,2})\s+bulan))"
    )

    KABUPATEN_PATTERN = (
        r"\bKABUPATEN\s+(.+?)"
        r"(?=\s*(?:\?|,|\.|$|"
        r"\bPADA\s+BULAN\b|"
        r"\bBULAN\b|"
        r"\b(?:\d{1,2})\s+bulan))"
    )

    KECAMATAN_PATTERN = (
        r"\bKECAMATAN\s+(.+?)"
        r"(?=\s*(?:\?|,|\.|$|"
        r"\bPADA\s+BULAN\b|"
        r"\bBULAN\b|"
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
        r"\bPADA\s+BULAN\b|"
        r"\bBULAN\b|"
        r"\b(?:\d{1,2})\s+bulan))"
    )

    # ==========================================================
    # PROVINCE / UNION / WHOLE DATASET
    #
    # Dataset Power AI saat ini mencakup Jawa Timur.
    #
    # Semua istilah berikut dianggap mempunyai arti yang sama:
    #
    #   provinsi
    #   provinsi jawa timur
    #   provinsi jatim
    #   jawa timur
    #   jatim
    #   union
    #   keseluruhan
    #   seluruh site
    #   seluruh wilayah
    #   semua site
    #   semua wilayah
    #
    # Semuanya dipetakan menjadi:
    #
    #   scope_type  = province
    #   scope_value = Jawa Timur
    #
    # ==========================================================

    PROVINCE_ALIASES = (
        "PROVINSI JAWA TIMUR",
        "PROVINSI JATIM",
        "JAWA TIMUR",
        "JATIM",
    )

    WHOLE_PROVINCE_ALIASES = (
        "UNION",
        "KESELURUHAN",
        "SELURUH SITE",
        "SEMUA SITE",
        "SELURUH WILAYAH",
        "SEMUA WILAYAH",
        "SELURUH JAWA TIMUR",
        "SELURUH JATIM",
        "SEMUA JAWA TIMUR",
        "SEMUA JATIM",
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
        "BONDOWOSO",
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

    # ==========================================================
    # CONTRACT / EOC
    # ==========================================================

    CONTRACT_SUBJECT_ALIASES = {"eoc": ("EOC", "END OF CONTRACT", "AKHIR KONTRAK", "AKHIR MASA KONTRAK", "KONTRAK BERAKHIR", "KONTRAK HABIS", "KONTRAK SELESAI", "JATUH TEMPO KONTRAK", "MASA KONTRAK"), "kategori": ("KATEGORI KONTRAK", "KATEGORI"), "no_contract": ("NO CONTRACT", "NOMOR CONTRACT", "NO KONTRAK", "NOMOR KONTRAK"), "last_recurring": ("LAST RECURRING", "RECURRING TERAKHIR"), "preventif_vandalisme": ("PREVENTIF VANDALISME", "PREVENTIF", "VANDALISME")}

    CONTRACT_KEYWORDS = (
        "KONTRAK",
        "CONTRACT",
        "PERJANJIAN KONTRAK",
        "NOMOR KONTRAK",
        "NO KONTRAK",
        "MASA KONTRAK",
        "AKHIR KONTRAK",
        "AKHIR MASA KONTRAK",
        "KONTRAK BERAKHIR",
        "KONTRAK HABIS",
        "KONTRAK SELESAI",
        "JATUH TEMPO KONTRAK",
        "EOC",
        "END OF CONTRACT",
        "KATEGORI KONTRAK",
        "KATEGORI",
        "NO CONTRACT",
        "NOMOR CONTRACT",
        "LAST RECURRING",
        "RECURRING TERAKHIR",
        "PREVENTIF VANDALISME",
        "PREVENTIF",
        "VANDALISME",
    )

    EOC_BEFORE_KEYWORDS = (
        "SEBELUM",
        "KURANG DARI",
        "DI BAWAH",
        "LEBIH CEPAT DARI",
    )

    EOC_AFTER_KEYWORDS = (
        "SETELAH",
        "SESUDAH",
        "LEBIH DARI",
        "DI ATAS",
    )

    EOC_UP_TO_KEYWORDS = (
        "SAMPAI",
        "HINGGA",
        "PALING LAMBAT",
        "MAKSIMAL",
    )

    EOC_BETWEEN_KEYWORDS = (
        "ANTARA",
        "PERIODE",
        "RENTANG",
    )

    @classmethod
    def _extract_contract_subject(
        cls,
        text: str
    ):
        text = (text or "").upper().strip()

        # ======================================================
        # EOC / END OF CONTRACT
        # ======================================================

        eoc_patterns = (
            r"\bKONTRAK(?:NYA)?\b.*\bHABIS\b",
            r"\bKONTRAK(?:NYA)?\b.*\bBERAKHIR\b",
            r"\bKONTRAK(?:NYA)?\b.*\bSELESAI\b",
            r"\bKONTRAK(?:NYA)?\b.*\bJATUH\s+TEMPO\b",
            r"\bMASA\s+KONTRAK\b",
            r"\bEOC\b",
            r"\bEND\s+OF\s+CONTRACT\b",
        )

        for pattern in eoc_patterns:
            if re.search(pattern, text):
                return "eoc"

        # ======================================================
        # OTHER CONTRACT SUBJECTS
        # ======================================================

        priority = (
            "no_contract",
            "last_recurring",
            "preventif_vandalisme",
            "kategori",
        )

        for subject in priority:
            aliases = cls.CONTRACT_SUBJECT_ALIASES.get(
                subject,
                ()
            )

            for alias in aliases:
                if cls._contains_phrase(text, alias):
                    return subject

        return None
    @classmethod
    def _extract_contract_value(
        cls,
        text: str,
        subject: str
    ):
        text = (text or "").upper().strip()

        patterns = {
            "kategori": (
                r"\bKATEGORI(?:\s+KONTRAK)?\s*[:=]?\s*",
            ),
            "no_contract": (
                r"\b(?:NO\s+CONTRACT|NO\s+KONTRAK|NOMOR\s+CONTRACT|NOMOR\s+KONTRAK)\s*[:=]?\s*",
            ),
            "last_recurring": (
                r"\b(?:LAST\s+RECURRING|RECURRING\s+TERAKHIR)\s*[:=]?\s*",
            ),
            "preventif_vandalisme": (
                r"\b(?:PREVENTIF\s+VANDALISME|PREVENTIF|VANDALISME)\s*[:=]?\s*",
            ),
        }

        for pattern in patterns.get(subject, ()):
            match = re.search(pattern, text)

            if not match:
                continue

            value = text[match.end():]

            # Buang scope lokasi di bagian akhir pertanyaan.
            value = re.sub(
                r"\s+\bDI\s+(?:(?:KABUPATEN|KOTA|KECAMATAN)\s+)?[A-Z][A-Z\s-]*$",
                "",
                value,
            )

            value = value.strip(" \t\r\n:=")
            return value or None

        return None

    @classmethod
    def _extract_contract_context(
        cls,
        text: str,
        entity: Entity
    ):

        text = (
            text or ""
        ).upper().strip()

        has_contract = any(
            cls._contains_phrase(
                text,
                keyword
            )
            for keyword in cls.CONTRACT_KEYWORDS
        )

        if not has_contract:
            return

        entity.contract_subject = cls._extract_contract_subject(
            text
        )

        if entity.contract_subject is None:
            return

        # Non-EOC contract subjects use semantic values directly.
        if entity.contract_subject != "eoc":
            entity.contract_value = cls._extract_contract_value(
                text,
                entity.contract_subject
            )

            # A contract number can match SITE_PATTERN.
            # Contract semantics take precedence only here.
            if entity.contract_subject == "no_contract":
                entity.site_id = None

            return

        # EOC uses operator + date semantics.
        operator = (
            cls._extract_eoc_operator(
                text
            )
        )

        entity.eoc_operator = operator

        if operator is None:
            return

        (
            date_from,
            date_to,
        ) = cls._extract_eoc_dates(
            text,
            operator
        )

        entity.eoc_date_from = date_from
        entity.eoc_date_to = date_to
    @classmethod
    def extract(
        cls,
        message: str
    ) -> Entity:

        entity = Entity()

        text = (
            message or ""
        ).upper()

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

        entity.period_months = (
            cls.extract_period_months(
                message
            )
        )

        cls._extract_contract_context(
            message,
            entity
        )

        scope_message = message

        if (
            entity.contract_subject == "no_contract"
            and entity.contract_value
        ):
            scope_message = re.sub(
                r"\b(?:NO\s+CONTRACT|NO\s+KONTRAK|NOMOR\s+CONTRACT|NOMOR\s+KONTRAK)\s*[:=]?\s*"
                + re.escape(entity.contract_value)
                + r"\b",
                "",
                text,
                count=1
            )

        (
            entity.scope_type,
            entity.scope_value,
        ) = cls.extract_scope(
            scope_message
        )

        return entity
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

    # ==========================================================
    # CONTRACT / EOC OPERATOR
    # ==========================================================

    @classmethod
    def _extract_eoc_dates(
        cls,
        text: str,
        operator: str
    ):

        text = (
            text or ""
        ).upper().strip()

        years = re.findall(
            r"\b(20\d{2})\b",
            text
        )

        if not years:
            return (None, None)

        years = [
            int(year)
            for year in years
        ]

        if operator == "between":
            if len(years) >= 2:
                return (
                    f"{years[0]:04d}-01-01",
                    f"{years[1]:04d}-12-31"
                )
            return (None, None)

        year = years[0]

        if operator == "<":
            return (
                f"{year:04d}-01-01",
                None
            )

        if operator == ">":
            return (
                f"{year:04d}-12-31",
                None
            )

        if operator == "<=":
            return (
                None,
                f"{year:04d}-12-31"
            )

        if operator == ">=":
            return (
                f"{year:04d}-01-01",
                None
            )

        if operator == "=":
            return (
                f"{year:04d}-01-01",
                f"{year:04d}-12-31"
            )

        return (None, None)

    @classmethod
    def _extract_eoc_operator(
        cls,
        text: str
    ):

        text = (
            text or ""
        ).upper().strip()

        # ======================================================
        # BETWEEN / RANGE
        # ======================================================

        for keyword in cls.EOC_BETWEEN_KEYWORDS:

            if cls._contains_phrase(
                text,
                keyword
            ):

                return "between"

        if re.search(
            r"\bDARI\b.*\bSAMPAI\b",
            text
        ) or re.search(
            r"\bDARI\b.*\bHINGGA\b",
            text
        ):

            return "between"

        # ======================================================
        # BEFORE
        # ======================================================

        for keyword in cls.EOC_BEFORE_KEYWORDS:

            if cls._contains_phrase(
                text,
                keyword
            ):

                return "<"

        # ======================================================
        # AFTER
        # ======================================================

        for keyword in cls.EOC_AFTER_KEYWORDS:

            if cls._contains_phrase(
                text,
                keyword
            ):

                return ">"

        # ======================================================
        # UP TO / DEADLINE
        # ======================================================

        for keyword in cls.EOC_UP_TO_KEYWORDS:

            if cls._contains_phrase(
                text,
                keyword
            ):

                return "<="

        # ======================================================
        # EXPLICIT SYMBOLS
        # ======================================================

        if "<=" in text:
            return "<="

        if ">=" in text:
            return ">="

        if "<" in text:
            return "<"

        if ">" in text:
            return ">"

        if "=" in text:
            return "="

        return None
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
        # 3. KOTA
        #
        # Kota dan kabupaten harus dibedakan.
        #
        # Kota Mojokerto:
        #   scope_type  = kota
        #   scope_value = Mojokerto
        #
        # ======================================================

        match = re.search(
            cls.KOTA_PATTERN,
            text
        )

        if match:

            value = cls._clean_scope_value(
                match.group(1)
            )

            if value:

                return (
                    "kota",
                    value
                )

        # ======================================================
        # 4. KABUPATEN
        #
        # Kabupaten Mojokerto:
        #   scope_type  = kabupaten
        #   scope_value = Mojokerto
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
        # EXPLICIT NOP
        # Keep an explicit NOP label ahead of bare-city aliases
        # (for example, "NOP Malang" must remain a NOP scope).
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
        # 4A. BARE CITY NAME
        #
        # Contoh:
        #
        #   Mojokerto
        #
        # berarti pencarian gabungan:
        #
        #   Kota Mojokerto
        #   Kabupaten Mojokerto
        #
        # Repository/service akan menangani scope gabungan.
        # ======================================================

        for city in cls.CITIES:

            if cls._contains_phrase(
                text,
                city
            ):

                return (
                    "city_or_kabupaten",
                    city.title()
                )

        # ======================================================
        # 5. EXPLICIT PROVINCE
        #
        # Contoh:
        #
        #   provinsi jawa timur
        #   provinsi jatim
        #   jawa timur
        #   jatim
        #
        # Semua berarti:
        #
        #   province / Jawa Timur
        # ======================================================

        for alias in sorted(
            cls.PROVINCE_ALIASES,
            key=len,
            reverse=True
        ):

            if cls._contains_phrase(
                text,
                alias
            ):

                return (
                    "province",
                    "Jawa Timur"
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
        # 8. UNION / KESELURUHAN / SELURUH DATASET
        #
        # Karena dataset Power AI saat ini mencakup Jawa Timur,
        # semua istilah berikut berarti seluruh data Jawa Timur.
        #
        # Contoh:
        #
        #   "berapa site secara keseluruhan"
        #   "berapa site di union"
        #   "berapa site seluruhnya"
        #   "berapa site semua site"
        #
        # menjadi:
        #
        #   province / Jawa Timur
        #
        # Catatan:
        #
        # "semua site di Kecamatan Waru"
        #
        # sudah tertangkap oleh Kecamatan pada Point 2,
        # sehingga tidak jatuh ke province.
        # ======================================================

        if cls._is_whole_province_request(
            text
        ):

            return (
                "province",
                "Jawa Timur"
            )

        # ======================================================
        # 9. NO SCOPE
        # ======================================================

        return (
            None,
            None
        )

    # ==========================================================
    # WHOLE PROVINCE DETECTION
    # ==========================================================

    @classmethod
    def _is_whole_province_request(
        cls,
        text: str
    ):

        # ======================================================
        # EXPLICIT WHOLE DATASET ALIASES
        # ======================================================

        for keyword in cls.WHOLE_PROVINCE_ALIASES:

            if cls._contains_phrase(
                text,
                keyword
            ):

                return True

        # ======================================================
        # NATURAL LANGUAGE VARIATIONS
        # ======================================================

        natural_patterns = (
            r"\bSELURUHNYA\b",
            r"\bSEMUA\b",
            r"\bSECARA\s+KESELURUHAN\b",
            r"\bSECARA\s+UMUM\b",
            r"\bTINGKAT\s+PROVINSI\b",
            r"\bLEVEL\s+PROVINSI\b",
            r"\bAREA\s+JATIM\b",
            r"\bWILAYAH\s+JATIM\b",
        )

        for pattern in natural_patterns:

            if re.search(
                pattern,
                text
            ):

                return True

        return False

    # ==========================================================
    # CONTAINS PHRASE
    #
    # Dipakai supaya alias tidak salah match sebagai bagian
    # dari kata lain.
    # ==========================================================

    @staticmethod
    def _contains_phrase(
        text,
        phrase
    ):

        pattern = (
            r"(?<![A-Z0-9])"
            + re.escape(phrase)
            + r"(?![A-Z0-9])"
        )

        return bool(
            re.search(
                pattern,
                text
            )
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
        # EXPLICIT MONTH NAMES
        #
        # Query seperti:
        #
        # "pada bulan juni"
        #
        # tetap dianggap satu periode.
        # Pemilihan bulan aktual dilakukan oleh layer query.
        # ======================================================

        month_names = (
            "januari",
            "februari",
            "maret",
            "april",
            "mei",
            "juni",
            "juli",
            "agustus",
            "september",
            "oktober",
            "november",
            "desember",
        )

        for month in month_names:

            if re.search(
                rf"\b{month}\b",
                text
            ):

                return 1

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

        if value is None:
            return None

        value = value.strip(
            " -"
        )

        # ======================================================
        # STOP MARKERS
        #
        # Digunakan untuk mencegah scope mengambil bagian
        # pertanyaan berikutnya.
        #
        # Contoh:
        #
        # "Surabaya pada bulan Juni"
        #
        # harus menjadi:
        #
        # "Surabaya"
        # ======================================================

        stop_markers = (
            " PADA BULAN ",
            " BULAN ",
            " BAGAIMANA ",
            " BERAPA ",
            " APA ",
            " UNTUK ",
            " DENGAN ",
            " TERAKHIR ",
            " KEBELAKANG ",
            " KE BELAKANG ",
            " SEBELUMNYA ",
            " SEKARANG ",
            " INI ",
            " TADI ",
            " KEMARIN ",
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

        # ======================================================
        # CLEAN TRAILING QUESTION WORDS
        # ======================================================

        value = re.sub(
            r"\s+(PADA|DI|KE|DARI|DENGAN)$",
            "",
            value,
            flags=re.IGNORECASE
        )

        value = value.strip(
            " -?,."
        )

        # ======================================================
        # INVALID VALUES
        # ======================================================

        if value in {
            "",
            "INI",
            "TERSEBUT",
            "SANA",
            "TERSEBUT?",
        }:

            return None

        # ======================================================
        # NORMALIZE SPACES
        # ======================================================

        value = re.sub(
            r"\s+",
            " ",
            value
        ).strip()

        # ======================================================
        # TITLE CASE
        # ======================================================

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
        # TOKEN-BASED FUZZY MATCH
        #
        # Kita tidak langsung membandingkan seluruh kalimat
        # dengan kandidat karena itu bisa menghasilkan false
        # positive.
        # ======================================================

        words = text.split()

        # ======================================================
        # SINGLE WORD / MULTI WORD WINDOWS
        # ======================================================

        best_match = None
        best_score = 0.0

        for candidate in candidates:

            candidate_words = (
                candidate.split()
            )

            candidate_length = (
                len(candidate_words)
            )

            if candidate_length == 0:
                continue

            for index in range(
                0,
                len(words)
            ):

                window = " ".join(
                    words[
                        index:index + candidate_length
                    ]
                )

                if not window:
                    continue

                matches = get_close_matches(
                    window,
                    [candidate],
                    n=1,
                    cutoff=0.75
                )

                if matches:

                    from difflib import SequenceMatcher

                    score = (
                        SequenceMatcher(
                            None,
                            window,
                            candidate
                        ).ratio()
                    )

                    if score > best_score:

                        best_score = score
                        best_match = candidate

        return best_match





















