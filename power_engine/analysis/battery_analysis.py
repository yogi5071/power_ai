"""
Battery Analysis
Power AI Copilot
"""

from power_engine.analysis.models.analysis_result import AnalysisResult

from power_engine.rules.battery_rules import BatteryRules
from power_engine.engine.health_score_engine import HealthScoreEngine


class BatteryAnalysis:
    """
    Analyze battery condition and produce AnalysisResult.

    Responsibilities:
    - Evaluate battery rules
    - Populate AnalysisResult
    - Delegate health score calculation

    This class MUST NOT:
    - Access database
    - Call AI
    - Execute SQL
    """

    @staticmethod
    def analyze(site):

        if site is None:
            return None

        result = AnalysisResult(site)

        # =====================================================
        # Battery Information
        # =====================================================

        result.battery_age = site.battery_age

        result.technology = BatteryRules.technology_status(site)

        result.warranty = BatteryRules.warranty_status(site)

        result.remaining_time = BatteryRules.remaining_time(site)

        result.recommendation = BatteryRules.recommendation(site)

        result.is_old = BatteryRules.is_old(site)

        # =====================================================
        # Health Score
        # =====================================================

        (
            result.health_score,
            result.health_reasons,
        ) = HealthScoreEngine.calculate(site)

        return result