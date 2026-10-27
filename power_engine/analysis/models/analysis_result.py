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

        # =====================================================
        # Battery Information
        # =====================================================

        self.battery_age = 0
        self.technology = ""
        self.warranty = ""
        self.remaining_time = 0

        # =====================================================
        # Health
        # =====================================================

        self.health_score = 100
        self.health_reasons = []

        # =====================================================
        # Severity
        # =====================================================

      
        self.is_old = False

        # =====================================================
        # Recommendation
        # =====================================================

        self.recommendation = ""

    # =====================================================
    # Health Classification
    # =====================================================

    @property
    def is_health(self):
        return self.health_score >= 80

    @property
    def is_warning(self):
        return 60 <= self.health_score < 80

    @property
    def is_bad(self):
        return self.health_score < 60

    # =====================================================
    # Health Status
    # =====================================================

    @property
    def health_status(self):

        if self.is_bad:
            return "BAD"

        if self.is_warning:
            return "WARNING"

        return "HEALTH"

    # =====================================================
    # Severity
    # =====================================================

    @property
    def severity(self):

        if self.is_bad:
            return "CRITICAL"

        if self.is_warning:
            return "WARNING"

        return "GOOD"

    # =====================================================
    # Conclusion
    # =====================================================

    @property
    def conclusion(self):

        return (
            f"Battery {self.site.siteid} "
            f"berstatus {self.health_status} "
            f"dengan Severity {self.severity} "
            f"dan Health Score {self.health_score}/100."
        )