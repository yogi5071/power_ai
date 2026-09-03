"""
Telegram Handlers
Power AI Copilot
"""

import traceback

from telegram import Update
from telegram.ext import ContextTypes

from power_engine.ai.ai_router import AIRouter
from telegram_bot.conversation import ConversationManager


router = AIRouter()
conversation = ConversationManager()


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
        "🏢 Site Power\n"
        "💰 PLN Monthly\n"
        "📡 AMR\n\n"
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
        "• Apa fungsi rectifier?\n"
        "• Berapa site yang belum AMR di Waru?\n"
        "• Site mana saja yang belum AMR?"
    )

    await update.message.reply_text(text)


# ==========================================================
# CONTEXT HELPER
# ==========================================================

def _get_user_id(update: Update):

    if update.effective_user is None:
        return None

    return update.effective_user.id


def _build_context_question(
    question: str,
    previous_context: dict,
) -> str:

    if not previous_context:
        return question

    intent = previous_context.get("intent")
    scope_type = previous_context.get("scope_type")
    scope_value = previous_context.get("scope_value")
    status = previous_context.get("status")
    year = previous_context.get("year")
    site_id = previous_context.get("site_id")
    period_months = previous_context.get("period_months")

    context_parts = []

    if intent:
        context_parts.append(
            f"intent={intent}"
        )

    if scope_type:
        context_parts.append(
            f"scope_type={scope_type}"
        )

    if scope_value:
        context_parts.append(
            f"scope_value={scope_value}"
        )

    if status:
        context_parts.append(
            f"status={status}"
        )

    if year:
        context_parts.append(
            f"year={year}"
        )

    if site_id:
        context_parts.append(
            f"site_id={site_id}"
        )

    if period_months:
        context_parts.append(
            f"period_months={period_months}"
        )

    if not context_parts:
        return question

    context_text = ", ".join(context_parts)

    return (
        f"{question}\n\n"
        f"[Previous conversation context: {context_text}]"
    )


# ==========================================================
# SAVE CONTEXT
# ==========================================================

def _save_context(
    user_id,
    question: str,
    answer: str,
):

    if user_id is None:
        return

    # ------------------------------------------------------
    # AMR context
    # ------------------------------------------------------

    question_lower = question.lower()

    if "amr" in question_lower:

        scope_type = None
        scope_value = None

        # ----------------------------------------------
        # SITE
        # ----------------------------------------------

        import re

        site_match = re.search(
            r"\b[A-Z]{2,5}\d{2,6}\b",
            question.upper()
        )

        if site_match:

            scope_type = "siteid"
            scope_value = site_match.group(0)

        # ----------------------------------------------
        # KECAMATAN
        # ----------------------------------------------

        if "kecamatan" in question_lower:

            match = re.search(
                r"kecamatan\s+([a-zA-Z0-9_-]+)",
                question,
                re.IGNORECASE,
            )

            if match:

                scope_type = "kecamatan"
                scope_value = match.group(1)

        # ----------------------------------------------
        # KABUPATEN
        # ----------------------------------------------

        if "kabupaten" in question_lower:

            match = re.search(
                r"kabupaten\s+([a-zA-Z0-9_-]+)",
                question,
                re.IGNORECASE,
            )

            if match:

                scope_type = "kabupaten"
                scope_value = match.group(1)

        # ----------------------------------------------
        # NOP
        # ----------------------------------------------

        if "nop" in question_lower:

            match = re.search(
                r"nop\s+([a-zA-Z0-9_-]+)",
                question,
                re.IGNORECASE,
            )

            if match:

                scope_type = "nop"
                scope_value = match.group(1)

        # ----------------------------------------------
        # CLUSTER
        # ----------------------------------------------

        if "cluster" in question_lower:

            match = re.search(
                r"cluster\s+([a-zA-Z0-9_-]+)",
                question,
                re.IGNORECASE,
            )

            if match:

                scope_type = "cluster"
                scope_value = match.group(1)

        # ----------------------------------------------
        # UNION
        # ----------------------------------------------

        if (
            "total site" in question_lower
            or "seluruh site" in question_lower
            or "semua site" in question_lower
            or "seluruh data" in question_lower
            or "union" in question_lower
        ):

            scope_type = "union"
            scope_value = "union"

        # ----------------------------------------------
        # STATUS
        # ----------------------------------------------

        status = None

        if "belum amr" in question_lower:

            status = "Belum AMR"

        elif (
            "sudah amr" in question_lower
            or "yang amr" in question_lower
        ):

            status = "AMR"

        elif (
            "belum ada informasi" in question_lower
            or "tidak diketahui" in question_lower
        ):

            status = "-"

        # ----------------------------------------------
        # YEAR
        # ----------------------------------------------

        year = None

        year_match = re.search(
            r"\b20\d{2}\b",
            question,
        )

        if year_match:

            year = int(
                year_match.group(0)
            )

        # ----------------------------------------------
        # DEFAULT YEAR
        # ----------------------------------------------

        if year is None:

            from datetime import date

            year = date.today().year

        conversation.set_context(
            user_id=user_id,
            intent="amr",
            scope_type=scope_type,
            scope_value=scope_value,
            status=status,
            year=year,
        )


# ==========================================================
# CHAT
# ==========================================================

async def chat(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.message is None:
        return

    if update.message.text is None:
        return

    question = update.message.text.strip()

    if not question:
        return

    user_id = _get_user_id(update)

    # ======================================================
    # TELEGRAM REPLY CONTEXT
    # ======================================================

    reply_message = update.message.reply_to_message

    previous_context = {}

    if reply_message is not None:

        previous_context = conversation.get_context(
            user_id
        )

    # ======================================================
    # BUILD EFFECTIVE QUESTION
    # ======================================================

    effective_question = _build_context_question(
        question,
        previous_context,
    )

    print("=" * 60)
    print("QUESTION")
    print(question)

    if previous_context:

        print("-" * 60)
        print("PREVIOUS CONTEXT")
        print(previous_context)

    print("-" * 60)
    print("EFFECTIVE QUESTION")
    print(effective_question)

    print("=" * 60)

    try:

        answer = router.ask(
            effective_question
        )

        print("ANSWER")
        print(answer)
        print("=" * 60)

        sent_message = await update.message.reply_text(
            answer
        )

        # ==================================================
        # SAVE CONVERSATION CONTEXT
        # ==================================================

        _save_context(
            user_id=user_id,
            question=question,
            answer=answer,
        )

        # ==================================================
        # SAVE BOT MESSAGE ID
        # ==================================================

        if user_id is not None:

            current_context = conversation.get_context(
                user_id
            )

            conversation.set_context(
                user_id=user_id,
                bot_message_id=sent_message.message_id,
            )

    except Exception as e:

        traceback.print_exc()

        await update.message.reply_text(

            "❌ Terjadi kesalahan.\n\n"

            f"{e}"

        )