import pytest

from backend.app.scrapers.brreg_client import BrregClient


def test_normalize_valid_organization_number():
    client = BrregClient()

    result = client._normalize_org_number(
        "923 609 016"
    )

    assert result == "923609016"


def test_reject_invalid_organization_number():
    client = BrregClient()

    with pytest.raises(ValueError):
        client._normalize_org_number(
            "12345"
        )


def test_parse_registry_response():
    client = BrregClient()

    sample_response = {
        "organisasjonsnummer": "123456789",
        "navn": "Example AS",
        "organisasjonsform": {
            "beskrivelse": "Aksjeselskap"
        },
        "forretningsadresse": {
            "adresse": ["Example Street 1"],
            "postnummer": "0001",
            "poststed": "Oslo",
            "kommune": "Oslo",
        },
        "naeringskode1": {
            "kode": "62.010",
            "beskrivelse": "Computer programming activities",
        },
        "hjemmeside": "https://example.com",
    }

    company = client._parse_company(
        sample_response
    )

    assert company.organization_number == "123456789"
    assert company.legal_name == "Example AS"
    assert company.company_type == "Aksjeselskap"
    assert company.city == "Oslo"
    assert company.industry_code == "62.010"
    assert company.website == "https://example.com"