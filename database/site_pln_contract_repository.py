"""
Repository for site_pln_contract.

Data source:
    site_pln_contract

Contract domain:
    siteid
    site_name
    kategori
    no_contract
    end_of_contract
    last_recurring
    preventif_vandalisme

Scope hierarchy:
    siteid
    kecamatan
    kabupaten
    nop
    cluster
    province / union

Architecture:

    site_pln_contract
            |
            | LEFT JOIN
            v
       master_site
            |
            v
    SitePLNContractRepository

Important:
    - Contract adalah domain tersendiri.
    - master_site hanya digunakan sebagai enrichment/reference
      untuk informasi geografis dan organisasi.
    - LEFT JOIN digunakan agar record contract tetap dapat
      ditemukan walaupun site belum tersedia di master_site.
    - last_recurring adalah VARCHAR.
    - preventif_vandalisme adalah VARCHAR.
    - end_of_contract adalah DATE.
"""

from database.base_repository import BaseRepository


class SitePLNContractRepository(BaseRepository):

    # ==========================================================
    # SCOPE COLUMNS
    # ==========================================================

    SCOPE_COLUMNS = {
        "siteid": "c.siteid",
        "kecamatan": "ms.kecamatan",
        "kota": "ms.kabupaten",
        "kabupaten": "ms.kabupaten",
        "city_or_kabupaten": "ms.kabupaten",
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
        "seluruh",
        "all",
    }

    # ==========================================================
    # NORMALIZE SCOPE
    # ==========================================================

    @classmethod
    def normalize_scope(cls, scope_field):

        if scope_field is None:
            return None

        scope = (
            str(scope_field)
            .strip()
            .lower()
        )

        if scope in cls.PROVINCE_SCOPES:
            return "union"

        return scope

    # ==========================================================
    # NORMALIZE SCOPE VALUE
    # ==========================================================

    @staticmethod
    def normalize_scope_value(scope_value):

        if scope_value is None:
            return None

        return (
            str(scope_value)
            .strip()
        )

    @classmethod
    def build_scope_filter(cls, scope_field, scope_value):
        """Return a whitelisted SQL scope clause and bound parameters."""
        scope_column = cls.SCOPE_COLUMNS.get(scope_field)
        if not scope_column:
            raise ValueError(f"Unsupported contract scope: {scope_field}")
        if scope_value is None:
            raise ValueError(f"scope_value is required for scope '{scope_field}'")

        value = cls.normalize_scope_value(scope_value)
        if scope_field == "kota":
            return (
                f"LOWER(TRIM({scope_column})) = CONCAT('kota ', LOWER(TRIM(%s)))",
                (value,),
            )
        if scope_field == "kabupaten":
            return (
                f"(LOWER(TRIM({scope_column})) = LOWER(TRIM(%s)) "
                f"OR LOWER(TRIM({scope_column})) = CONCAT('kabupaten ', LOWER(TRIM(%s))))",
                (value, value),
            )
        if scope_field == "city_or_kabupaten":
            return (
                f"(LOWER(TRIM({scope_column})) = LOWER(TRIM(%s)) "
                f"OR LOWER(TRIM({scope_column})) = CONCAT('kota ', LOWER(TRIM(%s))) "
                f"OR LOWER(TRIM({scope_column})) = CONCAT('kabupaten ', LOWER(TRIM(%s))))",
                (value, value, value),
            )
        return (
            f"LOWER(TRIM({scope_column})) = LOWER(TRIM(%s))",
            (value,),
        )

    # ==========================================================
    # COUNT SITES
    # ==========================================================

    def count_sites(
        self,
        scope_field=None,
        scope_value=None,
    ):
        cursor = self.get_cursor()
        try:
            scope_field = self.normalize_scope(scope_field)
            conditions = ["YEAR(c.end_of_contract) <> 0"]
            params = []

            if scope_field == "union":
                pass
            elif scope_field:
                scope_condition, scope_params = self.build_scope_filter(
                    scope_field, scope_value
                )
                conditions.append(scope_condition)
                params.extend(scope_params)

            where_clause = ""
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)

            cursor.execute(
                f"""
                SELECT COUNT(DISTINCT c.siteid) AS total_site
                FROM site_pln_contract c
                LEFT JOIN master_site ms ON ms.siteid = c.siteid
                {where_clause}
                """,
                tuple(params),
            )
            row = cursor.fetchone() or {}
            return int(row.get("total_site", 0) or 0)
        finally:
            cursor.close()

    # ==========================================================
    # LIST SITES
    #
    # Return contract rows.
    #
    # Default limit digunakan untuk mencegah query terlalu besar.
    # ==========================================================

    def list_sites(
        self,
        scope_field=None,
        scope_value=None,
        limit=100,
        offset=0,
    ):

        cursor = self.get_cursor()

        try:

            scope_field = self.normalize_scope(
                scope_field
            )

            conditions = [
                  "YEAR(c.end_of_contract) <> 0"
              ]
            params = []

            # ==================================================
            # SCOPE
            # ==================================================

            if scope_field == "union":

                pass

            elif scope_field:

                scope_condition, scope_params = self.build_scope_filter(
                    scope_field,
                    scope_value,
                )

                conditions.append(scope_condition)
                params.extend(scope_params)
            # ==================================================
            # WHERE
            # ==================================================

            where_clause = ""

            if conditions:

                where_clause = (
                    "WHERE "
                    + " AND ".join(
                        conditions
                    )
                )

            # ==================================================
            # LIMIT / OFFSET
            # ==================================================

            try:

                limit = int(limit)

            except (
                TypeError,
                ValueError,
            ):

                limit = 100

            try:

                offset = int(offset)

            except (
                TypeError,
                ValueError,
            ):

                offset = 0

            if limit <= 0:
                limit = 100

            if offset < 0:
                offset = 0

            cursor.execute(
                f"""
                SELECT

                    c.siteid,
                    c.site_name,
                    c.kategori,
                    c.no_contract,
                    c.end_of_contract,
                    c.last_recurring,
                    c.preventif_vandalisme,

                    ms.kecamatan,
                    ms.kabupaten,
                    ms.nop_name,
                    ms.cluster

                FROM site_pln_contract c

                LEFT JOIN master_site ms
                    ON ms.siteid = c.siteid

                {where_clause}

                ORDER BY
                    c.siteid

                LIMIT %s
                OFFSET %s
                """,
                tuple(
                    params
                    + [
                        limit,
                        offset,
                    ]
                ),
            )

            return (
                cursor.fetchall()
                or []
            )

        finally:

            cursor.close()

    # ==========================================================
    # SEARCH
    #
    # Search text pada:
    #
    #   siteid
    #   site_name
    #   kategori
    #   no_contract
    #   last_recurring
    #   preventif_vandalisme
    #
    # end_of_contract tidak dicari sebagai text.
    # Untuk EOC gunakan query date khusus di service/repository
    # berikutnya.
    # ==========================================================

    def search(
        self,
        keyword,
        scope_field=None,
        scope_value=None,
        limit=100,
    ):

        if keyword is None:

            keyword = ""

        keyword = (
            str(keyword)
            .strip()
        )

        cursor = self.get_cursor()

        try:

            scope_field = self.normalize_scope(
                scope_field
            )

            conditions = [
                  "YEAR(c.end_of_contract) <> 0"
              ]
            params = []

            # ==================================================
            # TEXT SEARCH
            # ==================================================

            search_columns = (
                "c.siteid",
                "c.site_name",
                "c.kategori",
                "c.no_contract",
                "c.last_recurring",
                "c.preventif_vandalisme",
            )

            text_conditions = []

            for column in search_columns:

                text_conditions.append(
                    f"""
                    LOWER(
                        COALESCE(
                            {column},
                            ''
                        )
                    ) LIKE LOWER(%s)
                    """
                )

                params.append(
                    f"%{keyword}%"
                )

            conditions.append(
                "("
                + " OR ".join(
                    text_conditions
                )
                + ")"
            )

            # ==================================================
            # SCOPE
            # ==================================================

            if scope_field == "union":

                pass

            elif scope_field:

                scope_condition, scope_params = self.build_scope_filter(
                    scope_field,
                    scope_value,
                )

                conditions.append(scope_condition)
                params.extend(scope_params)
            where_clause = (
                "WHERE "
                + " AND ".join(
                    conditions
                )
            )

            try:

                limit = int(limit)

            except (
                TypeError,
                ValueError,
            ):

                limit = 100

            if limit <= 0:
                limit = 100

            cursor.execute(
                f"""
                SELECT

                    c.siteid,
                    c.site_name,
                    c.kategori,
                    c.no_contract,
                    c.end_of_contract,
                    c.last_recurring,
                    c.preventif_vandalisme,

                    ms.kecamatan,
                    ms.kabupaten,
                    ms.nop_name,
                    ms.cluster

                FROM site_pln_contract c

                LEFT JOIN master_site ms
                    ON ms.siteid = c.siteid

                {where_clause}

                ORDER BY
                    c.siteid

                LIMIT %s
                """,
                tuple(
                    params
                    + [limit]
                ),
            )

            return (
                cursor.fetchall()
                or []
            )

        finally:

            cursor.close()

    # ==========================================================
    # QUERY END OF CONTRACT
    #
    # Operator:
    #
    #   <
    #   <=
    #   =
    #   >=
    #   >
    #
    # BETWEEN:
    #
    #   operator = "between"
    #   date_value
    #   date_value_to
    #
    # end_of_contract adalah DATE.
    # ==========================================================

    def count_eoc(
        self,
        operator,
        date_value,
        date_value_to=None,
        scope_field=None,
        scope_value=None,
    ):

        cursor = self.get_cursor()

        try:

            scope_field = self.normalize_scope(
                scope_field
            )

            conditions = [
                "YEAR(c.end_of_contract) <> 0"
            ]

            params = []

            operator = (
                str(operator)
                .strip()
                .lower()
            )

            if operator in (
                "<",
                "<=",
                "=",
                ">",
                ">=",
            ):

                conditions.append(
                    f"""
                    c.end_of_contract {operator} %s
                    """
                )

                params.append(
                    date_value
                )

            elif operator in (
                "between",
                "between_inclusive",
            ):

                if date_value_to is None:

                    raise ValueError(
                        "date_value_to is required "
                        "for EOC BETWEEN"
                    )

                conditions.append(
                    """
                    c.end_of_contract
                    BETWEEN %s AND %s
                    """
                )

                params.extend(
                    [
                        date_value,
                        date_value_to,
                    ]
                )

            else:

                raise ValueError(
                    f"Unsupported EOC operator: "
                    f"{operator}"
                )

            if scope_field == "union":

                pass

            elif scope_field:

                scope_condition, scope_params = self.build_scope_filter(
                    scope_field,
                    scope_value,
                )

                conditions.append(scope_condition)
                params.extend(scope_params)
            where_clause = (
                "WHERE "
                + " AND ".join(
                    conditions
                )
            )

            cursor.execute(
                f"""
                SELECT
                    COUNT(
                        DISTINCT c.siteid
                    ) AS total_count

                FROM site_pln_contract c

                LEFT JOIN master_site ms
                    ON ms.siteid = c.siteid

                {where_clause}
                """,
                tuple(params),
            )

            row = cursor.fetchone()

            if not row:
                return 0

            return int(
                row["total_count"]
            )

        finally:

            cursor.close()
    def query_eoc(
        self,
        operator,
        date_value,
        date_value_to=None,
        scope_field=None,
        scope_value=None,
        limit=100,
    ):

        cursor = self.get_cursor()

        try:

            scope_field = self.normalize_scope(
                scope_field
            )

            conditions = [
                  "YEAR(c.end_of_contract) <> 0"
              ]
            params = []

            # ==================================================
            # EOC CONDITION
            # ==================================================

            operator = (
                str(operator)
                .strip()
                .lower()
            )

            if operator in (
                "<",
                "<=",
                "=",
                ">",
                ">=",
            ):

                conditions.append(
                    f"""
                    c.end_of_contract {operator} %s
                    """
                )

                params.append(
                    date_value
                )

            elif operator in (
                "between",
                "between_inclusive",
            ):

                if date_value_to is None:

                    raise ValueError(
                        "date_value_to is required "
                        "for EOC BETWEEN"
                    )

                conditions.append(
                    """
                    c.end_of_contract
                    BETWEEN %s AND %s
                    """
                )

                params.extend(
                    [
                        date_value,
                        date_value_to,
                    ]
                )

            else:

                raise ValueError(
                    f"Unsupported EOC operator: "
                    f"{operator}"
                )

            # ==================================================
            # SCOPE
            # ==================================================

            if scope_field == "union":

                pass

            elif scope_field:

                scope_condition, scope_params = self.build_scope_filter(
                    scope_field,
                    scope_value,
                )

                conditions.append(scope_condition)
                params.extend(scope_params)
            # ==================================================
            # WHERE
            # ==================================================

            where_clause = (
                "WHERE "
                + " AND ".join(
                    conditions
                )
            )

            # ==================================================
            # LIMIT
            # ==================================================

            try:

                limit = int(limit)

            except (
                TypeError,
                ValueError,
            ):

                limit = 100

            if limit <= 0:

                limit = 100

            # ==================================================
            # QUERY
            # ==================================================

            cursor.execute(
                f"""
                SELECT

                    c.siteid,
                    c.site_name,
                    c.kategori,
                    c.no_contract,
                    c.end_of_contract,
                    c.last_recurring,
                    c.preventif_vandalisme,

                    ms.kecamatan,
                    ms.kabupaten,
                    ms.nop_name,
                    ms.cluster

                FROM site_pln_contract c

                LEFT JOIN master_site ms
                    ON ms.siteid = c.siteid

                {where_clause}

                ORDER BY
                    c.end_of_contract ASC,
                    c.siteid

                LIMIT %s
                """,
                tuple(
                    params
                    + [limit]
                ),
            )

            return (
                cursor.fetchall()
                or []
            )

        finally:

            cursor.close()

    # ==========================================================
    # COUNT BY SCOPE
    #
    # Example:
    #
    #   count_by_scope("kabupaten")
    #
    # Result:
    #
    #   [
    #       {
    #           "scope_value": "...",
    #           "total_site": 123
    #       }
    #   ]
    #
    # Contract tanpa master_site tidak mempunyai informasi
    # geografis sehingga tidak masuk grouping geography.
    # ==========================================================


    # ==========================================================
    # QUERY CONTRACT FIELD
    #
    # Deterministic exact-match query untuk field contract:
    #   - kategori
    #   - no_contract
    #   - last_recurring
    #   - preventif_vandalisme
    # ==========================================================

    def query_field(
        self,
        field,
        value,
        scope_field=None,
        scope_value=None,
        limit=100,
    ):

        allowed_fields = {
            "kategori": "c.kategori",
            "no_contract": "c.no_contract",
            "last_recurring": "c.last_recurring",
            "preventif_vandalisme": "c.preventif_vandalisme",
        }

        field = str(field or "").strip().lower()

        if field not in allowed_fields:
            raise ValueError(
                f"Unsupported contract field: {field}"
            )

        if value is None:
            raise ValueError(
                f"Value is required for contract field: {field}"
            )

        value = str(value).strip()

        if not value:
            raise ValueError(
                f"Value cannot be empty for contract field: {field}"
            )

        scope_field = self.normalize_scope(scope_field)

        cursor = self.get_cursor()

        try:

            conditions = [
                f"LOWER({allowed_fields[field]}) = LOWER(%s)"
            ]

            params = [value]

            if scope_field == "union":

                pass

            elif scope_field:

                scope_condition, scope_params = self.build_scope_filter(
                    scope_field,
                    scope_value,
                )

                conditions.append(scope_condition)
                params.extend(scope_params)
            where_clause = (
                "WHERE "
                + " AND ".join(conditions)
            )

            try:
                limit = int(limit)
            except (
                TypeError,
                ValueError,
            ):
                limit = 100

            if limit <= 0:
                limit = 100

            limit = min(limit, 500)

            cursor.execute(
                f"""
                SELECT
                    c.siteid,
                    c.site_name,
                    c.kategori,
                    c.no_contract,
                    c.end_of_contract,
                    c.last_recurring,
                    c.preventif_vandalisme,

                    ms.kecamatan,
                    ms.kabupaten,
                    ms.nop_name,
                    ms.cluster

                FROM site_pln_contract c

                LEFT JOIN master_site ms
                    ON ms.siteid = c.siteid

                {where_clause}

                ORDER BY
                    c.siteid

                LIMIT %s
                """,
                tuple(
                    params + [limit]
                ),
            )

            return (
                cursor.fetchall()
                or []
            )

        finally:

            cursor.close()

    def count_by_scope(
        self,
        scope_field,
    ):

        scope_field = self.normalize_scope(
            scope_field
        )

        if scope_field == "union":

            cursor = self.get_cursor()

            try:

                cursor.execute(
                    """
                    SELECT
                        COUNT(
                            DISTINCT c.siteid
                        ) AS total_site

                    FROM site_pln_contract c
                    """
                )

                row = (
                    cursor.fetchone()
                    or {}
                )

                return [
                    {
                        "scope_value": (
                            "Jawa Timur"
                        ),
                        "total_site": int(
                            row.get(
                                "total_site",
                                0,
                            )
                            or 0
                        ),
                    }
                ]

            finally:

                cursor.close()

        scope_column = (
            self.SCOPE_COLUMNS.get(
                scope_field
            )
        )

        if not scope_column:

            raise ValueError(
                f"Unsupported contract scope: "
                f"{scope_field}"
            )

        cursor = self.get_cursor()

        try:

            cursor.execute(
                f"""
                SELECT

                    {scope_column}
                        AS scope_value,

                    COUNT(
                        DISTINCT c.siteid
                    ) AS total_site

                FROM site_pln_contract c

                LEFT JOIN master_site ms
                    ON ms.siteid = c.siteid

                WHERE {scope_column} IS NOT NULL

                GROUP BY
                    {scope_column}

                ORDER BY
                    total_site DESC,
                    scope_value
                """
            )

            rows = (
                cursor.fetchall()
                or []
            )

            return rows

        finally:

            cursor.close()





