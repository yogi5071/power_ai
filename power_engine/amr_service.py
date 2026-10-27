"""AMR analysis service."""

from datetime import date

from database.amr_repository import AMRRepository
from models.amr_result import AMRResult


class AMRService:

    def __init__(self):

        self.repository = AMRRepository()

    # ==========================================================
    # CURRENT YEAR
    # ==========================================================

    @staticmethod
    def current_year():

        return date.today().year

    # ==========================================================
    # ANALYZE STATISTICS
    # ==========================================================

    def analyze(
        self,
        scope_type,
        scope_value,
        year=None,
    ):

        year = year or self.current_year()

        statistics = self.repository.get_statistics(
            scope_type,
            scope_value,
            year,
        )

        result = AMRResult(
            scope_type=scope_type,
            scope_value=scope_value,
            statistics=statistics,
        )

        if not result.has_data:

            return None

        return result

    # ==========================================================
    # GET SITE LIST BY STATUS
    # ==========================================================

    def get_sites(
        self,
        scope_type,
        scope_value,
        status,
        year=None,
    ):

        year = year or self.current_year()

        return self.repository.get_sites_by_status(
            scope_type,
            scope_value,
            status,
            year,
        )

    # ==========================================================
    # ANALYZE + SITE LIST
    #
    # Digunakan nanti untuk pertanyaan:
    #
    # "Site mana saja yang belum AMR?"
    # ==========================================================

    def analyze_sites(
        self,
        scope_type,
        scope_value,
        status,
        year=None,
    ):

        year = year or self.current_year()

        statistics = self.repository.get_statistics(
            scope_type,
            scope_value,
            year,
        )

        sites = self.repository.get_sites_by_status(
            scope_type,
            scope_value,
            status,
            year,
        )

        result = AMRResult(
            scope_type=scope_type,
            scope_value=scope_value,
            statistics=statistics,
            sites=sites,
        )

        if not result.has_data:

            return None

        return result