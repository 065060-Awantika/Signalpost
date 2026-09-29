from backend.app.services.fact_extractor import FactExtractor


def test_extracts_organization_number():

    text = """
    Company information

    Legal name: Equinor ASA
    Organization number: 923609016
    Industry: Energy
    """

    extractor = FactExtractor()

    facts = extractor.extract(text)

    organization_facts = [
        fact
        for fact in facts
        if fact.field_name == "organization_number"
    ]

    assert len(organization_facts) == 1

    fact = organization_facts[0]

    assert fact.value == "923609016"
    assert fact.confidence >= 0.95
    assert "923609016" in fact.evidence_text


def test_extracts_multiple_company_facts():

    text = """
    Legal name: Equinor ASA
    Organization number: 923609016
    Website: https://www.equinor.com
    Industry: Energy
    Address: Forusbeen 50
    City: Stavanger
    """

    extractor = FactExtractor()

    facts = extractor.extract(text)

    fields = {
        fact.field_name
        for fact in facts
    }

    assert "legal_name" in fields
    assert "organization_number" in fields
    assert "website" in fields
    assert "industry" in fields
    assert "address" in fields
    assert "city" in fields


def test_extracts_norwegian_organization_number():

    text = """
    Foretaksnavn: Equinor ASA
    Organisasjonsnummer: 923609016
    """

    extractor = FactExtractor()

    facts = extractor.extract(text)

    assert any(
        fact.field_name == "organization_number"
        and fact.value == "923609016"
        for fact in facts
    )


def test_empty_text_returns_no_facts():

    extractor = FactExtractor()

    assert extractor.extract("") == []
    assert extractor.extract("   ") == []


def test_duplicate_facts_are_removed():

    text = """
    Organization number: 923609016
    Organization number: 923609016
    """

    extractor = FactExtractor()

    facts = extractor.extract(text)

    organization_facts = [
        fact
        for fact in facts
        if fact.field_name == "organization_number"
    ]

    assert len(organization_facts) == 1


def test_evidence_is_preserved():

    text = """
    Some company information.
    Organization number: 923609016
    The company operates internationally.
    """

    extractor = FactExtractor()

    facts = extractor.extract(text)

    fact = next(
        fact
        for fact in facts
        if fact.field_name == "organization_number"
    )

    assert "Organization number" in fact.evidence_text
    assert "923609016" in fact.evidence_text