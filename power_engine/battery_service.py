"""
Battery Service
Power AI Copilot

Coordinates battery analysis workflow.
"""

from database.master_site_repository import SiteRepository
from power_engine.analysis.battery_analysis import BatteryAnalysis


class BatteryService:
    """
    Service responsible for battery analysis.

    Responsibilities:
    - Load site information
    - Invoke BatteryAnalysis
    - Return analysis result

    This class MUST NOT contain:
    - Battery rules
    - Battery scoring logic
    - AI prompt generation
    - SQL queries
    """

    def __init__(self):

        self.repository = SiteRepository()

    # ==========================================================
    # SINGLE SITE
    # ==========================================================

    def analyze_site(self, site_id: str):
        """
        Analyze battery condition for one site.
        """

        site = self.repository.get_site_detail(site_id)

        if site is None:
            return None

        return BatteryAnalysis.analyze(site)

    # ==========================================================
    # PROVINCE
    # ==========================================================

    def analyze_province(self, province: str):
        """
        Analyze battery condition for one supported province.

        The current master_site dataset represents Jawa Timur,
        so province-level analysis is performed across all sites
        returned by the repository for that province.
        """

        sites = self.repository.get_sites_by_province(province)

        if not sites:
            return None

        return self._build_summary(
            sites=sites,
            location_type="Provinsi",
            location_name=province,
        )

    # ==========================================================
    # KABUPATEN
    # ==========================================================

    def analyze_kabupaten(self, kabupaten: str):

        sites = self.repository.get_sites_by_kabupaten(kabupaten)

        if not sites:
            return None

        return self._build_summary(
            sites=sites,
            location_type="Kabupaten",
            location_name=sites[0].kabupaten or kabupaten,
        )

    # ==========================================================
    # KECAMATAN
    # ==========================================================

    def analyze_kecamatan(self, kecamatan: str):

        sites = self.repository.get_sites_by_kecamatan(kecamatan)

        if not sites:
            return None

        return self._build_summary(
            sites=sites,
            location_type="Kecamatan",
            location_name=sites[0].kecamatan or kecamatan,
        )

    # ==========================================================
    # SUMMARY BUILDER
    # ==========================================================

    def _build_summary(
        self,
        sites,
        location_type,
        location_name,
    ):

        analyses = [
            BatteryAnalysis.analyze(site)
            for site in sites
        ]

        analyses.sort(
            key=lambda item: item.health_score
        )

        total = len(analyses)

        if total == 0:
            return None

        health = [
            item
            for item in analyses
            if item.health_status == "HEALTH"
        ]

        warning = [
            item
            for item in analyses
            if item.health_status == "WARNING"
        ]

        bad = [
            item
            for item in analyses
            if item.health_status == "BAD"
        ]

        technology = {}

        for item in analyses:

            name = item.site.battery or "Unknown"

            technology[name] = (
                technology.get(name, 0) + 1
            )

        return {

            "location_type": location_type,

            "location_name": location_name,

            "total_sites": total,

            "average_health_score": round(
                sum(
                    item.health_score
                    for item in analyses
                ) / total,
                2,
            ),

            "health_count": len(health),

            "warning_count": len(warning),

            "bad_count": len(bad),

            "technology": technology,

            "priority_sites": [

                {

                    "site_id": item.site.siteid,

                    "site_name": item.site.site_name,

                    "health_score": item.health_score,

                    "health_status": item.health_status,

                    "severity": item.severity,

                }

                for item in analyses[:5]

            ],

        }
