import os
from dotenv import load_dotenv

# Load file .env
load_dotenv()

# Ambil token Telegram dari .env
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Validasi
if not TELEGRAM_BOT_TOKEN:
    raise ValueError(
        "TELEGRAM_BOT_TOKEN tidak ditemukan. Periksa file .env"
    )