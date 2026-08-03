"""
Analysis Result
Power AI Copilot

Stores the complete result of battery analysis.
"""


class AnalysisResult:
    """
    Container for battery analysis output.

    This object is consumed by:
    - PromptManager
    - AI Router
    - Gemini
    """

    def __init__(self, site):

        # ==================================================
        # Original Site
        # ==================================================

        self.site = site

        # ==================================================
        # Basic Information
        # ==================================================

        self.site_id = site.site_id
        self.site_name = site.site_name
        self.region = site.region
        self.cluster = site.cluster
        self.witel = site.witel

        # ==================================================
        # Battery Information
        # ==================================================

        self.battery_age = 0
        self.technology = ""
        self.warranty = ""
        self.remaining_time = 0

        # ==================================================
        # Health Assessment
        # ==================================================

        self.health_score = 100
        self.health_reasons = []

        # ==================================================
        # Risk Assessment
        # ==================================================

        self.risk = ""
        self.is_old = False

        # ==================================================
        # Recommendation
        # ==================================================

        self.recommendation = ""

    @property
    def is_healthy(self):
        return self.health_score >= 80

    @property
    def is_warning(self):
        return 60 <= self.health_score < 80

    @property
    def is_critical(self):
        return self.health_score < 60