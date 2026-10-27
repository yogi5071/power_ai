"""
query/base_builder.py

Base class for all SQL builders.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from models.execution_plan import ExecutionPlan


class BaseSQLBuilder(ABC):
    """
    Base SQL Builder.

    Every table-specific builder must inherit this class.
    """

    @classmethod
    def build(cls, plan: ExecutionPlan) -> str:
        """
        Build SQL query.
        """

        sql = [
            cls.build_select(plan),
            cls.build_from(plan),
        ]

        where_clause = cls.build_where(plan)
        if where_clause:
            sql.append(where_clause)

        group_clause = cls.build_group_by(plan)
        if group_clause:
            sql.append(group_clause)

        order_clause = cls.build_order_by(plan)
        if order_clause:
            sql.append(order_clause)

        limit_clause = cls.build_limit(plan)
        if limit_clause:
            sql.append(limit_clause)

        return "\n".join(sql) + ";"

    @staticmethod
    @abstractmethod
    def build_select(plan: ExecutionPlan) -> str:
        """Build SELECT clause."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def build_from(plan: ExecutionPlan) -> str:
        """Build FROM clause."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def build_where(plan: ExecutionPlan) -> str:
        """Build WHERE clause."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def build_group_by(plan: ExecutionPlan) -> str:
        """Build GROUP BY clause."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def build_order_by(plan: ExecutionPlan) -> str:
        """Build ORDER BY clause."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def build_limit(plan: ExecutionPlan) -> str:
        """Build LIMIT clause."""
        raise NotImplementedError