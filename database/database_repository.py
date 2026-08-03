"""
database/database_repository.py

Base Database Repository.
"""

from database.base_repository import BaseRepository


class DatabaseRepository(BaseRepository):
    """
    Repository dasar yang menyediakan helper umum
    untuk seluruh repository database.
    """

    def __init__(self):
        super().__init__()

    # =====================================================
    # DATABASE INFORMATION
    # =====================================================

    def get_tables(self):
        """
        Mengambil seluruh nama tabel.
        """

        cursor = self.get_cursor()

        try:
            cursor.execute("SHOW TABLES")

            rows = cursor.fetchall()

            if not rows:
                return []

            # Ambil value kolom pertama
            return [list(row.values())[0] for row in rows]

        finally:
            cursor.close()

    # =====================================================
    # TABLE COLUMNS
    # =====================================================

    def get_columns(self, table_name):
        """
        Mengambil struktur kolom dari sebuah tabel.
        """

        cursor = self.get_cursor()

        try:
            cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")

            return cursor.fetchall()

        finally:
            cursor.close()

    # =====================================================
    # EXECUTE SELECT
    # =====================================================

    def fetch_one(self, sql, params=None):
        """
        Execute SELECT dan mengambil satu baris.
        """

        cursor = self.get_cursor()

        try:
            cursor.execute(sql, params or ())

            return cursor.fetchone()

        finally:
            cursor.close()

    def fetch_all(self, sql, params=None):
        """
        Execute SELECT dan mengambil seluruh baris.
        """

        cursor = self.get_cursor()

        try:
            cursor.execute(sql, params or ())

            return cursor.fetchall()

        finally:
            cursor.close()

    # =====================================================
    # EXECUTE DML
    # =====================================================

    def execute(self, sql, params=None):
        """
        INSERT / UPDATE / DELETE
        """

        cursor = self.get_cursor()

        try:
            cursor.execute(sql, params or ())

            self.commit()

            return cursor.rowcount

        except Exception:
            self.rollback()
            raise

        finally:
            cursor.close()