"""
Tool Registry
Power AI Copilot
"""

from power_engine.battery_service import BatteryService


class ToolRegistry:

    def __init__(self):

        self.tools = {
            "battery": BatteryService(),
        }

    def has_tool(self, name: str) -> bool:

        return name.lower() in self.tools

    def get(self, name: str):

        return self.tools.get(name.lower())