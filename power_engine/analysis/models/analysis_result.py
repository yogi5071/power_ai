"""
Analysis Result
Power AI Copilot
"""


class AnalysisResult:
    """
    Container for battery analysis result.

    This object stores ONLY analysis output.
    """

    def __init__(self, site):

        # Keep original site object
        self.site = site

        # Battery Information
        self.battery_age = 0
        self.technology = ""
        self.warranty = ""
        self.remaining_time = 0

        # Health
        self.health_score = 100
        self.health_reasons = []

        # Risk
        self.risk = ""
        self.is_old = False

        # Recommendation
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