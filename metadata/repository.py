"""
metadata/repository.py
"""

from database.connection import get_connection


class MetadataRepository:

    def get_distinct_values(
        self,
        table_name: str,
        column_name: str
    ):

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(

            f"""
            SELECT DISTINCT {column_name}
            FROM {table_name}
            WHERE {column_name} IS NOT NULL
            """
        )

        rows = cursor.fetchall()

        cursor.close()

        conn.close()

        return [

            row[0]

            for row in rows

            if row[0] not in (None, "")
        ]