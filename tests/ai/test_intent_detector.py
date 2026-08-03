from power_engine.ai.intent_detector import IntentDetector


def test(message):
    intent = IntentDetector.detect(message)
    print(f"Question : {message}")
    print(f"Intent   : {intent}")
    print("-" * 50)


if __name__ == "__main__":

    test("Bagaimana kondisi battery site SBY001?")

    test("Mengapa alarm mains fail muncul?")

    test("Apa itu rectifier?")

    test("Apa itu battery VRLA?")

    test("Selamat pagi")

    test("Apa fungsi BTS?")