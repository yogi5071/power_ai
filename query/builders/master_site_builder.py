"""
query/builders/master_site_builder.py

SQL Builder for master_site table.
"""

from __future__ import annotations

from metadata.modules import MODULE_TABLES

from models.execution_plan import ExecutionPlan

from query.base_builder import BaseSQLBuilder
from query.sql_formatter import SQLFormatter


class MasterSiteBuilder(BaseSQLBuilder):
    """
    SQL Builder for master_site table.
    """

    @staticmethod
    def build_select(plan: ExecutionPlan) -> str:
        """
        Build SELECT clause.
        """

        if not plan.select:
            return "SELECT *"

        columns = ",\n    ".join(plan.select)

        return (
            "SELECT\n"
            f"    {columns}"
        )

    @staticmethod
    def build_from(plan: ExecutionPlan) -> str:
        """
        Build FROM clause.
        """

        metadata = MODULE_TABLES[plan.module]

        return f"FROM {metadata.table_name}"

    @staticmethod
    def build_where(plan: ExecutionPlan) -> str:
        """
        Build WHERE clause.
        """

        if not plan.filters:
            return ""

        conditions = []

        for condition in plan.filters:
            conditions.append(
                SQLFormatter.format_filter(condition)
            )

        return (
            "WHERE\n    "
            + "\n    AND ".join(conditions)
        )

    @staticmethod
    def build_group_by(plan: ExecutionPlan) -> str:
        """
        Build GROUP BY clause.
        """

        if not plan.group_by:
            return ""

        return (
            "GROUP BY\n    "
            + ", ".join(plan.group_by)
        )

    @staticmethod
    def build_order_by(plan: ExecutionPlan) -> str:
        """
        Build ORDER BY clause.
        """

        if not plan.order_by:
            return ""

        ordering = []

        for item in plan.order_by:
            ordering.append(
                f"{item.field} {item.direction}"
            )

        return (
            "ORDER BY\n    "
            + ", ".join(ordering)
        )

    @staticmethod
    def build_limit(plan: ExecutionPlan) -> str:
        """
        Build LIMIT clause.
        """

        if plan.limit is None:
            return ""

        return f"LIMIT {plan.limit}"