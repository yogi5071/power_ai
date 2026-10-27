"""Outage service. Uses engineering-derived min/avg/max only."""

from database.outage_repository import OutageRepository
from models.outage_result import OutageResult


class OutageService:
    def __init__(self):
        self.repository = OutageRepository()

    def analyze(self, scope_type, scope_value):
        if not scope_type or not scope_value:
            return None
        row = self.repository.get_statistics(scope_type, scope_value)
        result = OutageResult(scope_type, scope_value, row or {})
        return result if result.has_data else None
