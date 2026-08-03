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

    def analyze_site(self, site_id: str):
        """
        Analyze battery condition for a site.
        """

        site = self.repository.get_site_detail(site_id)

        if site is None:
            return None

        return BatteryAnalysis.analyze(site)