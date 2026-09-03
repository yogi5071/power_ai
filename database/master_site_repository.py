from database.base_repository import BaseRepository
from metadata.master_site import MASTER_SITE
from models.site import Site


class SiteRepository(BaseRepository):

    # =====================================================
    # TOTAL SITE
    # =====================================================

    def count_sites(self):

        cursor = self.get_cursor()

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM master_site
        """)

        row = cursor.fetchone()

        cursor.close()

        return row["total"]

    # =====================================================
    # SEARCH SITE
    # =====================================================

    def search_site(self, keyword):

        cursor = self.get_cursor()

        sql = """
            SELECT
                siteid,
                site_name,
                cluster,
                kabupaten,
                kecamatan,
                longitude,
                latitude,
                battery,
                total_bank,
                total_load_rectifier_a,
                kategori_rectifier,
                tgl_instalasi_battery,
                status_warranty_battery
            FROM master_site
            WHERE
                siteid LIKE %s
                OR site_name LIKE %s
                OR cluster LIKE %s
                OR kabupaten LIKE %s
                OR kecamatan LIKE %s
            ORDER BY site_name
            LIMIT 20
        """

        like = f"%{keyword}%"

        cursor.execute(
            sql,
            (
                like,
                like,
                like,
                like,
                like,
            )
        )

        rows = cursor.fetchall()

        cursor.close()

        return [
            Site(row)
            for row in rows
        ]

    # =====================================================
    # DETAIL SITE
    # =====================================================

    def get_site_detail(self, siteid):

        cursor = self.get_cursor()

        sql = """
            SELECT
                siteid,
                site_name,
                cluster,
                kabupaten,
                kecamatan,
                longitude,
                latitude,
                battery,
                total_bank,
                total_load_rectifier_a,
                kategori_rectifier,
                tgl_instalasi_battery,
                status_warranty_battery
            FROM master_site
            WHERE siteid=%s
        """

        cursor.execute(
            sql,
            (siteid,)
        )

        row = cursor.fetchone()

        cursor.close()

        if row is None:
            return None

        return Site(row)

    # =====================================================
    # BATTERY BY KABUPATEN
    # =====================================================

    def get_sites_by_kabupaten(self, kabupaten):
        """Return all sites in one kabupaten using a parameterized query."""

        cursor = self.get_cursor()

        sql = """
            SELECT
                siteid,
                site_name,
                cluster,
                kabupaten,
                kecamatan,
                longitude,
                latitude,
                battery,
                total_bank,
                total_load_rectifier_a,
                kategori_rectifier,
                tgl_instalasi_battery,
                status_warranty_battery
            FROM master_site
            WHERE LOWER(kabupaten) = LOWER(%s)
            ORDER BY siteid
        """

        cursor.execute(
            sql,
            (kabupaten.strip(),)
        )

        rows = cursor.fetchall()

        cursor.close()

        return [
            Site(row)
            for row in rows
        ]

    # =====================================================
    # BATTERY BY KECAMATAN
    # =====================================================

    def get_sites_by_kecamatan(self, kecamatan):
        """Return all sites in one kecamatan using a parameterized query."""

        cursor = self.get_cursor()

        sql = """
            SELECT
                siteid,
                site_name,
                cluster,
                kabupaten,
                kecamatan,
                longitude,
                latitude,
                battery,
                total_bank,
                total_load_rectifier_a,
                kategori_rectifier,
                tgl_instalasi_battery,
                status_warranty_battery
            FROM master_site
            WHERE LOWER(kecamatan) = LOWER(%s)
            ORDER BY siteid
        """

        cursor.execute(
            sql,
            (kecamatan.strip(),)
        )

        rows = cursor.fetchall()

        cursor.close()

        return [
            Site(row)
            for row in rows
        ]


    # =====================================================
    # BATTERY BY PROVINCE
    # =====================================================

    def get_sites_by_province(self, province):
        """
        Return all sites for a supported province.

        master_site saat ini merupakan dataset Jawa Timur,
        sehingga seluruh isi master_site merepresentasikan
        Provinsi Jawa Timur.
        """

        normalized = (
            str(province)
            .strip()
            .lower()
        )

        if normalized not in {
            "jawa timur",
            "jatim",
            "province",
        }:
            raise ValueError(
                f"Unsupported province: {province}"
            )

        cursor = self.get_cursor()

        try:

            cursor.execute("""
                SELECT
                    siteid,
                    site_name,
                    cluster,
                    kabupaten,
                    kecamatan,
                    longitude,
                    latitude,
                    battery,
                    total_bank,
                    total_load_rectifier_a,
                    kategori_rectifier,
                    tgl_instalasi_battery,
                    status_warranty_battery
                FROM master_site
                ORDER BY siteid
            """)

            rows = cursor.fetchall()

            return [
                Site(row)
                for row in rows
            ]

        finally:
            cursor.close()

    # =====================================================
    # SAFE METADATA-DRIVEN QUERY
    # =====================================================

    def get_distinct_values(self, field_name):
        """Read runtime values for one whitelisted metadata field."""

        if not MASTER_SITE.has(field_name):
            raise ValueError(
                f"Unknown master_site field: {field_name}"
            )

        column = MASTER_SITE.get(field_name).column

        cursor = self.get_cursor()

        try:

            cursor.execute(
                f"""
                SELECT DISTINCT `{column}` AS value
                FROM `master_site`
                WHERE `{column}` IS NOT NULL
                  AND `{column}` <> ''
                """
            )

            return [
                row["value"]
                for row in cursor.fetchall()
            ]

        finally:

            cursor.close()

    # =====================================================
    # SAFE AGGREGATE QUERY
    # =====================================================

    def query_aggregate(
        self,
        operation,
        metric_field,
        filters,
        group_by=None,
        limit=10
    ):
        """Execute a read-only aggregate query using only metadata fields."""

        if operation not in {
            "count",
            "sum",
            "average"
        }:
            raise ValueError(
                f"Unsupported aggregate operation: {operation}"
            )

        if (
            metric_field
            and not MASTER_SITE.has(metric_field)
        ):
            raise ValueError(
                f"Unknown metric field: {metric_field}"
            )

        if (
            group_by
            and not MASTER_SITE.has(group_by)
        ):
            raise ValueError(
                f"Unknown group field: {group_by}"
            )

        for field_name, _ in filters:

            if not MASTER_SITE.has(field_name):
                raise ValueError(
                    f"Unknown filter field: {field_name}"
                )

        if operation == "count":

            aggregate = "COUNT(*)"

        else:

            column = MASTER_SITE.get(
                metric_field
            ).column

            function = (
                "SUM"
                if operation == "sum"
                else "AVG"
            )

            aggregate = (
                f"{function}(COALESCE(`{column}`, 0))"
            )

        select = f"{aggregate} AS value"

        group_clause = ""

        order_clause = ""

        if group_by:

            group_column = MASTER_SITE.get(
                group_by
            ).column

            select = (
                f"`{group_column}` AS group_value, "
                f"{aggregate} AS value"
            )

            group_clause = (
                f" GROUP BY `{group_column}`"
            )

            order_clause = (
                " ORDER BY value DESC"
            )

        conditions = []

        params = []

        for field_name, value in filters:

            column = MASTER_SITE.get(
                field_name
            ).column

            conditions.append(
                f"LOWER(`{column}`) = LOWER(%s)"
            )

            params.append(
                str(value)
            )

        where_clause = (
            f" WHERE {' AND '.join(conditions)}"
            if conditions
            else ""
        )

        safe_limit = max(
            1,
            min(int(limit), 100)
        )

        sql = (
            f"SELECT {select} "
            f"FROM `master_site`"
            f"{where_clause}"
            f"{group_clause}"
            f"{order_clause}"
            f" LIMIT {safe_limit}"
        )

        cursor = self.get_cursor()

        try:

            cursor.execute(
                sql,
                tuple(params)
            )

            return cursor.fetchall()

        finally:

            cursor.close()

    # =====================================================
    # LIST SITE
    # =====================================================

    def list_sites(
        self,
        filters,
        limit=10
    ):
        """Return a small, safe, read-only site list for a metadata filter set."""

        for field_name, _ in filters:

            if not MASTER_SITE.has(field_name):
                raise ValueError(
                    f"Unknown filter field: {field_name}"
                )

        conditions = []

        params = []

        for field_name, value in filters:

            column = MASTER_SITE.get(
                field_name
            ).column

            conditions.append(
                f"LOWER(`{column}`) = LOWER(%s)"
            )

            params.append(
                str(value)
            )

        where_clause = (
            f" WHERE {' AND '.join(conditions)}"
            if conditions
            else ""
        )

        safe_limit = max(
            1,
            min(int(limit), 25)
        )

        sql = (
            "SELECT "
            "siteid, "
            "site_name, "
            "kabupaten, "
            "kecamatan, "
            "cluster, "
            "battery, "
            "umur_battery_tahun, "
            "status_warranty_battery "
            "FROM `master_site`"
            f"{where_clause} "
            "ORDER BY siteid "
            f"LIMIT {safe_limit}"
        )

        cursor = self.get_cursor()

        try:

            cursor.execute(
                sql,
                tuple(params)
            )

            return cursor.fetchall()

        finally:

            cursor.close()

    # =====================================================
    # OLD BATTERY
    # =====================================================

    def get_old_battery(self):

        cursor = self.get_cursor()

        cursor.execute("""
            SELECT
                siteid,
                site_name,
                cluster,
                kabupaten,
                kecamatan,
                longitude,
                latitude,
                battery,
                total_bank,
                total_load_rectifier_a,
                kategori_rectifier,
                tgl_instalasi_battery,
                status_warranty_battery
            FROM master_site
        """)

        rows = cursor.fetchall()

        cursor.close()

        sites = [
            Site(row)
            for row in rows
        ]

        return [
            site
            for site in sites
            if site.battery_age > 1
        ]

    # =====================================================
    # WARRANTY EXPIRED
    # =====================================================

    def get_warranty_expired(self):

        cursor = self.get_cursor()

        cursor.execute("""
            SELECT
                siteid,
                site_name,
                status_warranty_battery
            FROM master_site
            WHERE status_warranty_battery='Expired'
        """)

        rows = cursor.fetchall()

        cursor.close()

        return rows

    # =====================================================
    # RECTIFIER OBSOLETE
    # =====================================================

    def get_rectifier_obsolete(
        self,
        scope_field=None,
        scope_value=None
    ):
        """
        Return sites that have rectifier obsolete units.

        Supported scope:
        - None
        - province
        - siteid
        - kecamatan
        - kabupaten
        - nop_name
        - cluster

        Obsolete unit is determined from:
            jumlah_rectifier_obsolete > 0

        This method intentionally does not use
        kategori_rectifier as the unit-level condition.
        """

        allowed_scope = {
            "siteid",
            "kecamatan",
            "kabupaten",
            "nop_name",
            "cluster",
            "province",
        }

        if scope_field is not None:

            if scope_field not in allowed_scope:
                raise ValueError(
                    f"Unsupported rectifier scope: {scope_field}"
                )

            # =================================================
            # PROVINCE
            #
            # master_site saat ini adalah dataset Jawa Timur.
            #
            # Tidak ada kolom province di tabel.
            # Karena itu province Jawa Timur berarti seluruh data.
            # =================================================

            if scope_field == "province":

                normalized_scope = (
                    str(scope_value)
                    .strip()
                    .lower()
                    if scope_value is not None
                    else "jawa timur"
                )

                if normalized_scope not in {
                    "jawa timur",
                    "jatim",
                    "province",
                }:
                    raise ValueError(
                        f"Unsupported province: {scope_value}"
                    )

        cursor = self.get_cursor()

        try:

            conditions = [
                "jumlah_rectifier_obsolete > 0"
            ]

            params = []

            # =================================================
            # NON-PROVINCE SCOPE
            # =================================================

            if (
                scope_field is not None
                and scope_field != "province"
            ):

                conditions.append(
                    f"LOWER(`{scope_field}`) = LOWER(%s)"
                )

                params.append(
                    str(scope_value).strip()
                )

            where_clause = (
                " WHERE "
                + " AND ".join(conditions)
            )

            cursor.execute(
                f"""
                SELECT
                    siteid,
                    site_name,
                    kabupaten,
                    kecamatan,
                    nop_name,
                    cluster,
                    jumlah_rectifier,
                    jumlah_rectifier_non_obsolete,
                    jumlah_rectifier_obsolete,
                    kategori_rectifier
                FROM master_site
                {where_clause}
                ORDER BY
                    jumlah_rectifier_obsolete DESC,
                    siteid
                """,
                tuple(params)
            )

            return cursor.fetchall()

        finally:

            cursor.close()

    # =====================================================
    # RECTIFIER STATISTICS
    # =====================================================

    def get_rectifier_statistics(
        self,
        scope_field=None,
        scope_value=None
    ):
        """
        Return Rectifier statistics for a given scope.

        SITE LEVEL
        ----------
        total_site
        obsolete_site
        non_obsolete_site

        UNIT LEVEL
        ----------
        total_rectifier
        total_non_obsolete
        total_obsolete

        Supported scope:
        - None
        - province
        - siteid
        - kecamatan
        - kabupaten
        - nop_name
        - cluster

        Important:
        kategori_rectifier is used only for SITE classification.

        jumlah_rectifier_obsolete and
        jumlah_rectifier_non_obsolete are used for UNIT counts.
        """

        allowed_scope = {
            "siteid",
            "kecamatan",
            "kabupaten",
            "nop_name",
            "cluster",
            "province",
        }

        if scope_field is not None:

            if scope_field not in allowed_scope:
                raise ValueError(
                    f"Unsupported rectifier scope: {scope_field}"
                )

            # =================================================
            # PROVINCE
            #
            # Seluruh dataset master_site = Jawa Timur.
            # =================================================

            if scope_field == "province":

                normalized_scope = (
                    str(scope_value)
                    .strip()
                    .lower()
                    if scope_value is not None
                    else "jawa timur"
                )

                if normalized_scope not in {
                    "jawa timur",
                    "jatim",
                    "province",
                }:
                    raise ValueError(
                        f"Unsupported province: {scope_value}"
                    )

        cursor = self.get_cursor()

        try:

            conditions = []

            params = []

            # =================================================
            # SCOPE FILTER
            # =================================================

            if (
                scope_field is not None
                and scope_field != "province"
            ):

                conditions.append(
                    f"LOWER(`{scope_field}`) = LOWER(%s)"
                )

                params.append(
                    str(scope_value).strip()
                )

            where_clause = (
                " WHERE "
                + " AND ".join(conditions)
                if conditions
                else ""
            )

            # =================================================
            # STATISTICS
            #
            # Site:
            #   kategori_rectifier
            #
            # Unit:
            #   jumlah_rectifier*
            # =================================================

            cursor.execute(
                f"""
                SELECT

                    COUNT(*) AS total_site,

                    SUM(
                        CASE
                            WHEN kategori_rectifier = 'Obsolete'
                            THEN 1
                            ELSE 0
                        END
                    ) AS obsolete_site,

                    SUM(
                        CASE
                            WHEN kategori_rectifier = 'Non Obsolete'
                            THEN 1
                            ELSE 0
                        END
                    ) AS non_obsolete_site,

                    SUM(
                        COALESCE(
                            jumlah_rectifier,
                            0
                        )
                    ) AS total_rectifier,

                    SUM(
                        COALESCE(
                            jumlah_rectifier_non_obsolete,
                            0
                        )
                    ) AS total_non_obsolete,

                    SUM(
                        COALESCE(
                            jumlah_rectifier_obsolete,
                            0
                        )
                    ) AS total_obsolete

                FROM master_site
                {where_clause}
                """,
                tuple(params)
            )

            row = cursor.fetchone()

            if not row:

                return {
                    "total_site": 0,
                    "obsolete_site": 0,
                    "non_obsolete_site": 0,
                    "total_rectifier": 0,
                    "total_non_obsolete": 0,
                    "total_obsolete": 0,
                }

            return {
                "total_site": (
                    row.get("total_site")
                    or 0
                ),
                "obsolete_site": (
                    row.get("obsolete_site")
                    or 0
                ),
                "non_obsolete_site": (
                    row.get("non_obsolete_site")
                    or 0
                ),
                "total_rectifier": (
                    row.get("total_rectifier")
                    or 0
                ),
                "total_non_obsolete": (
                    row.get("total_non_obsolete")
                    or 0
                ),
                "total_obsolete": (
                    row.get("total_obsolete")
                    or 0
                ),
            }

        finally:

            cursor.close()
                # =====================================================
    # PLN SITE PROFILE
    # =====================================================

    def get_pln_site_profile(
        self,
        siteid,
        tahun=None,
    ):
        """
        Return PLN profile information for one site.

        Profile fields:
        - siteid
        - site_name
        - pelanggan_id
        - nama_pelanggan
        - tower_owner
        - source_power
        - amr
        - daya
        - jenis_inquiry
        - type_tarif
        - schema_bayar
        - tp_nontp

        Location fields remain sourced from master_site
        when needed by higher-level scope queries.
        """

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

                    WHERE LOWER(spm.siteid) = LOWER(%s)

                    ORDER BY spm.tahun DESC

                    LIMIT 1
                    """,
                    (
                        str(siteid).strip(),
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

                    WHERE LOWER(spm.siteid) = LOWER(%s)
                      AND spm.tahun = %s

                    LIMIT 1
                    """,
                    (
                        str(siteid).strip(),
                        tahun,
                    ),
                )

            return cursor.fetchone()

        finally:

            cursor.close()

    # =====================================================
    # PLN MONTHLY HISTORY
    # =====================================================

    def get_pln_monthly(
        self,
        siteid,
        tahun=None,
    ):
        """
        Return complete PLN monthly data for one site.

        Monthly metrics:
        - KWHPAKAI
        - RPTAG

        The raw database values are returned unchanged.
        """

        cursor = self.get_cursor()

        try:

            if tahun is None:

                cursor.execute(
                    """
                    SELECT
                        spm.siteid,
                        ms.site_name,
                        spm.tahun,

                        spm.kwh_januari,
                        spm.rptag_januari,

                        spm.kwh_februari,
                        spm.rptag_februari,

                        spm.kwh_maret,
                        spm.rptag_maret,

                        spm.kwh_april,
                        spm.rptag_april,

                        spm.kwh_mei,
                        spm.rptag_mei,

                        spm.kwh_juni,
                        spm.rptag_juni,

                        spm.kwh_juli,
                        spm.rptag_juli,

                        spm.kwh_agustus,
                        spm.rptag_agustus,

                        spm.kwh_september,
                        spm.rptag_september,

                        spm.kwh_oktober,
                        spm.rptag_oktober,

                        spm.kwh_november,
                        spm.rptag_november,

                        spm.kwh_desember,
                        spm.rptag_desember

                    FROM site_pln_monthly spm

                    LEFT JOIN master_site ms
                        ON ms.siteid = spm.siteid

                    WHERE LOWER(spm.siteid) = LOWER(%s)

                    ORDER BY spm.tahun DESC

                    LIMIT 1
                    """,
                    (
                        str(siteid).strip(),
                    ),
                )

            else:

                cursor.execute(
                    """
                    SELECT
                        spm.siteid,
                        ms.site_name,
                        spm.tahun,

                        spm.kwh_januari,
                        spm.rptag_januari,

                        spm.kwh_februari,
                        spm.rptag_februari,

                        spm.kwh_maret,
                        spm.rptag_maret,

                        spm.kwh_april,
                        spm.rptag_april,

                        spm.kwh_mei,
                        spm.rptag_mei,

                        spm.kwh_juni,
                        spm.rptag_juni,

                        spm.kwh_juli,
                        spm.rptag_juli,

                        spm.kwh_agustus,
                        spm.rptag_agustus,

                        spm.kwh_september,
                        spm.rptag_september,

                        spm.kwh_oktober,
                        spm.rptag_oktober,

                        spm.kwh_november,
                        spm.rptag_november,

                        spm.kwh_desember,
                        spm.rptag_desember

                    FROM site_pln_monthly spm

                    LEFT JOIN master_site ms
                        ON ms.siteid = spm.siteid

                    WHERE LOWER(spm.siteid) = LOWER(%s)
                      AND spm.tahun = %s

                    LIMIT 1
                    """,
                    (
                        str(siteid).strip(),
                        tahun,
                    ),
                )

            return cursor.fetchone()

        finally:

            cursor.close()

    # =====================================================
    # PLN PROFILE + HISTORY
    # =====================================================

    def get_pln_site_data(
        self,
        siteid,
        tahun=None,
    ):
        """
        Return complete PLN data for one site.

        Combines:
        - PLN Site Profile
        - PLN Monthly History
        """

        profile = self.get_pln_site_profile(
            siteid=siteid,
            tahun=tahun,
        )

        if profile is None:
            return None

        monthly = self.get_pln_monthly(
            siteid=siteid,
            tahun=(
                profile.get("tahun")
                if tahun is None
                else tahun
            ),
        )

        result = dict(profile)

        if monthly:
            result.update(
                monthly
            )

        return result

    # =====================================================
    # LITHIUM STATISTIC
    # =====================================================

    def get_lithium_statistics(self):

        cursor = self.get_cursor()

        cursor.execute("""
            SELECT
                SUM(total_lithium) AS total_lithium,
                SUM(total_vrla) AS total_vrla
            FROM master_site
        """)

        row = cursor.fetchone()

        cursor.close()

        return row

    # =====================================================
    # CLUSTER STATISTIC
    # =====================================================

    def get_cluster_statistics(self):

        cursor = self.get_cursor()

        cursor.execute("""
            SELECT
                cluster,
                COUNT(*) AS total_site
            FROM master_site
            GROUP BY cluster
            ORDER BY total_site DESC
        """)

        rows = cursor.fetchall()

        cursor.close()

        return rows

    # =====================================================
    # KABUPATEN STATISTIC
    # =====================================================

    def get_kabupaten_statistics(self):

        cursor = self.get_cursor()

        cursor.execute("""
            SELECT
                kabupaten,
                COUNT(*) AS total_site
            FROM master_site
            GROUP BY kabupaten
            ORDER BY total_site DESC
        """)

        rows = cursor.fetchall()

        cursor.close()

        return rows