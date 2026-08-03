"""
Battery Analysis
Power AI Copilot
"""

from models.analysis_result import AnalysisResult

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

        result.battery_age = site.battery_age

        result.technology = BatteryRules.technology_status(site)

        result.warranty = BatteryRules.warranty_status(site)

        result.remaining_time = BatteryRules.remaining_time(site)

        result.risk = BatteryRules.risk_level(site)

        result.recommendation = BatteryRules.recommendation(site)

        result.is_old = BatteryRules.is_old(site)

        # ----------------------------------
        # Health Score
        # ----------------------------------

        result.health_score = HealthScoreEngine.calculate(result)

        return result