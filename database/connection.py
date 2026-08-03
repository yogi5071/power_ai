import mysql.connector
from dotenv import load_dotenv
import os

# Membaca file .env
load_dotenv()

def get_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )

        print("✅ Berhasil terhubung ke MySQL")
        return conn

    except mysql.connector.Error as err:
        print(f"❌ Gagal terhubung: {err}")
        return None