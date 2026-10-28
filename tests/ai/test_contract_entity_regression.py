from power_engine.ai.entity_extractor import EntityExtractor


def test_site_id_question_extracts_site_profile_not_contract_value():
    entity = EntityExtractor.extract(
        "Berapa nomor kontrak PLN untuk site SBY001?"
    )

    assert entity.site_id == "SBY001"
    assert entity.contract_subject == "no_contract"
    assert entity.contract_value is None


def test_site_id_and_explicit_contract_number_are_preserved():
    entity = EntityExtractor.extract(
        "Cari nomor kontrak PLN ABC123 untuk site SBY001"
    )

    assert entity.site_id == "SBY001"
    assert entity.contract_subject == "no_contract"
    assert entity.contract_value == "ABC123"


def test_contract_number_without_site_id_is_preserved():
    entity = EntityExtractor.extract(
        "Cari site dengan nomor kontrak PLN ABC123"
    )

    assert entity.contract_subject == "no_contract"
    assert entity.contract_value == "ABC123"
