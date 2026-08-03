import json

from power_engine.ai.gemini_service import GeminiService
from power_engine.ai.prompt_manager import PromptManager


class Planner:

    def __init__(self):

        self.ai = GeminiService()

    def create_plan(self, question: str):

        prompt = PromptManager.planner_prompt(question)

        response = self.ai.chat(prompt)

        try:

            return json.loads(response)

        except Exception:

            return {
                "module": "general",
                "action": "chat",
                "filters": [],
                "question": question
            }