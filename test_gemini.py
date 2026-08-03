"""
=========================================================
Power AI
Gemini Connection Test
=========================================================
"""

import traceback

from google import genai

from config.settings import Settings


def main():

    print("=" * 60)
    print("POWER AI - GEMINI CONNECTION TEST")
    print("=" * 60)

    try:

        # -------------------------------------------------
    # Validate Settings
        # -------------------------------------------------

        Settings.validate()

        print(f"Model      : {Settings.GEMINI_MODEL}")

        print(
            f"API Key    : {Settings.GEMINI_API_KEY[:10]}..."
        )

        print()

        # -------------------------------------------------
        # Create Client
        # -------------------------------------------------

        client = genai.Client(
            api_key=Settings.GEMINI_API_KEY
        )

        print("Client      : OK")

        # -------------------------------------------------
        # Generate Content
        # -------------------------------------------------

        response = client.models.generate_content(

            model=Settings.GEMINI_MODEL,

            contents="Balas hanya dengan satu kata: BERHASIL"

        )

        print("Request     : SUCCESS")

        print()

        print("=" * 60)
        print("Gemini Response")
        print("=" * 60)

        print(response.text)

        print("=" * 60)

    except Exception as e:

        print()

        print("=" * 60)
        print("ERROR")
        print("=" * 60)

        print(type(e).__name__)
        print()

        print(e)

        print()

        print("=" * 60)
        print("TRACEBACK")
        print("=" * 60)

        traceback.print_exc()


if __name__ == "__main__":
    main()