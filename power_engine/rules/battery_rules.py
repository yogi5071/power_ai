"""
Battery Business Rules
Power AI Copilot

Seluruh aturan battery berada di file ini.
Jangan letakkan business rules di SQL.
"""


class BatteryRules:

    @staticmethod
    def is_old(site):
        """
        Menentukan apakah battery sudah tua.

        VRLA     > 1 Tahun
        Lithium  > 5 Tahun
        """

        if site is None:
            return False

        if site.battery is None:
            return False

        battery = site.battery.strip().upper()
        age = site.battery_age

        if battery == "VRLA":
            return age > 1

        if battery == "LITHIUM":
            return age > 5

        return False

    @staticmethod
    def technology_status(site):
        """
        Menentukan status teknologi battery.
        """

        if site is None or site.battery is None:
            return "Unknown"

        battery = site.battery.strip().upper()

        if battery == "VRLA":
            return "VRLA"

        if battery == "LITHIUM":
            return "LITHIUM"

        return "Unknown"

    @staticmethod
    def warranty_status(site):
        """
        Warranty:

        VRLA      : Out of Warranty
        Lithium   :
            < 5 Tahun  -> In Warranty
            >=5 Tahun  -> Out of Warranty
        """

        if site is None or site.battery is None:
            return "Unknown"

        battery = site.battery.strip().upper()
        age = site.battery_age

        if battery == "VRLA":
            return "Out of Warranty"

        if battery == "LITHIUM":
            if age < 5:
                return "In Warranty"
            return "Out of Warranty"

        return "Unknown"

    @staticmethod
    def remaining_time(site):
        """
        Estimasi Remaining Time

        Rumus dasar:
            (Total Bank × 100) / Total Load Rectifier

        VRLA dibatasi maksimum ±60 menit (1 jam)
        sesuai karakteristik operasional.
        """

        if site is None:
            return 0

        if site.total_bank is None:
            return 0

        if site.total_load_rectifier is None:
            return 0

        if site.total_load_rectifier <= 0:
            return 0

        remaining = round(
            (site.total_bank * 100) / site.total_load_rectifier,
            2
        )

        if (
            site.battery is not None and
            site.battery.strip().upper() == "VRLA"
        ):
            remaining = min(remaining, 60)

        return remaining

    @staticmethod
    def risk_level(site):
        """
        Menentukan level risiko battery.
        """

        if BatteryRules.is_old(site):
            return "HIGH"

        return "NORMAL"

    @staticmethod
    def recommendation(site):
        """
        Memberikan rekomendasi engineer.
        """

        if site is None or site.battery is None:
            return "Tidak ada rekomendasi."

        battery = site.battery.strip().upper()

        if BatteryRules.is_old(site):

            if battery == "VRLA":
                return (
                    "VRLA telah melewati batas umur rekomendasi. "
                    "Disarankan melakukan Battery Capacity Test "
                    "dan mempersiapkan penggantian battery."
                )

            if battery == "LITHIUM":
                return (
                    "Lithium telah melewati umur rekomendasi. "
                    "Disarankan melakukan Battery Health Check, "
                    "evaluasi warranty, dan mempersiapkan replacement battery."
                )

        return "Battery masih dalam batas operasional."