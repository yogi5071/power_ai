class Formatter:
    """
    Telegram Message Formatter

    Tugas:
    Mengubah object hasil analysis menjadi
    pesan yang mudah dibaca engineer.
    """

    # ==================================================
    # Battery Report
    # ==================================================

    @staticmethod
    def battery_report(result):

        if result is None:
            return (
                "❌ Data battery tidak ditemukan."
            )


        site = result.site


        # ==============================
        # Status Emoji
        # ==============================

        if result.health_score >= 90:

            status_icon = "🟢"

        elif result.health_score >= 70:

            status_icon = "🟡"

        elif result.health_score >= 50:

            status_icon = "🟠"

        else:

            status_icon = "🔴"



        message = (

            "🔋 <b>Battery Health Report</b>\n"

            "━━━━━━━━━━━━━━━━━━\n\n"


            "📡 <b>Site Information</b>\n"

            f"Site ID      : <code>{site.siteid}</code>\n"

            f"Site Name    : {site.site_name}\n"

            f"Cluster      : {site.cluster}\n"

            f"Kabupaten    : {site.kabupaten}\n\n"


            "🔋 <b>Battery Information</b>\n"

            f"Technology   : {site.battery}\n"

            f"Age          : {result.battery_age} Tahun\n"

            f"Warranty     : {result.warranty}\n"

            f"Technology   : {result.technology}\n\n"


            "📊 <b>Analysis</b>\n"

            f"Health Score : {result.health_score}/100\n"

            f"Status       : {status_icon} {result.status}\n"

            f"Risk         : {result.risk}\n\n"


            "⏳ <b>Backup Estimation</b>\n"

            f"Remaining    : {result.remaining_time} Minutes\n\n"


            "💡 <b>Recommendation</b>\n"

            f"{result.recommendation}"

        )


        return message


    # ==================================================
    # Simple Message
    # ==================================================

    @staticmethod
    def simple(message):

        return message


    # ==================================================
    # Error Message
    # ==================================================

    @staticmethod
    def error(message):

        return (
            f"❌ <b>Error</b>\n\n"
            f"{message}"
        )