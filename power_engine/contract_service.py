"""
Contract Service.

Purpose:
    Service layer untuk menjalankan deterministic Contract queries.

Architecture:

    User Question
        â†“
    Entity / Intent Extraction
        â†“
    ContractService
        â†“
    SitePLNContractRepository
        â†“
    MySQL
        â†“
    Query Result

IMPORTANT:
    Service ini tidak menentukan hasil berdasarkan AI.

    AI hanya memberikan parameter seperti:

        keyword
        scope_field
        scope_value
        limit

    Repository yang menentukan hasil berdasarkan database.
"""

from datetime import date

from database.site_pln_contract_repository import (
    SitePLNContractRepository,
)


class ContractService:

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    def __init__(self):

        self.repository = SitePLNContractRepository()

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
                f"Invalid Contract limit: {limit}"
            )

        if limit <= 0:

            return 100

        return min(
            limit,
            500,
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
                scope_value
            )
        )

        return (
            scope_field,
            scope_value,
        )

    # ==========================================================
    # NORMALIZE KEYWORD
    # ==========================================================

    @staticmethod
    def normalize_keyword(keyword=None):

        if keyword is None:

            return None

        keyword = str(keyword).strip()

        if not keyword:

            return None

        return keyword

    # ==========================================================
    # GET SITE PROFILE
    # ==========================================================

    def get_site_profile(
        self,
        siteid,
    ):

        if siteid is None:

            raise ValueError(
                "Contract siteid cannot be None"
            )

        siteid = str(siteid).strip()

        if not siteid:

            raise ValueError(
                "Contract siteid cannot be empty"
            )

        return (
            self.repository.get_site_profile(
                siteid
            )
        )

    # ==========================================================
    # COUNT SITES
    # ==========================================================

    def count_sites(
        self,
        scope_field=None,
        scope_value=None,
    ):

        (
            scope_field,
            scope_value,
        ) = self.normalize_scope(
            scope_field,
            scope_value,
        )

        total_count = (
            self.repository.count_sites(
                scope_field=scope_field,
                scope_value=scope_value,
            )
        )

        return {
            "query_type": "contract_count",

            "scope_field": scope_field,

            "scope_value": scope_value,

            "count": total_count,

            "total_count": total_count,
        }

    # ==========================================================
    # LIST SITES
    # ==========================================================

    def list_sites(
        self,
        scope_field=None,
        scope_value=None,
        limit=100,
    ):

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
            self.repository.list_sites(
                scope_field=scope_field,
                scope_value=scope_value,
                limit=limit,
            )
        )

        total_count = (
            self.repository.count_sites(
                scope_field=scope_field,
                scope_value=scope_value,
            )
        )

        return {
            "query_type": "contract_list",

            "scope_field": scope_field,

            "scope_value": scope_value,

            "count": total_count,

            "total_count": total_count,

            "sampling_count": len(rows),

            "limit": limit,

            "rows": rows,
        }

    # ==========================================================
    # SEARCH
    # ==========================================================

    def search(
        self,
        keyword=None,
        scope_field=None,
        scope_value=None,
        limit=100,
    ):

        keyword = (
            self.normalize_keyword(
                keyword
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
            self.repository.search(
                keyword=keyword,
                scope_field=scope_field,
                scope_value=scope_value,
                limit=limit,
            )
        )

        return {
            "query_type": "contract_search",

            "keyword": keyword,

            "scope_field": scope_field,

            "scope_value": scope_value,

            "count": len(rows),

            "sampling_count": len(rows),

            "limit": limit,

            "rows": rows,
        }

    # ==========================================================
    # COUNT BY SCOPE
    # ==========================================================


    # ==========================================================
    # QUERY CONTRACT FIELD
    #
    # Deterministic exact-match query:
    #   kategori
    #   no_contract
    #   last_recurring
    #   preventif_vandalisme
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
            "kategori",
            "no_contract",
            "last_recurring",
            "preventif_vandalisme",
        }

        field = str(field or "").strip().lower()

        if field not in allowed_fields:
            raise ValueError(
                f"Unsupported contract field: {field}"
            )

        value = self.normalize_keyword(value)

        if value is None:
            raise ValueError(
                f"Value is required for contract field: {field}"
            )

        (
            scope_field,
            scope_value,
        ) = self.normalize_scope(
            scope_field,
            scope_value,
        )

        limit = self.normalize_limit(limit)

        rows = self.repository.query_field(
            field=field,
            value=value,
            scope_field=scope_field,
            scope_value=scope_value,
            limit=limit,
        )

        return {
            "query_type": "contract_field",
            "field": field,
            "value": value,
            "scope_field": scope_field,
            "scope_value": scope_value,
            "count": len(rows),
            "total_count": len(rows),
            "sampling_count": len(rows),
            "limit": limit,
            "rows": rows,
        }

    def query_eoc(
        self,
        operator,
        date_value,
        date_value_to=None,
        scope_field=None,
        scope_value=None,
        limit=100,
    ):
        operator = str(operator).strip().lower()

        allowed_operators = {
            "<",
            "<=",
            "=",
            ">",
            ">=",
            "between",
            "between_inclusive",
        }

        if operator not in allowed_operators:
            raise ValueError(
                f"Unsupported EOC operator: {operator}"
            )

        def normalize_date(value, field_name):
            if value is None:
                raise ValueError(
                    f"{field_name} is required"
                )

            value = str(value).strip()

            try:
                from datetime import date

                return date.fromisoformat(value).isoformat()

            except (TypeError, ValueError):
                raise ValueError(
                    f"Invalid EOC date for {field_name}: {value}"
                )

        date_value = normalize_date(
            date_value,
            "date_value",
        )

        if operator in (
            "between",
            "between_inclusive",
        ):
            date_value_to = normalize_date(
                date_value_to,
                "date_value_to",
            )
        else:
            date_value_to = None

        scope_field, scope_value = self.normalize_scope(
            scope_field,
            scope_value,
        )

        limit = self.normalize_limit(limit)

        total_count = self.repository.count_eoc(
            operator=operator,
            date_value=date_value,
            date_value_to=date_value_to,
            scope_field=scope_field,
            scope_value=scope_value,
        )

        rows = self.repository.query_eoc(
            operator=operator,
            date_value=date_value,
            date_value_to=date_value_to,
            scope_field=scope_field,
            scope_value=scope_value,
            limit=limit,
        )

        return {
            "query_type": "eoc",
            "operator": operator,
            "date_from": date_value,
            "date_to": date_value_to,
            "scope_field": scope_field,
            "scope_value": scope_value,
            "count": total_count,
            "total_count": total_count,
            "sampling_count": len(rows),
            "limit": limit,
            "rows": rows,
        }
    def count_by_scope(
        self,
        scope_field,
        scope_value=None,
    ):

        (
            scope_field,
            scope_value,
        ) = self.normalize_scope(
            scope_field,
            scope_value,
        )

        rows = (
            self.repository.count_by_scope(
                scope_field=scope_field,
                scope_value=scope_value,
            )
        )

        return {
            "query_type": "contract_count_by_scope",

            "scope_field": scope_field,

            "scope_value": scope_value,

            "count": len(rows),

            "rows": rows,
        }


