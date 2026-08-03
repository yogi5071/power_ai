"""
metadata/base.py

Base metadata definition for Power AI Copilot.

This module defines structured metadata objects
used by Planner, Validator, Query Builder,
Classification Engine,
and AI reasoning layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterator, Optional


# ==========================================================
# Field Metadata
# ==========================================================

@dataclass(frozen=True)
class FieldMetadata:
    """
    Metadata untuk satu field database.
    """

    name: str

    label: str

    column: str

    data_type: str

    operators: list[str] = field(default_factory=list)

    values: Optional[list[Any]] = None

    aliases: dict[str, list[str]] = field(default_factory=dict)

    unit: Optional[str] = None

    description: str = ""

    nullable: bool = True

    # ------------------------------------------------------

    def export_for_ai(self) -> dict[str, Any]:

        return {

            "name": self.name,

            "label": self.label,

            "column": self.column,

            "data_type": self.data_type,

            "operators": self.operators,

            "values": self.values,

            "aliases": self.aliases,

            "unit": self.unit,

            "description": self.description,

            "nullable": self.nullable,

        }


# ==========================================================
# Table Metadata
# ==========================================================

@dataclass(frozen=True)
class TableMetadata:
    """
    Metadata satu tabel database.
    """

    table_name: str

    fields: dict[str, FieldMetadata]

    primary_key: str

    description: str = ""

    # ======================================================
    # Basic
    # ======================================================

    def get(
        self,
        name: str
    ) -> FieldMetadata:

        return self.fields[name]

    def has(
        self,
        name: str
    ) -> bool:

        return name in self.fields

    def all_fields(
        self
    ) -> list[str]:

        return list(
            self.fields.keys()
        )

    # ======================================================
    # Iterator
    # ======================================================

    def iter_fields(
        self
    ) -> Iterator[FieldMetadata]:

        return iter(
            self.fields.values()
        )

    # ======================================================
    # Values
    # ======================================================

    def get_allowed_values(
        self,
        field_name: str
    ) -> list[Any]:

        if not self.has(field_name):

            return []

        values = self.get(
            field_name
        ).values

        return values or []

    # ======================================================
    # Operators
    # ======================================================

    def get_allowed_operators(
        self,
        field_name: str
    ) -> list[str]:

        if not self.has(field_name):

            return []

        return self.get(
            field_name
        ).operators

    # ======================================================
    # Aliases
    # ======================================================

    def get_aliases(
        self,
        field_name: str
    ) -> dict[str, list[str]]:

        if not self.has(field_name):

            return {}

        aliases = self.get(
            field_name
        ).aliases

        return aliases or {}

    # ======================================================
    # Normalize Alias
    # ======================================================

    def find_value_alias(
        self,
        field_name: str,
        user_value: Any
    ) -> Any:

        if not self.has(field_name):

            return user_value

        if not isinstance(
            user_value,
            str
        ):

            return user_value

        aliases = self.get_aliases(
            field_name
        )

        normalized = (
            user_value
            .lower()
            .strip()
        )

        for real_value, alias_list in aliases.items():

            if normalized == real_value.lower():

                return real_value

            for alias in alias_list:

                if normalized == alias.lower().strip():

                    return real_value

        return user_value

    # ======================================================
    # Search
    # ======================================================

    def find_field_by_column(
        self,
        column: str
    ) -> FieldMetadata | None:

        for field in self.iter_fields():

            if field.column == column:

                return field

        return None

    # ======================================================
    # Export
    # ======================================================

    def export_for_ai(
        self
    ) -> dict[str, Any]:

        return {

            "table_name": self.table_name,

            "primary_key": self.primary_key,

            "description": self.description,

            "fields": {

                name: field.export_for_ai()

                for name, field

                in self.fields.items()

            }

        }

    # ======================================================
    # Debug
    # ======================================================

    def __len__(
        self
    ) -> int:

        return len(
            self.fields
        )

    def __contains__(
        self,
        item: str
    ) -> bool:

        return self.has(
            item
        )

    def __repr__(
        self
    ) -> str:

        return (

            f"TableMetadata("
            f"table='{self.table_name}', "
            f"fields={len(self.fields)})"

        )