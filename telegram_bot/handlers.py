"""
Telegram Handlers
Power AI Copilot
"""

import traceback

from telegram import Update
from telegram.ext import ContextTypes

from power_engine.ai.ai_router import AIRouter


router = AIRouter()


# ==========================================================
# /start
# ==========================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = (
        "👋 Selamat datang di *Power AI Copilot*\n\n"
        "Saya dapat membantu menganalisa:\n\n"
        "🔋 Battery Health\n"
        "⚡ Alarm Power\n"
        "🔌 Rectifier\n"
        "🏢 Site Power\n\n"
        "Contoh:\n"
        "`Bagaimana kondisi battery site SBY001?`"
    )

    await update.message.reply_markdown(text)


# ==========================================================
# /help
# ==========================================================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    text = (
        "Contoh pertanyaan:\n\n"
        "• Bagaimana kondisi battery site SBY001?\n"
        "• Cek battery site MLG123\n"
        "• Apa itu battery VRLA?\n"
        "• Mengapa alarm mains fail muncul?\n"
        "• Apa fungsi rectifier?"
    )

    await update.message.reply_text(text)


# ==========================================================
# Chat
# ==========================================================

async def chat(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.message is None:
        return

    question = update.message.text.strip()

    if not question:
        return

    print("=" * 60)
    print("QUESTION")
    print(question)
    print("=" * 60)

    try:

        answer = router.ask(question)

        print("ANSWER")
        print(answer)
        print("=" * 60)

        await update.message.reply_text(answer)

    except Exception as e:

        traceback.print_exc()

        await update.message.reply_text(

            "❌ Terjadi kesalahan.\n\n"

            f"{e}"

        )