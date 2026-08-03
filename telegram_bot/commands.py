from telegram import Update
from telegram.ext import ContextTypes

from telegram_bot.router import MessageRouter
from telegram_bot.dispatcher import Dispatcher
from telegram_bot.keyboards import (
    main_menu_keyboard,
    battery_menu_keyboard,
    alarm_menu_keyboard,
    site_menu_keyboard,
    rectifier_menu_keyboard,
)

# ==========================================================
# Initialize
# ==========================================================

router = MessageRouter()
dispatcher = Dispatcher()


# ==========================================================
# /start
# ==========================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command: /start"""

    message = (
        "🤖 <b>Power Assistant</b>\n\n"
        "✅ <b>System Online</b>\n\n"
        "Ready to Analyze Power Site\n\n"
        "Silakan pilih menu di bawah atau langsung ketik pertanyaan.\n\n"
        "<i>Version 1.0</i>"
    )

    await update.message.reply_text(
        message,
        parse_mode="HTML",
        reply_markup=main_menu_keyboard()
    )


# ==========================================================
# /help
# ==========================================================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command: /help"""

    message = (
        "📖 <b>Power Assistant Help</b>\n\n"
        "Anda dapat menggunakan menu atau langsung mengetik.\n\n"
        "<b>Contoh:</b>\n"
        "• Battery SBY001\n"
        "• Alarm MLG023\n"
        "• Rectifier KDR001\n"
        "• SBY001\n\n"
        "🚧 AI Assistant akan segera tersedia."
    )

    await update.message.reply_text(
        message,
        parse_mode="HTML",
        reply_markup=main_menu_keyboard()
    )


# ==========================================================
# Handle All Messages
# ==========================================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message is None:
        return

    text = update.message.text.strip()

    # ======================================================
    # MAIN MENU
    # ======================================================

    if text == "🏠 Main Menu":

        await update.message.reply_text(
            "🏠 <b>Main Menu</b>",
            parse_mode="HTML",
            reply_markup=main_menu_keyboard()
        )
        return

    # ======================================================
    # BATTERY MENU
    # ======================================================

    if text == "🔋 Battery":

        await update.message.reply_text(
            (
                "🔋 <b>Battery Menu</b>\n\n"
                "Silakan pilih menu di bawah."
            ),
            parse_mode="HTML",
            reply_markup=battery_menu_keyboard()
        )
        return

    # ======================================================
    # ALARM MENU
    # ======================================================

    if text == "🚨 Alarm":

        await update.message.reply_text(
            (
                "🚨 <b>Alarm Menu</b>\n\n"
                "Silakan pilih menu di bawah."
            ),
            parse_mode="HTML",
            reply_markup=alarm_menu_keyboard()
        )
        return

    # ======================================================
    # SITE MENU
    # ======================================================

    if text == "📡 Site":

        await update.message.reply_text(
            (
                "📡 <b>Site Menu</b>\n\n"
                "Silakan pilih menu di bawah."
            ),
            parse_mode="HTML",
            reply_markup=site_menu_keyboard()
        )
        return

    # ======================================================
    # RECTIFIER MENU
    # ======================================================

    if text == "⚡ Rectifier":

        await update.message.reply_text(
            (
                "⚡ <b>Rectifier Menu</b>\n\n"
                "Silakan pilih menu di bawah."
            ),
            parse_mode="HTML",
            reply_markup=rectifier_menu_keyboard()
        )
        return

    # ======================================================
    # HELP BUTTON
    # ======================================================

    if text == "❓ Help":

        await help_command(update, context)
        return

    # ======================================================
    # DATABASE
    # ======================================================

    if text == "⚙ Database":

        await update.message.reply_text(
            (
                "⚙ <b>Database Menu</b>\n\n"
                "🚧 Feature masih dalam pengembangan."
            ),
            parse_mode="HTML"
        )
        return

    # ======================================================
    # ROUTER
    # ======================================================

    router_result = router.route(text)

    response = dispatcher.dispatch(router_result)

    await update.message.reply_text(
        response,
        parse_mode="HTML"
    )