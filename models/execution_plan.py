"""
models/execution_plan.py

Data model untuk komunikasi antara:

Gemini Planner
        |
        v
Query Builder
        |
        v
Repository

Power AI Copilot
"""


from dataclasses import dataclass, field
from typing import Any, Optional



@dataclass
class FilterCondition:
    """
    Representasi satu kondisi filter.

    Contoh:

    kabupaten = Probolinggo

    atau

    umur_battery > 8
    """

    field: str

    operator: str

    value: Any



@dataclass
class SortCondition:
    """
    Representasi sorting.

    Contoh:

    umur_battery DESC
    """

    field: str

    direction: str = "ASC"



@dataclass
class ExecutionPlan:
    """
    Rencana eksekusi query.

    Object ini menjadi bahasa
    antara AI dan database.
    """


    # Module tujuan
    # contoh:
    # battery
    # alarm
    # rectifier

    module: str


    # Operasi yang dilakukan

    # contoh:
    # count
    # list
    # summary
    # aggregate

    operation: str



    # Field yang ingin diambil

    select: list[str] = field(
        default_factory=list
    )



    # Filter kondisi

    filters: list[FilterCondition] = field(
        default_factory=list
    )



    # Grouping

    group_by: list[str] = field(
        default_factory=list
    )



    # Sorting

    order_by: list[SortCondition] = field(
        default_factory=list
    )



    # Limit data

    limit: Optional[int] = None



    # Metadata tambahan

    description: str = ""



    def add_filter(
        self,
        field_name: str,
        operator: str,
        value: Any
    ):
        """
        Menambahkan filter baru.
        """

        self.filters.append(

            FilterCondition(
                field=field_name,
                operator=operator,
                value=value
            )

        )



    def get_filter(
        self,
        field_name: str
    ):
        """
        Mengambil filter berdasarkan field.
        """

        for item in self.filters:

            if item.field == field_name:

                return item


        return None



    def has_filter(
        self,
        field_name: str
    ) -> bool:
        """
        Mengecek apakah filter tersedia.
        """

        return (
            self.get_filter(field_name)
            is not None
        )