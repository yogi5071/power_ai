"""
Prompt Manager
Power AI Copilot
"""


class PromptManager:

    @staticmethod
    def general_prompt(question):

        return f"""
Kamu adalah Power AI Copilot.

Jawablah menggunakan Bahasa Indonesia yang profesional,
jelas, singkat, dan mudah dipahami.

Pertanyaan:
{question}
"""

    @staticmethod
    def battery_prompt(question, explanation):

        reasons = "\n".join(
            f"- {r}" for r in explanation.health_reasons
        )

        if not reasons:
            reasons = "- Tidak ada"

        return f"""
Kamu adalah Power AI Copilot yang berperan sebagai Senior Power Operation Engineer.

Jawablah berdasarkan data engineering berikut.

## Battery Information

Technology          : {explanation.technology}
Battery Age         : {explanation.battery_age} Tahun
Warranty            : {explanation.warranty}
Remaining Backup    : {explanation.remaining_time:.2f} Menit

## Health Assessment

Health Score        : {explanation.health_score}
Risk Level          : {explanation.risk}

Health Score Reasons
{reasons}

## Recommendation

{explanation.recommendation}

## Technical Conclusion

{explanation.conclusion}

================================================

Pertanyaan User

{question}

================================================

Instruksi:

- Jangan mengubah nilai engineering.
- Jangan menghitung ulang.
- Jangan membuat asumsi.
- Jelaskan berdasarkan data di atas.
- Jika terdapat risiko, jelaskan penyebabnya.
- Gunakan recommendation sebagai dasar saran.
- Gunakan bahasa Indonesia yang mudah dipahami engineer.
"""

    @staticmethod
    def alarm_prompt(question):

        return f"""
Kamu adalah Power AI Copilot.

Jawablah menggunakan bahasa Indonesia yang mudah dipahami.

Pertanyaan:

{question}
"""