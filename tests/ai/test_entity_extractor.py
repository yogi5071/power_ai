from power_engine.ai.entity_extractor import EntityExtractor


def test(message):

    site = EntityExtractor.extract_site_id(message)

    print(f"Question : {message}")
    print(f"Site ID  : {site}")
    print("-" * 50)


if __name__ == "__main__":

    test("Bagaimana kondisi battery site SBY001?")

    test("Cek alarm MLG123")

    test("Battery JKT999")

    test("Site abc123")

    test("Selamat pagi")