"""
database/base_repository.py

Base Repository untuk seluruh Database Layer.
"""

from __future__ import annotations

import mysql.connector

from database.connection import get_connection


class BaseRepository:
    """
    Base class untuk seluruh repository database.

    Menyediakan:
    - Connection
    - Cursor
    - Commit
    - Rollback
    - Close Connection
    """

    def __init__(self):
        self._connection = get_connection()

        if self._connection is None:
            raise ConnectionError("Gagal membuat koneksi ke database.")

    # =====================================================
    # CONNECTION
    # =====================================================

    def get_connection(self):
        """
        Mengembalikan object MySQL Connection.
        """
        return self._connection

    # =====================================================
    # CURSOR
    # =====================================================

    def get_cursor(self):
        """
        Cursor dictionary agar hasil query berupa dict.
        """
        return self._connection.cursor(dictionary=True)

    # =====================================================
    # TRANSACTION
    # =====================================================

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    # =====================================================
    # CLOSE
    # =====================================================

    def close(self):
        if self._connection and self._connection.is_connected():
            self._connection.close()

    # =====================================================
    # DESTRUCTOR
    # =====================================================

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass