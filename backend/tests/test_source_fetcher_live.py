from backend.app.scrapers.source_fetcher import SourceFetcher


def test_live_fetch():

    fetcher = SourceFetcher()

    result = fetcher.fetch(
        "https://www.equinor.com"
    )

    print("\n--- SIGNALPOST LIVE FETCH ---")
    print("Success:", result.success)
    print("Status:", result.status_code)
    print("Content type:", result.content_type)
    print("Final URL:", result.final_url)
    print("Content length:", len(result.content))

    assert result.success is True
    assert result.status_code == 200
    assert len(result.content) > 0