"""
query/sql_formatter.py

Utility functions for formatting SQL values.
"""

from __future__ import annotations

from typing import Any

from models.execution_plan import FilterCondition


class SQLFormatter:
    """
    Helper for formatting SQL clauses.
    """

    @staticmethod
    def format_filter(condition: FilterCondition) -> str:
        """
        Convert FilterCondition into SQL expression.

        Example:
            jenis_battery = 'VRLA'
        """

        value = SQLFormatter.format_value(condition.value)

        return (
            f"{condition.field} "
            f"{condition.operator} "
            f"{value}"
        )

    @staticmethod
    def format_value(value: Any) -> str:
        """
        Convert Python value to SQL literal.
        """

        if value is None:
            return "NULL"

        if isinstance(value, bool):
            return "TRUE" if value else "FALSE"

        if isinstance(value, (int, float)):
            return str(value)

        value = str(value).replace("'", "''")

        return f"'{value}'"