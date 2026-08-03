"""
Telegram Bot
Power AI Copilot
"""

import logging

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from config.settings import Settings

from telegram_bot.handlers import (
    start,
    help_command,
    chat,
)


logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


class TelegramBot:

    def __init__(self):

        Settings.validate()

        self.app = (
            Application.builder()
            .token(Settings.BOT_TOKEN)
            .build()
        )

        self.register_handlers()

    def register_handlers(self):

        self.app.add_handler(
            CommandHandler(
                "start",
                start,
            )
        )

        self.app.add_handler(
            CommandHandler(
                "help",
                help_command,
            )
        )

        self.app.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                chat,
            )
        )

    def run(self):

        print("=" * 60)
        print(" POWER AI COPILOT ")
        print("=" * 60)
        print(" Telegram Bot Running...")
        print("=" * 60)

        self.app.run_polling(
            allowed_updates=["message"]
        )


def run():

    bot = TelegramBot()

    bot.run()