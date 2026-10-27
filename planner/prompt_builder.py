"""
ai/prompt_builder.py

Build prompt yang dikirim ke AI.

Class ini HANYA bertugas membangun prompt.
Tidak melakukan request API.
Tidak melakukan parsing response.
"""

from typing import Dict


class PromptBuilder:
    """
    Build berbagai prompt untuk AI.
    """

    @staticmethod
    def build_planner_prompt(
        user_question: str,
        metadata: Dict
    ) -> str:
        """
        Membuat prompt untuk Planner AI.
        """

        return f"""
You are an AI Planner for Power AI.

Your job is NOT to answer the user.

Your ONLY job is to convert the user's request into a valid Execution Plan.

Available metadata:

{metadata}

User Request:

{user_question}

Rules:

1. Never answer the user.
2. Never generate SQL.
3. Never explain your reasoning.
4. Return ONLY valid JSON.
5. Use metadata field names exactly.
6. If information is missing, ask for clarification.

Return JSON only.
"""