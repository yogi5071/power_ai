"""
metadata/manager.py

Metadata Manager

Central manager untuk seluruh metadata Power AI Copilot.

Responsibilities
----------------
- Load metadata module
- Menyimpan MetadataContext
- Memberikan MetadataContext kepada service lain
"""

from __future__ import annotations

from metadata.context import MetadataContext
from metadata.loader import MetadataLoader
from metadata.modules import MODULE_TABLES


class MetadataManager:

    def __init__(self):

        self.loader = MetadataLoader()

        self.contexts: dict[str, MetadataContext] = {}

    # =====================================================
    # Load
    # =====================================================

    def load_module(
        self,
        module_name: str
    ) -> None:

        if module_name not in MODULE_TABLES:
            raise KeyError(
                f"Unknown metadata module: {module_name}"
            )

        table_metadata = MODULE_TABLES[module_name]

        context = self.loader.load(
            table_metadata
        )

        self.contexts[module_name] = context

    # =====================================================
    # Load All
    # =====================================================

    def load_all(self) -> None:

        for module_name in MODULE_TABLES.keys():

            self.load_module(module_name)

    # =====================================================
    # Get Context
    # =====================================================

    def get_context(
        self,
        module_name: str
    ) -> MetadataContext:

        if module_name not in self.contexts:

            raise RuntimeError(

                f"Metadata module '{module_name}' has not been loaded."

            )

        return self.contexts[module_name]

    # =====================================================
    # Reload
    # =====================================================

    def reload(
        self,
        module_name: str
    ) -> None:

        self.load_module(module_name)

    # =====================================================
    # Clear
    # =====================================================

    def clear(self) -> None:

        self.contexts.clear()