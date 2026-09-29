from backend.app.scrapers.html_cleaner import HTMLCleaner
from backend.app.scrapers.source_fetcher import SourceFetcher
from backend.app.services.fact_extractor import FactExtractor


def test_live_equinor_fact_extraction():
    url = "https://www.equinor.com"

    fetcher = SourceFetcher()
    fetched = fetcher.fetch(url)

    assert fetched.success is True
    assert fetched.content

    cleaner = HTMLCleaner()
    clean_text = cleaner.clean(
        fetched.content
    )

    assert clean_text

    extractor = FactExtractor()
    facts = extractor.extract(
        clean_text
    )

    print(
        "\n========== LIVE FACT EXTRACTION =========="
    )

    print(
        "URL:",
        fetched.final_url,
    )

    print(
        "Clean text length:",
        len(clean_text),
    )

    print(
        "Total facts:",
        len(facts),
    )

    for fact in facts:
        print(
            f"\nField: {fact.field_name}"
        )

        print(
            f"Value: {fact.value}"
        )

        print(
            f"Confidence: {fact.confidence}"
        )

        print(
            f"Year: {fact.value_year}"
        )

        print(
            f"Evidence: "
            f"{fact.evidence_text[:300]}"
        )

    print(
        "\n=========================================="
    )

    assert len(facts) >= 0