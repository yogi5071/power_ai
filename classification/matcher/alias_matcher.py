"""
classification/matcher/alias_matcher.py
"""

from __future__ import annotations

from classification.classification_item import ClassificationItem
from classification.matcher.confidence import Confidence
from classification.matcher.utils import token_equals

from metadata.context import MetadataContext


class AliasMatcher:

    @classmethod
    def match(
        cls,
        token: str,
        context: MetadataContext
    ) -> ClassificationItem | None:

        for field in context.table.fields.values():

            aliases = field.aliases or {}

            for alias, real_value in aliases.items():

                if token_equals(token, alias):

                    return ClassificationItem(

                        field=field.name,

                        value=real_value,

                        confidence=Confidence.ALIAS

                    )

        return None