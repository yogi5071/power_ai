"""
planner/validator.py

Validate ExecutionPlan
against metadata definition.
"""

from __future__ import annotations

from metadata.master_site import MASTER_SITE

from models.execution_plan import ExecutionPlan

from exceptions.validation_error import ValidationError


class ExecutionPlanValidator:

    """
    Validate ExecutionPlan.
    """

    VALID_MODULES = {

        "battery",
        "alarm",
        "rectifier",
        "power",

    }

    VALID_OPERATIONS = {

        "list",
        "count",
        "summary",
        "aggregate",

    }

    @classmethod
    def validate(
        cls,
        plan: ExecutionPlan
    ) -> ExecutionPlan:

        cls.validate_module(plan)

        cls.validate_operation(plan)

        cls.validate_select(plan)

        cls.validate_filters(plan)

        cls.validate_group_by(plan)

        cls.validate_order_by(plan)

        return plan

    @classmethod
    def validate_module(
        cls,
        plan: ExecutionPlan
    ):

        if plan.module not in cls.VALID_MODULES:

            raise ValidationError(

                f"Unknown module: {plan.module}"

            )

    @classmethod
    def validate_operation(
        cls,
        plan: ExecutionPlan
    ):

        if plan.operation not in cls.VALID_OPERATIONS:

            raise ValidationError(

                f"Unknown operation: {plan.operation}"

            )

    @classmethod
    def validate_select(
        cls,
        plan: ExecutionPlan
    ):

        for field in plan.select:

            if not MASTER_SITE.has(field):

                raise ValidationError(

                    f"Unknown select field: {field}"

                )

    @classmethod
    def validate_filters(
        cls,
        plan: ExecutionPlan
    ):

        for condition in plan.filters:

            if not MASTER_SITE.has(

                condition.field

            ):

                raise ValidationError(

                    f"Unknown filter field: "

                    f"{condition.field}"

                )

            allowed = MASTER_SITE.get_allowed_operators(

                condition.field

            )

            if allowed:

                if condition.operator not in allowed:

                    raise ValidationError(

                        f"Operator "

                        f"{condition.operator}"

                        f" is not allowed "

                        f"for "

                        f"{condition.field}"

                    )

            condition.value = MASTER_SITE.find_value_alias(

                condition.field,

                condition.value

            )

            allowed_values = MASTER_SITE.get_allowed_values(

                condition.field

            )

            if allowed_values:

                if condition.value not in allowed_values:

                    raise ValidationError(

                        f"Invalid value "

                        f"{condition.value}"

                        f" for "

                        f"{condition.field}"

                    )

    @classmethod
    def validate_group_by(
        cls,
        plan: ExecutionPlan
    ):

        for field in plan.group_by:

            if not MASTER_SITE.has(field):

                raise ValidationError(

                    f"Unknown group_by field: "

                    f"{field}"

                )

    @classmethod
    def validate_order_by(
        cls,
        plan: ExecutionPlan
    ):

        for sort in plan.order_by:

            if not MASTER_SITE.has(sort.field):

                raise ValidationError(

                    f"Unknown order_by field: "

                    f"{sort.field}"

                )

            direction = sort.direction.upper()

            if direction not in {

                "ASC",

                "DESC"

            }:

                raise ValidationError(

                    f"Unknown sort direction: "

                    f"{sort.direction}"

                )

            sort.direction = direction