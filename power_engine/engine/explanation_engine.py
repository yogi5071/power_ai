"""
Explanation Engine
Power AI Copilot

Mengubah AnalysisResult menjadi penjelasan teknis
yang akan digunakan PromptManager.
"""

from models.explanation import Explanation


class ExplanationEngine:
    """
    Generate technical explanation from AnalysisResult.

    Responsibilities
    ----------------
    - Build explanation object
    - Do NOT access database
    - Do NOT calculate score
    - Do NOT execute business rules
    """

    @staticmethod
    def generate(result):

        explanation = Explanation()

        # ==================================================
        # Technology
        # ==================================================

        explanation.technology = result.technology

        # ==================================================
        # Battery Age
        # ==================================================

        explanation.battery_age = result.battery_age

        # ==================================================
        # Warranty
        # ==================================================

        explanation.warranty = result.warranty

        # ==================================================
        # Remaining Time
        # ==================================================

        explanation.remaining_time = result.remaining_time

        # ==================================================
        # Health
        # ==================================================

        explanation.health_score = result.health_score

        explanation.health_reasons = result.health_reasons

        # ==================================================
        # Risk
        # ==================================================

        explanation.risk = result.risk

        # ==================================================
        # Recommendation
        # ==================================================

        explanation.recommendation = result.recommendation

        # ==================================================
        # Conclusion
        # ==================================================

        if result.health_score >= 90:

            explanation.conclusion = (
                "Battery berada dalam kondisi sangat baik."
            )

        elif result.health_score >= 70:

            explanation.conclusion = (
                "Battery masih layak digunakan namun perlu dimonitor."
            )

        elif result.health_score >= 50:

            explanation.conclusion = (
                "Battery mulai menunjukkan penurunan performa."
            )

        else:

            explanation.conclusion = (
                "Battery memerlukan tindakan korektif."
            )

        return explanation