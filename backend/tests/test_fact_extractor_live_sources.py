from backend.app.scrapers.brreg_client import BrregClient
from backend.app.scrapers.html_cleaner import HTMLCleaner
from backend.app.scrapers.source_discovery import SourceDiscovery
from backend.app.scrapers.source_fetcher import SourceFetcher
from backend.app.services.fact_extractor import FactExtractor


def test_live_equinor_multi_source_extraction():
    organization_number = "923609016"

    brreg = BrregClient()
    company = brreg.get_company(
        organization_number
    )

    discovery = SourceDiscovery()
    sources = discovery.discover(company)

    fetcher = SourceFetcher()
    cleaner = HTMLCleaner()
    extractor = FactExtractor()

    total_facts = 0
    successful_sources = 0

    print(
        "\n========== MULTI-SOURCE FACT EXTRACTION =========="
    )

    print(
        "Company:",
        company.legal_name,
    )

    print(
        "Organization number:",
        company.organization_number,
    )

    print(
        "Discovered sources:",
        len(sources),
    )

    for source in sources:
        # Skip BRREG here because this test is measuring
        # extraction from public web pages.
        if source.source_type != "company_website":
            continue

        print(
            "\n--------------------------------------------------"
        )

        print(
            "URL:",
            source.url,
        )

        fetched = fetcher.fetch(
            source.url
        )

        print(
            "Success:",
            fetched.success,
        )

        if not fetched.success:
            print(
                "Error:",
                fetched.error,
            )
            continue

        successful_sources += 1

        clean_text = cleaner.clean(
            fetched.content
        )

        facts = extractor.extract(
            clean_text
        )

        total_facts += len(facts)

        print(
            "Clean text length:",
            len(clean_text),
        )

        print(
            "Facts:",
            len(facts),
        )

        for fact in facts:
            print(
                "  -",
                fact.field_name,
                "=",
                fact.value,
                "| confidence:",
                fact.confidence,
            )

    print(
        "\n=================================================="
    )

    print(
        "Successful website sources:",
        successful_sources,
    )

    print(
        "Total extracted facts:",
        total_facts,
    )

    print(
        "=================================================="
    )

    assert company.organization_number == (
        organization_number
    )

    assert company.legal_name == (
        "EQUINOR ASA"
    )

    assert successful_sources >= 1

    assert total_facts >= 1