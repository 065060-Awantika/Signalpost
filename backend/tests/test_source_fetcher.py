import requests

from backend.app.scrapers.source_fetcher import (
    SourceFetcher,
)


class FakeResponse:

    def __init__(
        self,
        status_code=200,
        url="https://example.com",
        content_type="text/html",
        content=b"<html>Hello</html>",
        headers=None,
        encoding="utf-8",
    ):
        self.status_code = status_code
        self.url = url
        self.encoding = encoding
        self.headers = headers or {
            "content-type": content_type,
        }
        self._content = content

    def iter_content(
        self,
        chunk_size=16384,
    ):
        yield self._content

    def close(self):
        pass


def test_successful_fetch(monkeypatch):

    def fake_get(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(
        requests,
        "get",
        fake_get,
    )

    fetcher = SourceFetcher()

    result = fetcher.fetch(
        "https://example.com"
    )

    assert result.success is True
    assert result.status_code == 200
    assert result.content == "<html>Hello</html>"
    assert result.content_type == "text/html"


def test_http_error(monkeypatch):

    def fake_get(*args, **kwargs):
        return FakeResponse(
            status_code=404,
            content=b"",
        )

    monkeypatch.setattr(
        requests,
        "get",
        fake_get,
    )

    fetcher = SourceFetcher()

    result = fetcher.fetch(
        "https://example.com/missing"
    )

    assert result.success is False
    assert result.status_code == 404
    assert result.error == "HTTP 404"


def test_timeout(monkeypatch):

    def fake_get(*args, **kwargs):
        raise requests.Timeout()

    monkeypatch.setattr(
        requests,
        "get",
        fake_get,
    )

    fetcher = SourceFetcher()

    result = fetcher.fetch(
        "https://example.com"
    )

    assert result.success is False
    assert result.status_code == 0
    assert result.error == "Request timed out."


def test_response_size_limit(monkeypatch):

    def fake_get(*args, **kwargs):
        return FakeResponse(
            content=b"1234567890",
        )

    monkeypatch.setattr(
        requests,
        "get",
        fake_get,
    )

    fetcher = SourceFetcher(
        max_content_size=5
    )

    result = fetcher.fetch(
        "https://example.com"
    )

    assert result.success is False
    assert result.error == (
        "Response exceeds maximum size."
    )