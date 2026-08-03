"""
Entity Extractor
Power AI Copilot
"""

import re
from difflib import get_close_matches

from models.entity import Entity


class EntityExtractor:

    # =====================================================
    # Regex
    # =====================================================

    SITE_PATTERN = r"\b[A-Z]{3}\d{3}\b"

    # =====================================================
    # Dictionaries
    # =====================================================

    CITIES = [
        "SURABAYA",
        "SIDOARJO",
        "MALANG",
        "GRESIK",
        "PASURUAN",
        "MOJOKERTO",
        "JEMBER",
        "MADIUN",
        "KEDIRI",
        "BLITAR",
        "PROBOLINGGO",
    ]

    TECHNOLOGIES = [
        "VRLA",
        "LITHIUM",
    ]

    VENDORS = [
        "HUAWEI",
        "ZTE",
        "ERICSSON",
        "NOKIA",
    ]

    BATTERY_STATUS = [
        "OUT OF WARRANTY",
        "OLD",
        "CRITICAL",
        "WARNING",
        "HEALTHY",
    ]

    ALARMS = [
        "MAINS FAIL",
        "LOW VOLTAGE",
        "RECTIFIER FAIL",
        "GENSET RUNNING",
        "HIGH TEMPERATURE",
        "BATTERY DISCONNECT",
    ]

    # =====================================================
    # Public
    # =====================================================

    @classmethod
    def extract(cls, message: str) -> Entity:

        entity = Entity()

        text = message.upper()

        cls._extract_site(text, entity)
        cls._extract_city(text, entity)
        cls._extract_vendor(text, entity)
        cls._extract_technology(text, entity)
        cls._extract_battery_status(text, entity)
        cls._extract_alarm(text, entity)

        return entity

    # =====================================================
    # Site
    # =====================================================

    @classmethod
    def _extract_site(cls, text, entity):

        match = re.search(cls.SITE_PATTERN, text)

        if match:
            entity.site_id = match.group()

    # =====================================================
    # City
    # =====================================================

    @classmethod
    def _extract_city(cls, text, entity):

        city = cls._find_best_match(text, cls.CITIES)

        if city:
            entity.city = city.title()

    # =====================================================
    # Vendor
    # =====================================================

    @classmethod
    def _extract_vendor(cls, text, entity):

        vendor = cls._find_best_match(text, cls.VENDORS)

        if vendor:
            entity.vendor = vendor.title()

    # =====================================================
    # Technology
    # =====================================================

    @classmethod
    def _extract_technology(cls, text, entity):

        tech = cls._find_best_match(text, cls.TECHNOLOGIES)

        if tech:
            entity.technology = tech.title()

    # =====================================================
    # Battery Status
    # =====================================================

    @classmethod
    def _extract_battery_status(cls, text, entity):

        status = cls._find_best_match(text, cls.BATTERY_STATUS)

        if status:
            entity.battery_status = status.title()

    # =====================================================
    # Alarm
    # =====================================================

    @classmethod
    def _extract_alarm(cls, text, entity):

        alarm = cls._find_best_match(text, cls.ALARMS)

        if alarm:
            entity.alarm = alarm.title()

    # =====================================================
    # Utility
    # =====================================================

    @staticmethod
    def _find_best_match(text, candidates):

        # Exact Match
        for item in candidates:

            if item in text:
                return item

        # Fuzzy Match
        words = text.split()

        matches = get_close_matches(
            " ".join(words),
            candidates,
            n=1,
            cutoff=0.75
        )

        if matches:
            return matches[0]

        return None