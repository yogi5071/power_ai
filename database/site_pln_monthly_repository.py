"""
Repository for site_pln_monthly.

Data source:
    site_pln_monthly

Scope hierarchy:
    siteid
    kecamatan
    kabupaten
    nop
    cluster
    province / union

PLN data:
    Site Profile
        pelanggan_id
        nama_pelanggan
        tower_owner
        source_power
        amr
        daya
        jenis_inquiry
        type_tarif
        schema_bayar
        tp_nontp

    Monthly:
        KWHPAKAI
        RPTAG

Business rule:
    - NULL berbeda dengan 0.
    - 0 adalah nilai data yang valid.
    - NULL berarti data bulan tersebut tidak tersedia.
    - SARPEN dapat memiliki SourcePower = PLN tetapi
      pelanggan/schema_bayar = SARPEN dan historical
      KWH/RPTAG = 0.
"""

from database.base_repository import BaseRepository


class SitePLNMonthlyRepository(BaseRepository):

    # ==========================================================
    # SCOPE COLUMNS
    # ==========================================================

    SCOPE_COLUMNS = {
        "siteid": "ms.siteid",
        "kecamatan": "ms.kecamatan",
        "kabupaten": "ms.kabupaten",
        "nop": "ms.nop_name",
        "cluster": "ms.cluster",
    }

    # ==========================================================
    # PROVINCE / UNION
    # ==========================================================

    PROVINCE_SCOPES = {
        "province",
        "provinsi",
        "union",
        "keseluruhan",
    }

    # ==========================================================
    # MONTH COLUMNS
    #
    # Setiap bulan memiliki:
    #
    #   KWHPAKAI
    #   RPTAG
    #
    # Jangan menggunakan COALESCE(..., 0)
    # karena NULL harus tetap dibedakan dari 0.
    # ==========================================================

    MONTH_COLUMNS = {
        1: {
            "kwh": "kwh_januari",
            "rptag": "rptag_januari",
        },
        2: {
            "kwh": "kwh_februari",
            "rptag": "rptag_februari",
        },
        3: {
            "kwh": "kwh_maret",
            "rptag": "rptag_maret",
        },
        4: {
            "kwh": "kwh_april",
            "rptag": "rptag_april",
        },
        5: {
            "kwh": "kwh_mei",
            "rptag": "rptag_mei",
        },
        6: {
            "kwh": "kwh_juni",
            "rptag": "rptag_juni",
        },
        7: {
            "kwh": "kwh_juli",
            "rptag": "rptag_juli",
        },
        8: {
            "kwh": "kwh_agustus",
            "rptag": "rptag_agustus",
        },
        9: {
            "kwh": "kwh_september",
            "rptag": "rptag_september",
        },
        10: {
            "kwh": "kwh_oktober",
            "rptag": "rptag_oktober",
        },
        11: {
            "kwh": "kwh_november",
            "rptag": "rptag_november",
        },
        12: {
            "kwh": "kwh_desember",
            "rptag": "rptag_desember",
        },
    }

    # ==========================================================
    # MONTH NAMES
    # ==========================================================

    MONTH_NAMES = {
        1: "Januari",
        2: "Februari",
        3: "Maret",
        4: "April",
        5: "Mei",
        6: "Juni",
        7: "Juli",
        8: "Agustus",
        9: "September",
        10: "Oktober",
        11: "November",
        12: "Desember",
    }

    # ==========================================================
    # NORMALIZE SCOPE
    # ==========================================================

    @classmethod
    def normalize_scope(cls, scope_field):

        if scope_field is None:
            return None

        scope = str(
            scope_field
        ).strip().lower()

        if scope in cls.PROVINCE_SCOPES:
            return "union"

        return scope

    # ==========================================================
    # MONTHLY PLN
    #
    # Return:
    #
    # {
    #     year,
    #     month,
    #     month_name,
    #     total_site,
    #     total_kwh,
    #     total_value,
    #     average_kwh,
    #     average_value,
    #     minimum_kwh,
    #     maximum_kwh,
    #     minimum_value,
    #     maximum_value
    # }
    #
    # IMPORTANT:
    #
    # SQL aggregate secara natural mengabaikan NULL.
    #
    # Jadi:
    #
    #   NULL -> tidak dihitung
    #   0    -> tetap dihitung
    #
    # Ini sesuai rule data PLN kita.
    # ==========================================================

    def get_months(
        self,
        scope_field,
        scope_value,
        periods,
    ):

        if not periods:
            return []

        values = []

        cursor = self.get_cursor()

        scope_field = self.normalize_scope(
            scope_field
        )

        try:

            for year, month in periods:

                if month not in self.MONTH_COLUMNS:

                    raise ValueError(
                        f"Unsupported PLN month: {month}"
                    )

                columns = self.MONTH_COLUMNS[
                    month
                ]

                kwh_column = columns["kwh"]
                rptag_column = columns["rptag"]

                # ==================================================
                # UNION / PROVINCE
                # ==================================================

                if scope_field == "union":

                    cursor.execute(
                        f"""
                        SELECT

                            COUNT(
                                DISTINCT spm.siteid
                            ) AS total_site,

                            SUM(
                                spm.`{kwh_column}`
                            ) AS total_kwh,

                            SUM(
                                spm.`{rptag_column}`
                            ) AS total_value,

                            AVG(
                                spm.`{kwh_column}`
                            ) AS average_kwh,

                            AVG(
                                spm.`{rptag_column}`
                            ) AS average_value,

                            MIN(
                                spm.`{kwh_column}`
                            ) AS minimum_kwh,

                            MAX(
                                spm.`{kwh_column}`
                            ) AS maximum_kwh,

                            MIN(
                                spm.`{rptag_column}`
                            ) AS minimum_value,

                            MAX(
                                spm.`{rptag_column}`
                            ) AS maximum_value

                        FROM site_pln_monthly spm

                        INNER JOIN master_site ms
                            ON ms.siteid = spm.siteid

                        WHERE spm.tahun = %s

                          AND (
                              spm.`{kwh_column}` IS NOT NULL
                              OR spm.`{rptag_column}` IS NOT NULL
                          )
                        """,
                        (
                            year,
                        ),
                    )

                # ==================================================
                # SITE / KECAMATAN / KABUPATEN / NOP / CLUSTER
                # ==================================================

                else:

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
                        SELECT

                            COUNT(
                                DISTINCT spm.siteid
                            ) AS total_site,

                            SUM(
                                spm.`{kwh_column}`
                            ) AS total_kwh,

                            SUM(
                                spm.`{rptag_column}`
                            ) AS total_value,

                            AVG(
                                spm.`{kwh_column}`
                            ) AS average_kwh,

                            AVG(
                                spm.`{rptag_column}`
                            ) AS average_value,

                            MIN(
                                spm.`{kwh_column}`
                            ) AS minimum_kwh,

                            MAX(
                                spm.`{kwh_column}`
                            ) AS maximum_kwh,

                            MIN(
                                spm.`{rptag_column}`
                            ) AS minimum_value,

                            MAX(
                                spm.`{rptag_column}`
                            ) AS maximum_value

                        FROM site_pln_monthly spm

                        INNER JOIN master_site ms
                            ON ms.siteid = spm.siteid

                        WHERE spm.tahun = %s

                          AND LOWER(
                              {scope_column}
                          ) = LOWER(%s)

                          AND (
                              spm.`{kwh_column}` IS NOT NULL
                              OR spm.`{rptag_column}` IS NOT NULL
                          )
                        """,
                        (
                            year,
                            str(
                                scope_value
                            ).strip(),
                        ),
                    )

                row = (
                    cursor.fetchone()
                    or {}
                )

                values.append(
                    {
                        "year": year,

                        "month": month,

                        "month_name": (
                            self.MONTH_NAMES[
                                month
                            ]
                        ),

                        **row,
                    }
                )

            return values

        finally:

            cursor.close()

    # ==========================================================
    # PLN SITE PROFILE
    #
    # Profile adalah struktur PLN site.
    #
    # Bukan monthly billing.
    # ==========================================================

    def get_site_profile(
        self,
        siteid,
        tahun=None,
    ):

        cursor = self.get_cursor()

        try:

            if tahun is None:

                cursor.execute(
                    """
                    SELECT

                        spm.siteid,

                        ms.site_name,

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

                    LEFT JOIN master_site ms
                        ON ms.siteid = spm.siteid

                    WHERE LOWER(
                        spm.siteid
                    ) = LOWER(%s)

                    ORDER BY spm.tahun DESC

                    LIMIT 1
                    """,
                    (
                        str(
                            siteid
                        ).strip(),
                    ),
                )

            else:

                cursor.execute(
                    """
                    SELECT

                        spm.siteid,

                        ms.site_name,

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

                    LEFT JOIN master_site ms
                        ON ms.siteid = spm.siteid

                    WHERE LOWER(
                        spm.siteid
                    ) = LOWER(%s)

                      AND spm.tahun = %s

                    LIMIT 1
                    """,
                    (
                        str(
                            siteid
                        ).strip(),

                        tahun,
                    ),
                )

            return (
                cursor.fetchone()
                or None
            )

        finally:

            cursor.close()

    # ==========================================================
    # PLN SITE MONTHLY RAW DATA
    #
    # Digunakan ketika kita membutuhkan historical lengkap
    # untuk satu site.
    # ==========================================================

    def get_site_monthly(
        self,
        siteid,
        tahun=None,
    ):

        cursor = self.get_cursor()

        try:

            if tahun is None:

                cursor.execute(
                    """
                    SELECT *

                    FROM site_pln_monthly

                    WHERE LOWER(
                        siteid
                    ) = LOWER(%s)

                    ORDER BY tahun DESC

                    LIMIT 1
                    """,
                    (
                        str(
                            siteid
                        ).strip(),
                    ),
                )

            else:

                cursor.execute(
                    """
                    SELECT *

                    FROM site_pln_monthly

                    WHERE LOWER(
                        siteid
                    ) = LOWER(%s)

                      AND tahun = %s

                    LIMIT 1
                    """,
                    (
                        str(
                            siteid
                        ).strip(),

                        tahun,
                    ),
                )

            return (
                cursor.fetchone()
                or None
            )

        finally:

            cursor.close()

      # ==========================================================
    # PLN SITE CAPACITY / DAYA
    #
    # Kapasitas/daya PLN adalah nilai per site.
    #
    # Source:
    #     site_pln_monthly.daya
    #
    # Tidak melakukan:
    #     SUM
    #     AVG
    #     MIN
    #     MAX
    # ==========================================================

    def get_site_capacity(
        self,
        siteid,
        year,
    ):

        cursor = self.get_cursor()

        try:

            cursor.execute(
                """
                SELECT

                    spm.siteid,

                    spm.tahun,

                    spm.daya AS kapasitas_pln

                FROM site_pln_monthly spm

                WHERE LOWER(
                    spm.siteid
                ) = LOWER(%s)

                  AND spm.tahun = %s

                LIMIT 1
                """,
                (
                    str(
                        siteid
                    ).strip(),

                    year,
                ),
            )

            return (
                cursor.fetchone()
                or {}
            )

        finally:

            cursor.close()

    # ==========================================================
    # COMPLETE SITE DATA
    #
    # Profile + raw monthly.
    # ==========================================================

    def get_site_data(
        self,
        siteid,
        tahun=None,
    ):

        profile = self.get_site_profile(
            siteid,
            tahun,
        )

        if profile is None:
            return None

        monthly = self.get_site_monthly(
            siteid,
            profile.get("tahun")
            if tahun is None
            else tahun,
        )

        result = dict(
            profile
        )

        if monthly:
            result.update(
                monthly
            )

        return result