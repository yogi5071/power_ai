"""
Battery Analysis Engine
Power AI Copilot
"""

from models.analysis_result import AnalysisResult
from power_engine.rules.battery_rules import BatteryRules


class BatteryAnalysis:

    @staticmethod
    def analyze(site):

        if site is None:
            return None

        result = AnalysisResult(site)

        # ---------------------------------
        # Basic Information
        # ---------------------------------

        result.battery_age = site.battery_age

        # ---------------------------------
        # Engineering Analysis
        # ---------------------------------

        result.technology = BatteryRules.technology_status(site)

        result.warranty = BatteryRules.warranty_status(site)

        result.remaining_time = BatteryRules.remaining_time(site)

        result.risk = BatteryRules.risk_level(site)

        result.recommendation = BatteryRules.recommendation(site)

        result.is_old = BatteryRules.is_old(site)

        # ---------------------------------
        # Health Score
        # ---------------------------------

        result.health_score = BatteryRules.health_score(result)

        return result