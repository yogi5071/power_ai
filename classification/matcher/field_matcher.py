"""
classification/matcher/field_matcher.py
"""

from __future__ import annotations

from metadata.context import MetadataContext
from metadata.base import FieldMetadata


class FieldMatcher:

    @staticmethod
    def get_fields(
        context: MetadataContext
    ) -> list[FieldMetadata]:

        return list(
            context.table.fields.values()
        )
        