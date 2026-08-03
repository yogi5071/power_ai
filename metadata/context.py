"""
metadata/context.py

Metadata Context

Menggabungkan metadata statis (TableMetadata)
dan metadata runtime (MetadataRuntime)
menjadi satu object yang digunakan oleh
seluruh Power AI Copilot.

Architecture

MetadataManager
        │
        ▼
MetadataContext
        ├── table
        └── runtime

ClassificationEngine
Planner
SQL Builder
Validator
"""

from __future__ import annotations

from dataclasses import dataclass

from metadata.base import TableMetadata
from metadata.runtime import MetadataRuntime


@dataclass(slots=True)
class MetadataContext:
    """
    Container yang menggabungkan metadata statis
    dan metadata runtime.

    Attributes
    ----------
    table:
        Definisi metadata statis.

    runtime:
        Nilai metadata hasil load dari database.
    """

    table: TableMetadata

    runtime: MetadataRuntime

    # =====================================================
    # Shortcut
    # =====================================================

    @property
    def table_metadata(
        self
    ) -> TableMetadata:

        return self.table

    @property
    def runtime_metadata(
        self
    ) -> MetadataRuntime:

        return self.runtime

    # =====================================================
    # Runtime Helpers
    # =====================================================

    def runtime_fields(
        self
    ) -> list[str]:

        return self.runtime.fields()

    def runtime_values(
        self,
        field_name: str
    ) -> list:

        return self.runtime.get_values(
            field_name
        )

    # =====================================================
    # Table Helpers
    # =====================================================

    def fields(
        self
    ):

        return self.table.iter_fields()

    def get_field(
        self,
        field_name: str
    ):

        return self.table.get(
            field_name
        )

    def get_aliases(
        self,
        field_name: str
    ) -> dict:

        return self.table.get_aliases(
            field_name
        )

    # =====================================================
    # Debug
    # =====================================================

    def export(self) -> dict:

        return {

            "table": self.table.export_for_ai(),

            "runtime": self.runtime.export()

        }

    def __repr__(self) -> str:

        return (

            f"MetadataContext("
            f"fields={len(self.runtime)}, "
            f"table='{self.table.name}')"

        )