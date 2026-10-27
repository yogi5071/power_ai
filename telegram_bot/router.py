import re

from models.intent import Intent
from models.router_result import RouterResult


class MessageRouter:
    """
    Power Assistant Message Router

    Tugas:
    1. Membersihkan text
    2. Mencari Site ID
    3. Menentukan Intent
    4. Menghasilkan RouterResult
    """

    # ==========================================
    # Normalize Text
    # ==========================================

    def normalize(self, text: str) -> str:

        text = text.lower().strip()

        # Hilangkan karakter aneh
        text = re.sub(r"[^\w\s]", "", text)

        # Rapikan spasi
        text = re.sub(r"\s+", " ", text)

        return text

    # ==========================================
    # Extract Site ID
    # ==========================================

    def extract_site(self, text: str):

        """
        Contoh:

        SBY001
        MLG023
        KDR101
        """

        match = re.search(r"\b[a-z]{3}\d{3}\b", text)

        if match:
            return match.group().upper()

        return None

    # ==========================================
    # Greeting
    # ==========================================

    def is_greeting(self, text: str):

        greetings = [
            "halo",
            "hai",
            "hello",
            "hi",
            "pagi",
            "siang",
            "sore",
            "malam"
        ]

        return text in greetings

    # ==========================================
    # Battery Intent
    # ==========================================

    def is_battery(self, text: str):

        keywords = [
            "battery",
            "baterai",
            "accu"
        ]

        return any(word in text for word in keywords)

    # ==========================================
    # Alarm Intent
    # ==========================================

    def is_alarm(self, text: str):

        keywords = [
            "alarm",
            "warning",
            "fault"
        ]

        return any(word in text for word in keywords)

    # ==========================================
    # Rectifier Intent
    # ==========================================

    def is_rectifier(self, text: str):

        keywords = [
            "rectifier",
            "recti"
        ]

        return any(word in text for word in keywords)

    # ==========================================
    # Site Intent
    # ==========================================

    def is_site(self, site):

        return site is not None

    # ==========================================
    # Main Router
    # ==========================================

    def route(self, text: str) -> RouterResult:

        normalized = self.normalize(text)

        site = self.extract_site(normalized)

        # Greeting
        if self.is_greeting(normalized):

            return RouterResult(
                intent=Intent.GREETING,
                confidence=1.0,
                original_text=text,
                normalized_text=normalized
            )

        # Battery
        if self.is_battery(normalized):

            return RouterResult(
                intent=Intent.BATTERY,
                confidence=0.98,
                original_text=text,
                normalized_text=normalized,
                entities={
                    "site_id": site
                }
            )

        # Alarm
        if self.is_alarm(normalized):

            return RouterResult(
                intent=Intent.ALARM,
                confidence=0.98,
                original_text=text,
                normalized_text=normalized,
                entities={
                    "site_id": site
                }
            )

        # Rectifier
        if self.is_rectifier(normalized):

            return RouterResult(
                intent=Intent.RECTIFIER,
                confidence=0.98,
                original_text=text,
                normalized_text=normalized,
                entities={
                    "site_id": site
                }
            )

        # Site
        if self.is_site(site):

            return RouterResult(
                intent=Intent.SITE,
                confidence=0.90,
                original_text=text,
                normalized_text=normalized,
                entities={
                    "site_id": site
                }
            )

        # Default
        return RouterResult(
            intent=Intent.GENERAL_AI,
            confidence=0.70,
            original_text=text,
            normalized_text=normalized
        )