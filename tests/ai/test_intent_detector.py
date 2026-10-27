from power_engine.ai.intent_detector import IntentDetector


def test_battery_condition_question():
    assert IntentDetector.detect("Bagaimana kondisi battery site SBY001?") == "battery"


def test_mains_fail_alarm_question():
    assert IntentDetector.detect("Mengapa alarm mains fail muncul?") == "alarm"


def test_rectifier_definition_question():
    assert IntentDetector.detect("Apa itu rectifier?") == "rectifier"


def test_battery_vrla_definition_question():
    assert IntentDetector.detect("Apa itu battery VRLA?") == "battery"


def test_greeting():
    assert IntentDetector.detect("Selamat pagi") == "general"


def test_bts_function_question():
    assert IntentDetector.detect("Apa fungsi BTS?") == "general"
