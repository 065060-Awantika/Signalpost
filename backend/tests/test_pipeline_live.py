from backend.app.scrapers.source_fetcher import SourceFetcher
from backend.app.scrapers.html_cleaner import HTMLCleaner
from backend.app.services.fact_extractor import FactExtractor


def test_live_company_pipeline():

    url = "https://www.equinor.com"

    # 1. Fetch
    fetcher = SourceFetcher()

    fetched = fetcher.fetch(url)

    assert fetched.success is True
    assert fetched.status_code == 200
    assert fetched.content

    print("\n========== SIGNALPOST PIPELINE ==========")
    print("Source:", fetched.final_url)
    print("Status:", fetched.status_code)
    print("Raw HTML:", len(fetched.content), "characters")

    # 2. Clean HTML
    cleaner = HTMLCleaner()

    clean_text = cleaner.clean(
        fetched.content
    )

    print("CLEAN TEXT:", repr(clean_text))
    print("CLEAN TEXT LENGTH:", len(clean_text))

    assert clean_text

    print("Clean text:", len(clean_text), "characters")

    # 3. Extract facts
    extractor = FactExtractor()

    facts = extractor.extract(
        clean_text
    )

    print("\n========== EXTRACTED FACTS ==========")

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
            f"Evidence: {fact.evidence_text[:250]}"
        )

    print(
        "\nTotal facts:",
        len(facts),
    )

    # We only require the pipeline to
    # successfully process the live page.
    assert len(facts) >= 0