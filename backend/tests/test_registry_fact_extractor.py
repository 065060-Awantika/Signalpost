from backend.app.scrapers.brreg_client import RegistryCompany
from backend.app.services.registry_fact_extractor import (
    RegistryFactExtractor,
)


def sample_company():
    return RegistryCompany(
        organization_number="923609016",
        legal_name="EQUINOR ASA",
        company_type="Allmennaksjeselskap",
        address="Forusbeen 50",
        postal_code="4035",
        city="Stavanger",
        municipality="Stavanger",
        industry_code="06.100",
        industry_description="Extraction of crude petroleum",
        website="www.equinor.com",
    )


def test_extracts_registry_facts():

    extractor = RegistryFactExtractor()

    facts = extractor.extract(
        sample_company()
    )

    fields = {
        fact.field_name
        for fact in facts
    }

    assert "organization_number" in fields
    assert "legal_name" in fields
    assert "company_type" in fields
    assert "address" in fields
    assert "postal_code" in fields
    assert "city" in fields
    assert "municipality" in fields
    assert "industry_code" in fields
    assert "industry" in fields
    assert "website" in fields


def test_organization_number_has_high_confidence():

    extractor = RegistryFactExtractor()

    facts = extractor.extract(
        sample_company()
    )

    fact = next(
        fact
        for fact in facts
        if fact.field_name == "organization_number"
    )

    assert fact.value == "923609016"
    assert fact.confidence >= 0.99


def test_registry_evidence_is_preserved():

    extractor = RegistryFactExtractor()

    facts = extractor.extract(
        sample_company()
    )

    fact = next(
        fact
        for fact in facts
        if fact.field_name == "legal_name"
    )

    assert fact.value == "EQUINOR ASA"
    assert "BRREG" in fact.evidence_text


def test_empty_registry_fields_are_skipped():

    extractor = RegistryFactExtractor()

    company = RegistryCompany(
        organization_number="123456789",
        legal_name="Example AS",
        company_type=None,
        address=None,
        postal_code=None,
        city=None,
        municipality=None,
        industry_code=None,
        industry_description=None,
        website=None,
    )

    facts = extractor.extract(company)

    fields = {
        fact.field_name
        for fact in facts
    }

    assert fields == {
        "organization_number",
        "legal_name",
    }