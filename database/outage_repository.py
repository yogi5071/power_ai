"""Read-only repository for engineering outage statistics."""

from database.base_repository import BaseRepository


class OutageRepository(BaseRepository):

    ALLOWED_SCOPE_COLUMNS = {
        "siteid": "siteid",
        "kecamatan": "kecamatan",
        "kabupaten": "kabupaten",
        "nop": "nop_name",
        "cluster": "cluster",
    }

    def get_statistics(self, scope_field: str, scope_value: str):
        column = self.ALLOWED_SCOPE_COLUMNS.get(scope_field)

        if not column:
            raise ValueError(
                f"Unsupported outage scope: {scope_field}"
            )

        cursor = self.get_cursor()

        try:
            cursor.execute(
                f"""
                SELECT
                    COUNT(*) AS total_site,
                    AVG(pemadaman_avg) AS outage_avg,
                    MAX(pemadaman_max) AS outage_max
                FROM master_site
                WHERE LOWER(`{column}`) = LOWER(%s)
                """,
                (str(scope_value).strip(),),
            )

            return cursor.fetchone()

        finally:
            cursor.close()