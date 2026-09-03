from power_engine.ai.intent_detector import IntentDetector
from power_engine.ai.entity_extractor import EntityExtractor


def test_pln_site_three_months():
    q = "Berapa PLN 3 bulan terakhir site ABC123?"
    assert IntentDetector.detect(q) == "pln"
    assert EntityExtractor.extract_scope(q) == ("siteid", "ABC123")
    assert EntityExtractor.extract_period_months(q) == 3


def test_pln_without_scope_is_not_invented():
    q = "Berapa tagihan PLN bulan ini?"
    assert IntentDetector.detect(q) == "pln"
    assert EntityExtractor.extract_scope(q) == (None, None)
    assert EntityExtractor.extract_period_months(q) == 1


def test_outage_kecamatan():
    q = "Berapa rata-rata pemadaman Kecamatan Taman?"
    assert IntentDetector.detect(q) == "outage"
    assert EntityExtractor.extract_scope(q) == ("kecamatan", "Taman")


def test_battery_outage_combined():
    q = "Bagaimana kondisi battery ABC123 dan pemadamannya?"
    assert IntentDetector.detect(q) == "battery_outage"
    assert EntityExtractor.extract_scope(q) == ("siteid", "ABC123")
