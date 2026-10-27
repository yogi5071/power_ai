from database.database_repository import DatabaseRepository


class DatabaseService:

    def __init__(self):
        self.repo = DatabaseRepository()

    # ==========================
    # Metadata
    # ==========================

    def get_tables(self):
        return self.repo.get_tables()

    def get_columns(self, table_name):
        return self.repo.get_columns(table_name)

    # ==========================
    # Query
    # ==========================

    def fetch_one(self, sql, params=None):
        return self.repo.fetch_one(sql, params)

    def fetch_all(self, sql, params=None):
        return self.repo.fetch_all(sql, params)

    def execute(self, sql, params=None):
        return self.repo.execute(sql, params)

    def close(self):
        self.repo.close()