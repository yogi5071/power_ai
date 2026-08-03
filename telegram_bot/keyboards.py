from telegram import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


# ==========================================================
# Main Menu
# ==========================================================

def main_menu_keyboard():

    keyboard = [
        ["🔋 Battery", "🚨 Alarm"],
        ["📡 Site", "⚡ Rectifier"],
        ["⚙ Database", "❓ Help"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Pilih menu atau ketik pertanyaan..."
    )


# ==========================================================
# Battery Menu
# ==========================================================

def battery_menu_keyboard():

    keyboard = [
        ["🔍 Check Battery"],
        ["📊 Battery Report"],
        ["🏠 Main Menu"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


# ==========================================================
# Alarm Menu
# ==========================================================

def alarm_menu_keyboard():

    keyboard = [
        ["🚨 Active Alarm"],
        ["📈 Alarm Report"],
        ["🏠 Main Menu"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


# ==========================================================
# Site Menu
# ==========================================================

def site_menu_keyboard():

    keyboard = [
        ["📡 Site Detail"],
        ["📍 Site Location"],
        ["🏠 Main Menu"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


# ==========================================================
# Rectifier Menu
# ==========================================================

def rectifier_menu_keyboard():

    keyboard = [
        ["⚡ Rectifier Status"],
        ["🏠 Main Menu"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )


# ==========================================================
# Confirm Dialog
# ==========================================================

def confirm_keyboard():

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "✅ Yes",
                callback_data="yes"
            ),
            InlineKeyboardButton(
                "❌ No",
                callback_data="no"
            ),
        ]
    ])

    return keyboard