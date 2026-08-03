"""
metadata/runtime.py

Runtime metadata storage.

Berisi seluruh value dinamis yang diambil dari database.
Contoh:

site_id
kabupaten
cluster
vendor
nop
technology
dll.

Class ini TIDAK mengetahui database.
Ia hanya menjadi container runtime metadata.
"""

from __future__ import annotations


class MetadataRuntime:

    def __init__(self):

        self.clear()

    # =====================================================
    # Clear
    # =====================================================

    def clear(self) -> None:

        self._values: dict[str, list] = {}

    # =====================================================
    # Set Values
    # =====================================================

    def set_values(
        self,
        field_name: str,
        values: list
    ) -> None:

        unique = []

        seen = set()

        for value in values:

            if value is None:
                continue

            if value in seen:
                continue

            seen.add(value)

            unique.append(value)

        self._values[field_name] = unique

    # =====================================================
    # Get Values
    # =====================================================

    def get_values(
        self,
        field_name: str
    ) -> list:

        return self._values.get(
            field_name,
            []
        )

    # =====================================================
    # Has Field
    # =====================================================

    def has(
        self,
        field_name: str
    ) -> bool:

        return field_name in self._values

    # =====================================================
    # Contains Value
    # =====================================================

    def contains(
        self,
        field_name: str,
        value
    ) -> bool:

        return value in self.get_values(
            field_name
        )

    # =====================================================
    # Fields
    # =====================================================

    def fields(
        self
    ) -> list[str]:

        return list(
            self._values.keys()
        )

    # =====================================================
    # Export
    # =====================================================

    def export(
        self
    ) -> dict:

        return dict(
            self._values
        )

    # =====================================================
    # Length
    # =====================================================

    def __len__(
        self
    ) -> int:

        return len(
            self._values
        )

    # =====================================================
    # Contains
    # =====================================================

    def __contains__(
        self,
        field_name: str
    ) -> bool:

        return self.has(
            field_name
        )

    # =====================================================
    # String
    # =====================================================

    def __repr__(
        self
    ) -> str:

        return (
            f"MetadataRuntime("
            f"{len(self._values)} fields)"
        )