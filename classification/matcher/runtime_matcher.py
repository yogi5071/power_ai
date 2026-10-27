"""
classification/matcher/runtime_matcher.py
"""

from __future__ import annotations

from classification.classification_item import ClassificationItem
from classification.matcher.confidence import Confidence
from classification.matcher.utils import token_equals

from metadata.context import MetadataContext


class RuntimeMatcher:

    @classmethod
    def match(
        cls,
        token: str,
        context: MetadataContext
    ) -> ClassificationItem | None:

        runtime = context.runtime.export()

        for field_name, values in runtime.items():

            for value in values:

                if token_equals(token, str(value)):

                    return ClassificationItem(

                        field=field_name,

                        value=str(value),

                        confidence=Confidence.RUNTIME

                    )

        return None