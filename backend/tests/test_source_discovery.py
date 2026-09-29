from backend.app.scrapers.brreg_client import RegistryCompany
from backend.app.scrapers.source_discovery import (
    SourceDiscovery,
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
        industry_description="Utvinning av råolje",
        website="www.equinor.com",
    )


def test_discovery_returns_official_registry():

    discovery = SourceDiscovery()

    sources = discovery.discover(
        sample_company()
    )

    registry_sources = [
        source
        for source in sources
        if source.source_type == "official_registry"
    ]

    assert len(registry_sources) == 1

    assert (
        "923609016"
        in registry_sources[0].url
    )


def test_discovery_returns_company_website():

    discovery = SourceDiscovery()

    sources = discovery.discover(
        sample_company()
    )

    website_sources = [
        source
        for source in sources
        if source.source_type == "company_website"
    ]

    assert len(website_sources) >= 1

    assert any(
        "equinor.com"
        in source.url
        for source in website_sources
    )


def test_discovery_does_not_create_duplicate_urls():

    discovery = SourceDiscovery()

    sources = discovery.discover(
        sample_company()
    )

    urls = [
        source.url.rstrip("/")
        for source in sources
    ]

    assert len(urls) == len(set(urls))


def test_website_is_normalized():

    discovery = SourceDiscovery()

    company = sample_company()

    company.website = "https://www.example.com/"

    sources = discovery.discover(company)

    assert any(
        source.url == "https://www.example.com"
        for source in sources
    )