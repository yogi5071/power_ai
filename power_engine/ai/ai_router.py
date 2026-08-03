"""
AI Router
Power AI Copilot

Flow:
User
    ↓
IntentDetector
    ↓
EntityExtractor
    ↓
ToolRegistry
    ↓
BatteryService
    ↓
PromptManager
    ↓
GeminiService
"""

from power_engine.ai.gemini_service import GeminiService
from power_engine.ai.prompt_manager import PromptManager
from power_engine.ai.intent_detector import IntentDetector
from power_engine.ai.entity_extractor import EntityExtractor
from power_engine.ai.tool_registry import ToolRegistry


class AIRouter:
    """
    Main router for all AI requests.

    Responsibilities:
    - Detect user intent
    - Extract required entities
    - Call the appropriate Power Service
    - Build prompt
    - Generate final AI response

    This class MUST NOT contain:
    - SQL queries
    - Database logic
    - Business rules
    - Battery calculations
    """

    def __init__(self):

        self.ai = GeminiService()

        self.registry = ToolRegistry()

    def ask(self, question: str) -> str:
        """
        Process user question and return AI response.
        """

        intent = IntentDetector.detect(question)

        # ==========================================================
        # BATTERY
        # ==========================================================

        if intent == "battery":

            site_id = EntityExtractor.extract_site_id(question)

            if site_id is None:
                return "Silakan sebutkan Site ID."

            battery_service = self.registry.get("battery")

            result = battery_service.analyze_site(site_id)

            if result is None:
                return f"Site {site_id} tidak ditemukan."

            prompt = PromptManager.battery_prompt(
                question,
                result
            )

            return self.ai.generate(prompt)

        # ==========================================================
        # GENERAL QUESTION
        # ==========================================================

        prompt = PromptManager.general_prompt(question)

        return self.ai.generate(prompt)