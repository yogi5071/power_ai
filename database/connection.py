"""MySQL connection factory for the repository layer."""

import os

import mysql.connector
from dotenv import load_dotenv


load_dotenv()


def get_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )
        print("MySQL connection established")
        return connection
    except mysql.connector.Error as error:
        print(f"MySQL connection failed: {error}")
        return None
