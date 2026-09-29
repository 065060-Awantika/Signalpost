from backend.app.services.fact_extractor import FactExtractor


def test_extracts_employee_count():
    extractor = FactExtractor()

    text = """
    About Example AS.
    Employees: 250.
    """

    facts = extractor.extract(text)

    fact = next(
        fact
        for fact in facts
        if fact.field_name == "employee_count"
    )

    assert fact.value == "250"
    assert fact.confidence == 0.90


def test_extracts_employee_count_from_norwegian_label():
    extractor = FactExtractor()

    text = """
    Example AS har 125 ansatte.
    """

    facts = extractor.extract(text)

    fact = next(
        fact
        for fact in facts
        if fact.field_name == "employee_count"
    )

    assert fact.value == "125"


def test_extracts_founded_year():
    extractor = FactExtractor()

    text = """
    Example AS.
    Founded: 1998.
    """

    facts = extractor.extract(text)

    fact = next(
        fact
        for fact in facts
        if fact.field_name == "founded_year"
    )

    assert fact.value == "1998"
    assert fact.value_year == 1998


def test_extracts_email():
    extractor = FactExtractor()

    text = """
    Contact email: hello@example.com
    """

    facts = extractor.extract(text)

    fact = next(
        fact
        for fact in facts
        if fact.field_name == "email"
    )

    assert fact.value == "hello@example.com"
    assert fact.confidence == 0.95


def test_extracts_phone():
    extractor = FactExtractor()

    text = """
    Phone: +47 22 12 34 56
    """

    facts = extractor.extract(text)

    fact = next(
        fact
        for fact in facts
        if fact.field_name == "phone"
    )

    assert fact.value == "+47 22 12 34 56"


def test_extracts_country():
    extractor = FactExtractor()

    text = """
    Company: Example AS
    Country: Norway
    """

    facts = extractor.extract(text)

    fact = next(
        fact
        for fact in facts
        if fact.field_name == "country"
    )

    assert fact.value == "Norway"


def test_rejects_invalid_employee_count():
    extractor = FactExtractor()

    text = """
    Employees: 0
    """

    facts = extractor.extract(text)

    employee_facts = [
        fact
        for fact in facts
        if fact.field_name == "employee_count"
    ]

    assert employee_facts == []


def test_rejects_invalid_founded_year():
    extractor = FactExtractor()

    text = """
    Founded: 1500
    """

    facts = extractor.extract(text)

    founded_facts = [
        fact
        for fact in facts
        if fact.field_name == "founded_year"
    ]

    assert founded_facts == []


def test_evidence_is_preserved_for_new_fields():
    extractor = FactExtractor()

    text = """
    Example AS has approximately 500 employees.
    Employees: 500.
    """

    facts = extractor.extract(text)

    fact = next(
        fact
        for fact in facts
        if fact.field_name == "employee_count"
    )

    assert "Employees: 500" in fact.evidence_text