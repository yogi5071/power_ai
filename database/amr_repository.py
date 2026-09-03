"""Read-only repository for AMR analysis."""

from database.base_repository import BaseRepository


class AMRRepository(BaseRepository):

    # ==========================================================
    # SCOPE
    # ==========================================================

    SCOPE_COLUMNS = {
        "siteid": "ms.siteid",
        "kecamatan": "ms.kecamatan",
        "kabupaten": "ms.kabupaten",
        "nop": "ms.nop_name",
        "cluster": "ms.cluster",
    }

    # ==========================================================
    # AMR STATUS
    # ==========================================================

    AMR_STATUS = "AMR"

    NOT_AMR_STATUS = "Belum AMR"

    UNKNOWN_STATUS = "-"

    # ==========================================================
    # GET STATUS FOR ONE SITE
    # ==========================================================

    def get_site_status(self, siteid, year):

        cursor = self.get_cursor()

        try:

            cursor.execute(
                """
                SELECT
                    spm.siteid,
                    spm.tahun,
                    spm.amr
                FROM site_pln_monthly spm
                WHERE LOWER(spm.siteid) = LOWER(%s)
                  AND spm.tahun = %s
                LIMIT 1
                """,
                (
                    str(siteid).strip(),
                    year,
                ),
            )

            row = cursor.fetchone() or {}

            # ==================================================
            # NORMALIZE STATUS
            #
            # NULL / kosong dianggap:
            # Belum ada informasi
            # ==================================================

            if row:

                status = row.get("amr")

                if status is None:
                    row["amr"] = self.UNKNOWN_STATUS

                elif not str(status).strip():
                    row["amr"] = self.UNKNOWN_STATUS

                else:
                    row["amr"] = str(status).strip()

            return row

        finally:

            cursor.close()

    # ==========================================================
    # GET AMR STATISTICS
    #
    # Menghasilkan 3 kategori:
    #
    # AMR
    # Belum AMR
    # -
    #
    # NULL / kosong juga masuk kategori "-".
    # ==========================================================

    def get_statistics(
        self,
        scope_field,
        scope_value,
        year
    ):

        cursor = self.get_cursor()

        try:

            # ==================================================
            # UNION
            #
            # UNION = SELURUH SITE
            # ==================================================

            if scope_field == "union":

                cursor.execute(
                    """
                    SELECT

                        COUNT(DISTINCT spm.siteid)
                            AS total_site,

                        COUNT(
                            DISTINCT CASE
                                WHEN LOWER(TRIM(spm.amr))
                                     = LOWER(%s)
                                THEN spm.siteid
                            END
                        ) AS total_amr,

                        COUNT(
                            DISTINCT CASE
                                WHEN LOWER(TRIM(spm.amr))
                                     = LOWER(%s)
                                THEN spm.siteid
                            END
                        ) AS total_belum_amr,

                        COUNT(
                            DISTINCT CASE
                                WHEN spm.amr IS NULL
                                  OR TRIM(spm.amr) = ''
                                  OR TRIM(spm.amr) = %s
                                THEN spm.siteid
                            END
                        ) AS total_unknown

                    FROM site_pln_monthly spm

                    WHERE spm.tahun = %s
                    """,
                    (
                        self.AMR_STATUS,
                        self.NOT_AMR_STATUS,
                        self.UNKNOWN_STATUS,
                        year,
                    ),
                )

            # ==================================================
            # OTHER SCOPES
            #
            # siteid
            # kecamatan
            # kabupaten
            # nop
            # cluster
            # ==================================================

            else:

                scope_column = self.SCOPE_COLUMNS.get(
                    scope_field
                )

                if not scope_column:

                    raise ValueError(
                        f"Unsupported AMR scope: {scope_field}"
                    )

                cursor.execute(
                    f"""
                    SELECT

                        COUNT(DISTINCT spm.siteid)
                            AS total_site,

                        COUNT(
                            DISTINCT CASE
                                WHEN LOWER(TRIM(spm.amr))
                                     = LOWER(%s)
                                THEN spm.siteid
                            END
                        ) AS total_amr,

                        COUNT(
                            DISTINCT CASE
                                WHEN LOWER(TRIM(spm.amr))
                                     = LOWER(%s)
                                THEN spm.siteid
                            END
                        ) AS total_belum_amr,

                        COUNT(
                            DISTINCT CASE
                                WHEN spm.amr IS NULL
                                  OR TRIM(spm.amr) = ''
                                  OR TRIM(spm.amr) = %s
                                THEN spm.siteid
                            END
                        ) AS total_unknown

                    FROM site_pln_monthly spm

                    INNER JOIN master_site ms
                        ON ms.siteid = spm.siteid

                    WHERE spm.tahun = %s
                      AND LOWER({scope_column})
                          = LOWER(%s)
                    """,
                    (
                        self.AMR_STATUS,
                        self.NOT_AMR_STATUS,
                        self.UNKNOWN_STATUS,
                        year,
                        str(scope_value).strip(),
                    ),
                )

            return cursor.fetchone() or {}

        finally:

            cursor.close()

    # ==========================================================
    # GET SITE LIST BY AMR STATUS
    #
    # Digunakan nanti untuk pertanyaan:
    #
    # "Site mana saja yang belum AMR?"
    #
    # "Site mana saja yang sudah AMR?"
    #
    # "Site mana saja yang belum ada informasi?"
    # ==========================================================

    def get_sites_by_status(
        self,
        scope_field,
        scope_value,
        status,
        year
    ):

        cursor = self.get_cursor()

        try:

            # ==================================================
            # UNION
            # ==================================================

            if scope_field == "union":

                if status == self.UNKNOWN_STATUS:

                    cursor.execute(
                        """
                        SELECT
                            spm.siteid,
                            spm.tahun,
                            spm.amr
                        FROM site_pln_monthly spm
                        WHERE spm.tahun = %s
                          AND (
                              spm.amr IS NULL
                              OR TRIM(spm.amr) = ''
                              OR TRIM(spm.amr) = %s
                          )
                        ORDER BY spm.siteid
                        """,
                        (
                            year,
                            self.UNKNOWN_STATUS,
                        ),
                    )

                else:

                    cursor.execute(
                        """
                        SELECT
                            spm.siteid,
                            spm.tahun,
                            spm.amr
                        FROM site_pln_monthly spm
                        WHERE spm.tahun = %s
                          AND LOWER(TRIM(spm.amr))
                              = LOWER(%s)
                        ORDER BY spm.siteid
                        """,
                        (
                            year,
                            status,
                        ),
                    )

            # ==================================================
            # OTHER SCOPES
            # ==================================================

            else:

                scope_column = self.SCOPE_COLUMNS.get(
                    scope_field
                )

                if not scope_column:

                    raise ValueError(
                        f"Unsupported AMR scope: {scope_field}"
                    )

                if status == self.UNKNOWN_STATUS:

                    cursor.execute(
                        f"""
                        SELECT
                            spm.siteid,
                            spm.tahun,
                            spm.amr
                        FROM site_pln_monthly spm

                        INNER JOIN master_site ms
                            ON ms.siteid = spm.siteid

                        WHERE spm.tahun = %s
                          AND LOWER({scope_column})
                              = LOWER(%s)
                          AND (
                              spm.amr IS NULL
                              OR TRIM(spm.amr) = ''
                              OR TRIM(spm.amr) = %s
                          )

                        ORDER BY spm.siteid
                        """,
                        (
                            year,
                            str(scope_value).strip(),
                            self.UNKNOWN_STATUS,
                        ),
                    )

                else:

                    cursor.execute(
                        f"""
                        SELECT
                            spm.siteid,
                            spm.tahun,
                            spm.amr
                        FROM site_pln_monthly spm

                        INNER JOIN master_site ms
                            ON ms.siteid = spm.siteid

                        WHERE spm.tahun = %s
                          AND LOWER({scope_column})
                              = LOWER(%s)
                          AND LOWER(TRIM(spm.amr))
                              = LOWER(%s)

                        ORDER BY spm.siteid
                        """,
                        (
                            year,
                            str(scope_value).strip(),
                            status,
                        ),
                    )

            return cursor.fetchall() or []

        finally:

            cursor.close()