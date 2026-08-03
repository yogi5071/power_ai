"""
metadata/loader.py
"""

from metadata.runtime import MetadataRuntime
from metadata.repository import MetadataRepository


class MetadataLoader:

    def __init__(self):

        self.runtime = MetadataRuntime()

        self.repository = MetadataRepository()

    def load(
        self,
        table_metadata
    ):

        self.runtime.clear()

        for field in table_metadata.fields.values():

            # hanya field string / enum yang perlu
            if field.data_type not in ("string", "enum"):
                continue

            # enum statis
            if field.values:

                self.runtime.set_values(
                    field.name,
                    field.values
                )

                continue

            # ambil dari SQL

            values = self.repository.get_distinct_values(

                table_metadata.table_name,

                field.column

            )

            self.runtime.set_values(

                field.name,

                values

            )

        return self.runtime