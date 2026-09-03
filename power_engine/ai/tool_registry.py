"""
Tool Registry
Power AI Copilot
"""

from power_engine.battery_service import BatteryService
from power_engine.outage_service import OutageService
from power_engine.pln_service import PLNService
from power_engine.amr_service import AMRService


class ToolRegistry:

    def __init__(self):

        self.tools = {
            "battery": BatteryService(),
            "outage": OutageService(),
            "pln": PLNService(),
            "amr": AMRService(),
        }

    def has_tool(self, name: str) -> bool:

        return name.lower() in self.tools

    def get(self, name: str):

        return self.tools.get(
            name.lower()
        )