"""
PLN Query Service.

Purpose:
    Service layer untuk menjalankan deterministic PLN queries.

Architecture:

    User Question
        ↓
    Entity / Intent Extraction
        ↓
    PLNQueryService
        ↓
    PLNQueryRepository
        ↓
    MySQL
        ↓
    Query Result

IMPORTANT:
    Service ini TIDAK menentukan hasil berdasarkan AI.

    AI hanya memberikan parameter seperti:

        metric       = rptag
        operator     = <
        threshold    = 1000000
        scope_field  = nop
        scope_value  = SBY
        year         = 2026
        month        = None

    Repository yang menentukan hasil berdasarkan database.
"""


from datetime import date
from decimal import Decimal

from database.pln_query_repository import PLNQueryRepository


class PLNQueryService:

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    def __init__(self):

        self.repository = PLNQueryRepository()

    # ==========================================================
    # NORMALIZE YEAR
    # ==========================================================

    @staticmethod
    def normalize_year(year=None):

        if year is None:

            return date.today().year

        try:

            return int(year)

        except (
            TypeError,
            ValueError,
        ):

            raise ValueError(
                f"Invalid PLN year: {year}"
            )

    # ==========================================================
    # NORMALIZE LIMIT
    # ==========================================================

    @staticmethod
    def normalize_limit(limit=100):

        if limit is None:

            return 100

        try:

            limit = int(limit)

        except (
            TypeError,
            ValueError,
        ):

            raise ValueError(
                f"Invalid PLN limit: {limit}"
            )

        if limit <= 0:

            return 100

        return min(
            limit,
            500,
        )

    # ==========================================================
    # NORMALIZE THRESHOLD
    #
    # Threshold dapat berupa:
    #
    # 1000000
    # "1000000"
    # "1.000.000"
    # "Rp1.000.000"
    # "Rp 1.000.000"
    #
    # Tidak melakukan konversi ambigu.
    # ==========================================================

    @staticmethod
    def normalize_threshold(
        threshold
    ):

        if threshold is None:

            raise ValueError(
                "PLN threshold cannot be None"
            )

        if isinstance(
            threshold,
            Decimal,
        ):

            return threshold

        if isinstance(
            threshold,
            (int, float),
        ):

            return Decimal(
                str(threshold)
            )

        value = (
            str(threshold)
            .strip()
            .lower()
        )

        value = (
            value
            .replace(
                "rp",
                "",
            )
            .replace(
                "idr",
                "",
            )
            .replace(
                " ",
                "",
            )
        )

        # ------------------------------------------------------
        # Format Indonesia:
        #
        # 1.000.000
        # 1.500.000,50
        # ------------------------------------------------------

        if "," in value:

            value = value.replace(
                ".",
                ""
            )

            value = value.replace(
                ",",
                "."
            )

        else:

            # --------------------------------------------------
            # Jika terdapat banyak titik:
            #
            # 1.000.000
            #
            # anggap sebagai separator ribuan.
            # --------------------------------------------------

            if value.count(".") > 1:

                value = value.replace(
                    ".",
                    ""
                )

            # --------------------------------------------------
            # Satu titik:
            #
            # 1000000.50
            #
            # tetap dipertahankan sebagai decimal.
            # --------------------------------------------------

        try:

            return Decimal(
                value
            )

        except Exception:

            raise ValueError(
                f"Invalid PLN threshold: "
                f"{threshold}"
            )

    # ==========================================================
    # NORMALIZE SCOPE
    # ==========================================================

    def normalize_scope(
        self,
        scope_field=None,
        scope_value=None,
    ):

        if scope_field is None:

            return None, None

        scope_field = (
            self.repository.normalize_scope(
                scope_field
            )
        )

        scope_value = (
            self.repository.normalize_scope_value(
                scope_field,
                scope_value,
            )
        )

        return (
            scope_field,
            scope_value,
        )

    # ==========================================================
    # RESOLVE MONTH
    #
    # Jika month=None:
    #
    # repository akan mencari latest available month.
    # ==========================================================

    def resolve_month(
        self,
        metric,
        year,
        month=None,
        scope_field=None,
        scope_value=None,
    ):

        if month is not None:

            return (
                self.repository.normalize_month(
                    month
                )
            )

        return (
            self.repository.get_latest_available_month(
                year=year,
                metric=metric,
                scope_field=scope_field,
                scope_value=scope_value,
            )
        )

    # ==========================================================
    # QUERY METRIC
    #
    # General entry point:
    #
    # metric:
    #     rptag / kwh
    #
    # operator:
    #     < > <= >= = !=
    #
    # threshold:
    #     angka
    #
    # scope:
    #     optional
    # ==========================================================

    def query_metric(
        self,
        metric,
        operator,
        threshold,
        year=None,
        month=None,
        scope_field=None,
        scope_value=None,
        limit=100,
    ):

        # ------------------------------------------------------
        # NORMALIZE
        # ------------------------------------------------------

        metric = (
            self.repository.normalize_metric(
                metric
            )
        )

        operator = (
            self.repository.normalize_operator(
                operator
            )
        )

        year = (
            self.normalize_year(
                year
            )
        )

        threshold = (
            self.normalize_threshold(
                threshold
            )
        )

        (
            scope_field,
            scope_value,
        ) = self.normalize_scope(
            scope_field,
            scope_value,
        )

        limit = (
            self.normalize_limit(
                limit
            )
        )

        # ------------------------------------------------------
        # VALIDATE
        # ------------------------------------------------------

        if metric not in (
            "kwh",
            "rptag",
        ):

            raise ValueError(
                f"Unsupported PLN metric: "
                f"{metric}"
            )

        if operator not in (
            "<",
            "<=",
            "=",
            ">",
            ">=",
            "!=",
            "<>",
        ):

            raise ValueError(
                f"Unsupported PLN operator: "
                f"{operator}"
            )

        # ------------------------------------------------------
        # QUERY
        # ------------------------------------------------------

        rows = (
            self.repository.query_metric(
                metric=metric,
                operator=operator,
                threshold=threshold,
                year=year,
                month=month,
                scope_field=scope_field,
                scope_value=scope_value,
                limit=limit,
            )
        )

        # ------------------------------------------------------
        # RESOLVE ACTUAL MONTH
        #
        # Repository memilih latest month bila month=None.
        # Kita kembalikan bulan yang sebenarnya digunakan.
        # ------------------------------------------------------

        actual_month = (
            self.resolve_month(
                metric=metric,
                year=year,
                month=month,
                scope_field=scope_field,
                scope_value=scope_value,
            )
        )

        month_info = None

        if actual_month:

            month_info = (
                self.repository.MONTH_COLUMNS.get(
                    actual_month
                )
            )

        # ------------------------------------------------------
        # RETURN STRUCTURED RESULT
        # ------------------------------------------------------

        return {
            "query_type": "metric",

            "metric": metric,

            "operator": operator,

            "threshold": threshold,

            "year": year,

            "month": actual_month,

            "month_name": (
                month_info["name"]
                if month_info
                else None
            ),

            "scope_field": scope_field,

            "scope_value": scope_value,

            "count": len(rows),

            "limit": limit,

            "rows": rows,
        }

    # ==========================================================
    # QUERY BELOW
    # ==========================================================

    def query_below(
        self,
        metric,
        threshold,
        year=None,
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
    # QUERY ABOVE
    # ==========================================================

    def query_above(
        self,
        metric,
        threshold,
        year=None,
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
    # QUERY EQUAL
    # ==========================================================

    def query_equal(
        self,
        metric,
        threshold,
        year=None,
        month=None,
        scope_field=None,
        scope_value=None,
        limit=100,
    ):

        return self.query_metric(
            metric=metric,
            operator="=",
            threshold=threshold,
            year=year,
            month=month,
            scope_field=scope_field,
            scope_value=scope_value,
            limit=limit,
        )

    # ==========================================================
    # QUERY BETWEEN
    # ==========================================================

    def query_between(
        self,
        metric,
        minimum,
        maximum,
        year=None,
        month=None,
        scope_field=None,
        scope_value=None,
        limit=100,
    ):

        metric = (
            self.repository.normalize_metric(
                metric
            )
        )

        year = (
            self.normalize_year(
                year
            )
        )

        minimum = (
            self.normalize_threshold(
                minimum
            )
        )

        maximum = (
            self.normalize_threshold(
                maximum
            )
        )

        (
            scope_field,
            scope_value,
        ) = self.normalize_scope(
            scope_field,
            scope_value,
        )

        limit = (
            self.normalize_limit(
                limit
            )
        )

        rows = (
            self.repository.query_between(
                metric=metric,
                minimum=minimum,
                maximum=maximum,
                year=year,
                month=month,
                scope_field=scope_field,
                scope_value=scope_value,
                limit=limit,
            )
        )

        actual_month = (
            self.resolve_month(
                metric=metric,
                year=year,
                month=month,
                scope_field=scope_field,
                scope_value=scope_value,
            )
        )

        month_info = None

        if actual_month:

            month_info = (
                self.repository.MONTH_COLUMNS.get(
                    actual_month
                )
            )

        return {
            "query_type": "between",

            "metric": metric,

            "operator": "between",

            "minimum": minimum,

            "maximum": maximum,

            "year": year,

            "month": actual_month,

            "month_name": (
                month_info["name"]
                if month_info
                else None
            ),

            "scope_field": scope_field,

            "scope_value": scope_value,

            "count": len(rows),

            "limit": limit,

            "rows": rows,
        }

    # ==========================================================
    # QUERY ZERO
    # ==========================================================

    def query_zero(
        self,
        metric,
        year=None,
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
    # QUERY PROFILE
    #
    # Contoh:
    #
    # "Site mana yang menggunakan AMR?"
    #
    # field = amr
    # value = AMR
    # ==========================================================

    def query_profile(
        self,
        field,
        value,
        year=None,
        scope_field=None,
        scope_value=None,
        limit=100,
    ):

        year = (
            self.normalize_year(
                year
            )
        )

        (
            scope_field,
            scope_value,
        ) = self.normalize_scope(
            scope_field,
            scope_value,
        )

        limit = (
            self.normalize_limit(
                limit
            )
        )

        rows = (
            self.repository.query_profile(
                field=field,
                value=value,
                scope_field=scope_field,
                scope_value=scope_value,
                year=year,
                limit=limit,
            )
        )

        return {
            "query_type": "profile",

            "field": (
                str(field)
                .strip()
                .lower()
            ),

            "value": (
                str(value)
                .strip()
            ),

            "year": year,

            "scope_field": scope_field,

            "scope_value": scope_value,

            "count": len(rows),

            "limit": limit,

            "rows": rows,
        }

    # ==========================================================
    # CONVENIENCE:
    # QUERY AMR
    # ==========================================================

    def query_amr(
        self,
        value="AMR",
        year=None,
        scope_field=None,
        scope_value=None,
        limit=100,
    ):

        return self.query_profile(
            field="amr",
            value=value,
            year=year,
            scope_field=scope_field,
            scope_value=scope_value,
            limit=limit,
        )

    # ==========================================================
    # CONVENIENCE:
    # QUERY SOURCE POWER
    # ==========================================================

    def query_source_power(
        self,
        value="PLN",
        year=None,
        scope_field=None,
        scope_value=None,
        limit=100,
    ):

        return self.query_profile(
            field="source_power",
            value=value,
            year=year,
            scope_field=scope_field,
            scope_value=scope_value,
            limit=limit,
        )

    # ==========================================================
    # CONVENIENCE:
    # QUERY SCHEMA BAYAR
    # ==========================================================

    def query_schema_bayar(
        self,
        value,
        year=None,
        scope_field=None,
        scope_value=None,
        limit=100,
    ):

        return self.query_profile(
            field="schema_bayar",
            value=value,
            year=year,
            scope_field=scope_field,
            scope_value=scope_value,
            limit=limit,
        )

    # ==========================================================
    # CONVENIENCE:
    # QUERY TYPE TARIF
    # ==========================================================

    def query_type_tarif(
        self,
        value,
        year=None,
        scope_field=None,
        scope_value=None,
        limit=100,
    ):

        return self.query_profile(
            field="type_tarif",
            value=value,
            year=year,
            scope_field=scope_field,
            scope_value=scope_value,
            limit=limit,
        )

    # ==========================================================
    # CONVENIENCE:
    # QUERY JENIS INQUIRY
    # ==========================================================

    def query_jenis_inquiry(
        self,
        value,
        year=None,
        scope_field=None,
        scope_value=None,
        limit=100,
    ):

        return self.query_profile(
            field="jenis_inquiry",
            value=value,
            year=year,
            scope_field=scope_field,
            scope_value=scope_value,
            limit=limit,
        )

    # ==========================================================
    # CONVENIENCE:
    # QUERY CUSTOMER
    # ==========================================================

    def query_pelanggan(
        self,
        value,
        year=None,
        scope_field=None,
        scope_value=None,
        limit=100,
    ):

        return self.query_profile(
            field="pelanggan_id",
            value=value,
            year=year,
            scope_field=scope_field,
            scope_value=scope_value,
            limit=limit,
        )

    # ==========================================================
    # CONVENIENCE:
    # QUERY CUSTOMER NAME
    # ==========================================================

    def query_nama_pelanggan(
        self,
        value,
        year=None,
        scope_field=None,
        scope_value=None,
        limit=100,
    ):

        return self.query_profile(
            field="nama_pelanggan",
            value=value,
            year=year,
            scope_field=scope_field,
            scope_value=scope_value,
            limit=limit,
        )

    # ==========================================================
    # CONVENIENCE:
    # QUERY TOWER OWNER
    # ==========================================================

    def query_tower_owner(
        self,
        value,
        year=None,
        scope_field=None,
        scope_value=None,
        limit=100,
    ):

        return self.query_profile(
            field="tower_owner",
            value=value,
            year=year,
            scope_field=scope_field,
            scope_value=scope_value,
            limit=limit,
        )

    # ==========================================================
    # CONVENIENCE:
    # QUERY DAYA
    # ==========================================================

    def query_daya(
        self,
        operator,
        threshold,
        year=None,
        scope_field=None,
        scope_value=None,
        limit=100,
    ):

        operator = (
            self.repository.normalize_operator(
                operator
            )
        )

        threshold = (
            self.normalize_threshold(
                threshold
            )
        )

        year = (
            self.normalize_year(
                year
            )
        )

        (
            scope_field,
            scope_value,
        ) = self.normalize_scope(
            scope_field,
            scope_value,
        )

        limit = (
            self.normalize_limit(
                limit
            )
        )

        cursor = self.repository.get_cursor()

        try:

            scope_sql = ""

            params = [
                year,
                threshold,
            ]

            if scope_field:

                scope_column = (
                    self.repository.SCOPE_COLUMNS.get(
                        scope_field
                    )
                )

                if not scope_column:

                    raise ValueError(
                        f"Unsupported PLN scope: "
                        f"{scope_field}"
                    )

                scope_sql = f"""
                    AND LOWER(
                        {scope_column}
                    ) = LOWER(%s)
                """

                params.append(
                    scope_value
                )

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

                WHERE spm.tahun = %s

                  AND spm.daya IS NOT NULL

                  AND spm.daya {operator} %s

                  {scope_sql}

                ORDER BY
                    spm.daya DESC

                LIMIT %s
            """

            params.append(
                limit
            )

            cursor.execute(
                query,
                tuple(params),
            )

            rows = (
                cursor.fetchall()
                or []
            )

            return {
                "query_type": "daya",

                "field": "daya",

                "operator": operator,

                "threshold": threshold,

                "year": year,

                "scope_field": scope_field,

                "scope_value": scope_value,

                "count": len(rows),

                "limit": limit,

                "rows": rows,
            }

        finally:

            cursor.close()