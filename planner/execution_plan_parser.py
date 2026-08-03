"""
planner/execution_plan_parser.py

Convert AI JSON response into ExecutionPlan object.
"""

from __future__ import annotations

import json
from typing import Any

from models.execution_plan import (
    ExecutionPlan,
    FilterCondition,
    SortCondition,
)


class ExecutionPlanParser:
    """
    Convert AI JSON response into ExecutionPlan.
    """

    @staticmethod
    def parse(response: str | dict[str, Any]) -> ExecutionPlan:

        if isinstance(response, str):
            try:
                response = json.loads(response)
            except json.JSONDecodeError as exc:
                raise ValueError("Invalid JSON returned by AI.") from exc

        if not isinstance(response, dict):
            raise TypeError("ExecutionPlan response must be a dictionary.")

        filters = [
            FilterCondition(
                field=item["field"],
                operator=item["operator"],
                value=item["value"],
            )
            for item in response.get("filters", [])
        ]

        order_by = [
            SortCondition(
                field=item["field"],
                direction=item.get("direction", "ASC"),
            )
            for item in response.get("order_by", [])
        ]

        return ExecutionPlan(
            module=response["module"],
            operation=response["operation"],
            select=response.get("select", []),
            filters=filters,
            group_by=response.get("group_by", []),
            order_by=order_by,
            limit=response.get("limit"),
            description=response.get("description", ""),
        )