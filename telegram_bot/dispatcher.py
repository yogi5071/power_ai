from models.intent import Intent

from power_engine.battery_service import BatteryService

from telegram_bot.formatter import Formatter


class Dispatcher:
    """
    Dispatcher

    Bertugas meneruskan hasil Router
    ke service yang sesuai.
    """

    def __init__(self):

        self.battery_service = BatteryService()

    # ======================================================
    # Main Dispatcher
    # ======================================================

    def dispatch(self, router_result):

        intent = router_result.intent

        if intent == Intent.GREETING:
            return self.handle_greeting()

        elif intent == Intent.BATTERY:
            return self.handle_battery(router_result)

        elif intent == Intent.ALARM:
            return Formatter.simple(
                "🚧 Alarm feature is under development."
            )

        elif intent == Intent.SITE:
            return Formatter.simple(
                "🚧 Site feature is under development."
            )

        elif intent == Intent.RECTIFIER:
            return Formatter.simple(
                "🚧 Rectifier feature is under development."
            )

        elif intent == Intent.GENERAL_AI:
            return Formatter.simple(
                "🤖 AI Assistant belum tersedia."
            )

        return Formatter.error(
            "Perintah tidak dikenali."
        )

    # ======================================================
    # Greeting
    # ======================================================

    def handle_greeting(self):

        return Formatter.simple(
            "👋 Halo, saya siap membantu analisis Power Site."
        )

    # ======================================================
    # Battery
    # ======================================================

    def handle_battery(self, router_result):

        site_id = router_result.entities.get("site")

        if not site_id:

            return Formatter.error(
                "Site ID tidak ditemukan.\n\n"
                "Contoh:\n"
                "Battery SBY001"
            )

        result = self.battery_service.analyze_site(site_id)

        if result is None:

            return Formatter.error(
                f"Site <b>{site_id}</b> tidak ditemukan."
            )

        return Formatter.battery_report(result)