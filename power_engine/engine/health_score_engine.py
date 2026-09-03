"""
Health Score Engine
Power AI Copilot

Responsible for calculating battery health score.
"""

from typing import List, Tuple


class HealthScoreEngine:
    """
    Calculate battery health score.

    Responsibilities:
    - Evaluate battery age
    - Evaluate backup capability
    - Evaluate warranty status
    - Produce health score
    - Produce health score reasons

    This class MUST NOT:
    - Access database
    - Call AI
    - Execute SQL
    """

    @staticmethod
    def calculate(site) -> Tuple[int, List[str]]:

        score = 100
        reasons = []

        # =====================================================
        # Battery Age
        # =====================================================

        if site.is_vrla:

            if site.battery_age >= 5:
                score -= 40
                reasons.append(
                    "VRLA battery has exceeded its 5-year design life (-40)"
                )

            elif site.battery_age >= 3:
                score -= 20
                reasons.append(
                    "VRLA battery is older than 3 years (-20)"
                )

        elif site.is_lithium:

            if site.battery_age >= 10:
                score -= 30
                reasons.append(
                    "Lithium battery has exceeded its 10-year design life (-30)"
                )

            elif site.battery_age >= 5:
                score -= 10
                reasons.append(
                    "Lithium battery is older than 5 years (-10)"
                )

        # =====================================================
        # Remaining Backup Time (Hours)
        # =====================================================

        backup_time = 0

        if site.total_load_rectifier > 0:

            backup_time = (
                (site.total_bank or 0) * 100
            ) / site.total_load_rectifier

        if backup_time < 10:
            score -= 20
            reasons.append(
                "Estimated remaining backup time is below 10 hours (-20)"
            )

        elif backup_time < 20:
            score -= 10
            reasons.append(
                "Estimated remaining backup time is below 20 hours (-10)"
            )

        # =====================================================
        # Warranty
        # =====================================================

        warranty = str(site.status_warranty_battery).upper()

        if "OUT" in warranty:

            score -= 10

            reasons.append(
                "Battery warranty has expired (-10)"
            )

        # =====================================================
        # Final Health Score
        # =====================================================

        score = max(score, 0)

        return score, reasons