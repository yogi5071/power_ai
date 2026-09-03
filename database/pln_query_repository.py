"""
Repository for deterministic PLN variable queries.

Purpose:
    Menjalankan query PLN berdasarkan variabel/condition.

Examples:
    - Site mana yang tagihannya di bawah 1 juta?
    - Site mana yang pemakaian listriknya di atas 5000 kWh?
    - Site mana yang tagihannya di bawah 1 juta di NOP SBY?
    - Site mana yang menggunakan AMR?
    - Site mana yang schema bayarnya SARPEN?

IMPORTANT:
    Repository ini bersifat deterministic.

    AI hanya boleh membantu memahami pertanyaan menjadi parameter.
    Hasil site yang memenuhi kondisi ditentukan oleh SQL/database.

Business rules:
    - RPTAG = nilai tagihan.
    - KWHPAKAI = pemakaian listrik.
    - 0 adalah nilai valid.
    - NULL berarti data tidak tersedia.
    - SARPEN ditentukan hanya berdasarkan jenis_inquiry.
    - Jika jenis_inquiry = SARPEN, tagihan PLN bulanan
      dianggap kosong, bukan Rp0.
"""

from database.base_repository import BaseRepository


class PLNQueryRepository(BaseRepository):

    # ==========================================================
    # SCOPE COLUMNS
    # ==========================================================

    SCOPE_COLUMNS = {
        "siteid": "spm.siteid",
        "kecamatan": "ms.kecamatan",
        "kabupaten": "ms.kabupaten",
        "nop": "ms.nop_name",
        "cluster": "ms.cluster",
    }

    # ==========================================================
    # PROFILE COLUMNS
    # ==========================================================

    PROFILE_COLUMNS = {
        "pelanggan_id": "spm.pelanggan_id",
        "nama_pelanggan": "spm.nama_pelanggan",
        "tower_owner": "spm.tower_owner",
        "source_power": "spm.source_power",
        "amr": "spm.amr",
        "daya": "spm.daya",
        "jenis_inquiry": "spm.jenis_inquiry",
        "type_tarif": "spm.type_tarif",
        "schema_bayar": "spm.schema_bayar",
        "tp_nontp": "spm.tp_nontp",
    }

    # ==========================================================
    # MONTH COLUMNS
    # ==========================================================

    MONTH_COLUMNS = {
        1: {
            "name": "Januari",
            "kwh": "kwh_januari",
            "rptag": "rptag_januari",
        },
        2: {
            "name": "Februari",
            "kwh": "kwh_februari",
            "rptag": "rptag_februari",
        },
        3: {
            "name": "Maret",
            "kwh": "kwh_maret",
            "rptag": "rptag_maret",
        },
        4: {
            "name": "April",
            "kwh": "kwh_april",
            "rptag": "rptag_april",
        },
        5: {
            "name": "Mei",
            "kwh": "kwh_mei",
            "rptag": "rptag_mei",
        },
        6: {
            "name": "Juni",
            "kwh": "kwh_juni",
            "rptag": "rptag_juni",
        },
        7: {
            "name": "Juli",
            "kwh": "kwh_juli",
            "rptag": "rptag_juli",
        },
        8: {
            "name": "Agustus",
            "kwh": "kwh_agustus",
            "rptag": "rptag_agustus",
        },
        9: {
            "name": "September",
            "kwh": "kwh_september",
            "rptag": "rptag_september",
        },
        10: {
            "name": "Oktober",
            "kwh": "kwh_oktober",
            "rptag": "rptag_oktober",
        },
        11: {
            "name": "November",
            "kwh": "kwh_november",
            "rptag": "rptag_november",
        },
        12: {
            "name": "Desember",
            "kwh": "kwh_desember",
            "rptag": "rptag_desember",
        },
    }

    # ==========================================================
    # METRIC ALIASES
    # ==========================================================

    METRIC_ALIASES = {
        "rptag": "rptag",
        "tagihan": "rptag",
        "billing": "rptag",
        "harga": "rptag",
        "biaya": "rptag",
        "nominal": "rptag",

        "kwh": "kwh",
        "kwhpakai": "kwh",
        "kwh_pakai": "kwh",
        "pemakaian": "kwh",
        "pemakaian_listrik": "kwh",
        "konsumsi": "kwh",
    }

    # ==========================================================
    # OPERATOR
    # ==========================================================

    OPERATORS = {
        "<": "<",
        "<=": "<=",
        "=": "=",
        "==": "=",
        ">": ">",
        ">=": ">=",
        "!=": "!=",
        "<>": "<>",
    }

    # ==========================================================
    # NOP ALIASES
    #
    # Database menyimpan nama NOP lengkap.
    # User dapat menggunakan singkatan.
    # ==========================================================

    NOP_ALIASES = {
        "sby": "surabaya",
        "surabaya": "surabaya",

        "mlg": "malang",
        "malang": "malang",

        "kdr": "kediri",
        "kediri": "kediri",

        "madiun": "madiun",

        "lm": "lamongan",
        "lmg": "lamongan",
        "lamongan": "lamongan",

        "jbr": "jember",
        "jember": "jember",

        "bwi": "banyuwangi",
        "banyuwangi": "banyuwangi",

        "bojonegoro": "bojonegoro",

        "mojokerto": "mojokerto",

        "pasuruan": "pasuruan",

        "probolinggo": "probolinggo",

        "sidoarjo": "sidoarjo",

        "pamekasan": "pamekasan",

        "sumenep": "sumenep",

        "bangkalan": "bangkalan",

        "tuban": "tuban",

        "nganjuk": "nganjuk",

        "ngawi": "ngawi",
    }

    # ==========================================================
    # NORMALIZE METRIC
    # ==========================================================

    @classmethod
    def normalize_metric(cls, metric):

        if metric is None:
            return None

        value = (
            str(metric)
            .strip()
            .lower()
        )

        return cls.METRIC_ALIASES.get(
            value
        )

    # ==========================================================
    # NORMALIZE OPERATOR
    # ==========================================================

    @classmethod
    def normalize_operator(cls, operator):

        if operator is None:
            return None

        value = (
            str(operator)
            .strip()
        )

        return cls.OPERATORS.get(
            value
        )

    # ==========================================================
    # NORMALIZE MONTH
    # ==========================================================

    @classmethod
    def normalize_month(cls, month):

        if month is None:
            return None

        if isinstance(month, int):

            if month in cls.MONTH_COLUMNS:
                return month

            return None

        value = (
            str(month)
            .strip()
            .lower()
        )

        aliases = {
            "januari": 1,
            "jan": 1,

            "februari": 2,
            "feb": 2,

            "maret": 3,
            "mar": 3,

            "april": 4,
            "apr": 4,

            "mei": 5,

            "juni": 6,
            "jun": 6,

            "juli": 7,
            "jul": 7,

            "agustus": 8,
            "agu": 8,
            "ags": 8,
            "aug": 8,

            "september": 9,
            "sep": 9,

            "oktober": 10,
            "okt": 10,

            "november": 11,
            "nov": 11,

            "desember": 12,
            "des": 12,
        }

        if value.isdigit():

            number = int(value)

            if number in cls.MONTH_COLUMNS:
                return number

        return aliases.get(
            value
        )

    # ==========================================================
    # NORMALIZE SCOPE
    #
    # Scope type tetap:
    #   siteid
    #   kecamatan
    #   kabupaten
    #   nop
    #   cluster
    # ==========================================================

    @staticmethod
    def normalize_scope(scope):

        if scope is None:
            return None

        value = (
            str(scope)
            .strip()
            .lower()
        )

        aliases = {
            "site": "siteid",
            "site_id": "siteid",

            "kec": "kecamatan",

            "kab": "kabupaten",

            "nop": "nop",

            "cluster": "cluster",
        }

        return aliases.get(
            value,
            value
        )

    # ==========================================================
    # NORMALIZE SCOPE VALUE
    #
    # Contoh:
    #
    # scope_field = nop
    # scope_value = SBY
    #
    # menjadi:
    #
    # scope_value = surabaya
    # ==========================================================

    @classmethod
    def normalize_scope_value(
        cls,
        scope_field,
        scope_value,
    ):

        if scope_value is None:
            return None

        value = (
            str(scope_value)
            .strip()
            .lower()
        )

        if scope_field == "nop":

            return cls.NOP_ALIASES.get(
                value,
                value
            )

        return value

    # ==========================================================
    # MONTH COLUMN
    # ==========================================================

    @classmethod
    def get_metric_column(
        cls,
        metric,
        month,
    ):

        normalized_metric = (
            cls.normalize_metric(
                metric
            )
        )

        normalized_month = (
            cls.normalize_month(
                month
            )
        )

        if not normalized_metric:
            raise ValueError(
                f"Unsupported PLN metric: "
                f"{metric}"
            )

        if not normalized_month:
            raise ValueError(
                f"Unsupported PLN month: "
                f"{month}"
            )

        month_info = cls.MONTH_COLUMNS[
            normalized_month
        ]

        if normalized_metric == "kwh":
            return month_info["kwh"]

        return month_info["rptag"]

    # ==========================================================
    # GET LATEST AVAILABLE MONTH
    #
    # NULL tidak dianggap data.
    # 0 tetap dianggap data valid.
    # ==========================================================

    def get_latest_available_month(
        self,
        year,
        metric="rptag",
        scope_field=None,
        scope_value=None,
    ):

        metric = self.normalize_metric(
            metric
        )

        if metric not in (
            "kwh",
            "rptag",
        ):
            raise ValueError(
                f"Unsupported PLN metric: "
                f"{metric}"
            )

        scope_field = self.normalize_scope(
            scope_field
        )

        scope_value = self.normalize_scope_value(
            scope_field,
            scope_value
        )

        cursor = self.get_cursor()

        try:

            for month in range(
                12,
                0,
                -1,
            ):

                column = (
                    self.get_metric_column(
                        metric,
                        month
                    )
                )

                if scope_field:

                    scope_column = (
                        self.SCOPE_COLUMNS.get(
                            scope_field
                        )
                    )

                    if not scope_column:

                        raise ValueError(
                            f"Unsupported PLN scope: "
                            f"{scope_field}"
                        )

                    cursor.execute(
                        f"""
                        SELECT 1

                        FROM site_pln_monthly spm

                        INNER JOIN master_site ms
                            ON ms.siteid = spm.siteid

                        WHERE spm.tahun = %s

                          AND LOWER(
                              {scope_column}
                          ) = LOWER(%s)

                          AND spm.`{column}` IS NOT NULL

                        LIMIT 1
                        """,
                        (
                            year,
                            scope_value,
                        ),
                    )

                else:

                    cursor.execute(
                        f"""
                        SELECT 1

                        FROM site_pln_monthly spm

                        WHERE spm.tahun = %s

                          AND spm.`{column}` IS NOT NULL

                        LIMIT 1
                        """,
                        (
                            year,
                        ),
                    )

                if cursor.fetchone():

                    return month

            return None

        finally:

            cursor.close()

    # ==========================================================
    # VARIABLE QUERY
    #
    # Contoh:
    #
    # metric:
    #     rptag
    #
    # operator:
    #     <
    #
    # threshold:
    #     1000000
    #
    # scope:
    #     nop = SBY
    #
    # month=None:
    #     otomatis memakai bulan terakhir yang tersedia.
    #
    # BUSINESS RULE SARPEN:
    #     SARPEN hanya ditentukan dari jenis_inquiry.
    #     SARPEN tidak dianggap sebagai tagihan Rp0.
    # ==========================================================

    def query_metric(
        self,
        metric,
        operator,
        threshold,
        year,
        month=None,
        scope_field=None,
        scope_value=None,
        limit=100,
    ):

        metric = self.normalize_metric(
            metric
        )

        operator = self.normalize_operator(
            operator
        )

        scope_field = self.normalize_scope(
            scope_field
        )

        scope_value = self.normalize_scope_value(
            scope_field,
            scope_value
        )

        if metric not in (
            "kwh",
            "rptag",
        ):
            raise ValueError(
                f"Unsupported PLN metric: "
                f"{metric}"
            )

        if operator not in self.OPERATORS.values():

            raise ValueError(
                f"Unsupported PLN operator: "
                f"{operator}"
            )

        if threshold is None:

            raise ValueError(
                "PLN threshold cannot be None"
            )

        if month is None:

            month = (
                self.get_latest_available_month(
                    year,
                    metric,
                    scope_field,
                    scope_value,
                )
            )

            if month is None:
                return []

        else:

            month = self.normalize_month(
                month
            )

            if month is None:
                raise ValueError(
                    "Invalid PLN month"
                )

        metric_column = (
            self.get_metric_column(
                metric,
                month
            )
        )

        month_info = (
            self.MONTH_COLUMNS[
                month
            ]
        )

        scope_column = None

        if scope_field:

            scope_column = (
                self.SCOPE_COLUMNS.get(
                    scope_field
                )
            )

            if not scope_column:

                raise ValueError(
                    f"Unsupported PLN scope: "
                    f"{scope_field}"
                )

        cursor = self.get_cursor()

        try:

            query = f"""
                SELECT

                    spm.siteid,

                    ms.site_name,

                    ms.kecamatan,

                    ms.kabupaten,

                    ms.nop_name,

                    ms.cluster,

                    spm.pelanggan_id,

                    spm.nama_pelanggan,

                    spm.tower_owner,

                    spm.source_power,

                    spm.amr,

                    spm.daya,

                    spm.jenis_inquiry,

                    spm.type_tarif,

                    spm.schema_bayar,

                    spm.tp_nontp,

                    spm.tahun,

                    spm.`{metric_column}` AS nilai,

                    spm.`{month_info["kwh"]}` AS kwh_pakai,

                    spm.`{month_info["rptag"]}` AS rptag,

                    %s AS bulan

                FROM site_pln_monthly spm

                INNER JOIN master_site ms
                    ON ms.siteid = spm.siteid

                WHERE spm.tahun = %s

                  AND spm.`{metric_column}` IS NOT NULL

                  AND LOWER(
                      TRIM(
                          COALESCE(
                              spm.jenis_inquiry,
                              ''
                          )
                      )
                  ) <> 'sarpen'

                  AND spm.`{metric_column}` {operator} %s
            """

            params = [
                month_info["name"],
                year,
                threshold,
            ]

            if scope_column:

                query += f"""
                  AND LOWER(
                      {scope_column}
                  ) = LOWER(%s)
                """

                params.append(
                    scope_value
                )

            query += f"""
                ORDER BY
                    spm.`{metric_column}` DESC
            """

            if limit:

                query += """
                    LIMIT %s
                """

                params.append(
                    int(limit)
                )

            cursor.execute(
                query,
                tuple(params),
            )

            return (
                cursor.fetchall()
                or []
            )

        finally:

            cursor.close()

    # ==========================================================
    # QUERY PROFILE
    #
    # Contoh:
    # AMR = AMR
    # schema_bayar = SARPEN
    # source_power = PLN
    # ==========================================================

    def query_profile(
        self,
        field,
        value,
        scope_field=None,
        scope_value=None,
        year=None,
        limit=100,
    ):

        if field is None:

            raise ValueError(
                "PLN profile field cannot be None"
            )

        field = (
            str(field)
            .strip()
            .lower()
        )

        column = (
            self.PROFILE_COLUMNS.get(
                field
            )
        )

        if not column:

            raise ValueError(
                f"Unsupported PLN profile field: "
                f"{field}"
            )

        scope_field = self.normalize_scope(
            scope_field
        )

        scope_value = self.normalize_scope_value(
            scope_field,
            scope_value
        )

        cursor = self.get_cursor()

        try:

            query = f"""
                SELECT

                    spm.siteid,

                    ms.site_name,

                    ms.kecamatan,

                    ms.kabupaten,

                    ms.nop_name,

                    ms.cluster,

                    spm.pelanggan_id,

                    spm.nama_pelanggan,

                    spm.tower_owner,

                    spm.source_power,

                    spm.amr,

                    spm.daya,

                    spm.jenis_inquiry,

                    spm.type_tarif,

                    spm.schema_bayar,

                    spm.tp_nontp,

                    spm.tahun

                FROM site_pln_monthly spm

                INNER JOIN master_site ms
                    ON ms.siteid = spm.siteid

                WHERE LOWER(
                    {column}
                ) = LOWER(%s)
            """

            params = [
                str(
                    value
                ).strip()
            ]

            if year is not None:

                query += """
                    AND spm.tahun = %s
                """

                params.append(
                    year
                )

            if scope_field:

                scope_column = (
                    self.SCOPE_COLUMNS.get(
                        scope_field
                    )
                )

                if not scope_column:

                    raise ValueError(
                        f"Unsupported PLN scope: "
                        f"{scope_field}"
                    )

                query += f"""
                    AND LOWER(
                        {scope_column}
                    ) = LOWER(%s)
                """

                params.append(
                    scope_value
                )

            query += """
                ORDER BY
                    spm.tahun DESC
            """

            if limit:

                query += """
                    LIMIT %s
                """

                params.append(
                    int(limit)
                )

            cursor.execute(
                query,
                tuple(params),
            )

            return (
                cursor.fetchall()
                or []
            )

        finally:

            cursor.close()

    # ==========================================================
    # QUERY SITES WITH ZERO VALUE
    #
    # 0 = data valid.
    # NULL = data tidak tersedia.
    #
    # SARPEN sudah dikeluarkan oleh query_metric()
    # karena SARPEN bukan tagihan Rp0.
    # ==========================================================

    def query_zero_metric(
        self,
        metric,
        year,
        month=None,
        scope_field=None,
        scope_value=None,
        limit=100,
    ):

        return self.query_metric(
            metric=metric,
            operator="=",
            threshold=0,
            year=year,
            month=month,
            scope_field=scope_field,
            scope_value=scope_value,
            limit=limit,
        )

    # ==========================================================
    # QUERY BELOW THRESHOLD
    # ==========================================================

    def query_below(
        self,
        metric,
        threshold,
        year,
        month=None,
        scope_field=None,
        scope_value=None,
        limit=100,
    ):

        return self.query_metric(
            metric=metric,
            operator="<",
            threshold=threshold,
            year=year,
            month=month,
            scope_field=scope_field,
            scope_value=scope_value,
            limit=limit,
        )

    # ==========================================================
    # QUERY ABOVE THRESHOLD
    # ==========================================================

    def query_above(
        self,
        metric,
        threshold,
        year,
        month=None,
        scope_field=None,
        scope_value=None,
        limit=100,
    ):

        return self.query_metric(
            metric=metric,
            operator=">",
            threshold=threshold,
            year=year,
            month=month,
            scope_field=scope_field,
            scope_value=scope_value,
            limit=limit,
        )

    # ==========================================================
    # QUERY BETWEEN VALUES
    # ==========================================================

    def query_between(
        self,
        metric,
        minimum,
        maximum,
        year,
        month=None,
        scope_field=None,
        scope_value=None,
        limit=100,
    ):

        metric = self.normalize_metric(
            metric
        )

        if metric not in (
            "kwh",
            "rptag",
        ):
            raise ValueError(
                f"Unsupported PLN metric: "
                f"{metric}"
            )

        if minimum is None:

            raise ValueError(
                "Minimum cannot be None"
            )

        if maximum is None:

            raise ValueError(
                "Maximum cannot be None"
            )

        scope_field = self.normalize_scope(
            scope_field
        )

        scope_value = self.normalize_scope_value(
            scope_field,
            scope_value
        )

        if month is None:

            month = (
                self.get_latest_available_month(
                    year,
                    metric,
                    scope_field,
                    scope_value,
                )
            )

            if month is None:
                return []

        else:

            month = self.normalize_month(
                month
            )

            if month is None:

                raise ValueError(
                    "Invalid PLN month"
                )

        metric_column = (
            self.get_metric_column(
                metric,
                month
            )
        )

        month_info = (
            self.MONTH_COLUMNS[
                month
            ]
        )

        cursor = self.get_cursor()

        try:

            query = f"""
                SELECT

                    spm.siteid,

                    ms.site_name,

                    ms.kecamatan,

                    ms.kabupaten,

                    ms.nop_name,

                    ms.cluster,

                    spm.pelanggan_id,

                    spm.nama_pelanggan,

                    spm.tower_owner,

                    spm.source_power,

                    spm.amr,

                    spm.daya,

                    spm.jenis_inquiry,

                    spm.type_tarif,

                    spm.schema_bayar,

                    spm.tp_nontp,

                    spm.tahun,

                    spm.`{month_info["kwh"]}` AS kwh_pakai,

                    spm.`{month_info["rptag"]}` AS rptag,

                    spm.`{metric_column}` AS nilai,

                    %s AS bulan

                FROM site_pln_monthly spm

                INNER JOIN master_site ms
                    ON ms.siteid = spm.siteid

                WHERE spm.tahun = %s

                  AND spm.`{metric_column}` IS NOT NULL

                  AND spm.`{metric_column}` BETWEEN %s AND %s
            """

            params = [
                month_info["name"],
                year,
                minimum,
                maximum,
            ]

            if scope_field:

                scope_column = (
                    self.SCOPE_COLUMNS.get(
                        scope_field
                    )
                )

                if not scope_column:

                    raise ValueError(
                        f"Unsupported PLN scope: "
                        f"{scope_field}"
                    )

                query += f"""
                    AND LOWER(
                        {scope_column}
                    ) = LOWER(%s)
                """

                params.append(
                    scope_value
                )

            query += f"""
                ORDER BY
                    spm.`{metric_column}` DESC
            """

            if limit:

                query += """
                    LIMIT %s
                """

                params.append(
                    int(limit)
                )

            cursor.execute(
                query,
                tuple(params),
            )

            return (
                cursor.fetchall()
                or []
            )

        finally:

            cursor.close()