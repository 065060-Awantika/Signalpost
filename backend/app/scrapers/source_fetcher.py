from dataclasses import dataclass
from typing import Optional

import requests


@dataclass
class FetchedSource:
    url: str
    final_url: str
    status_code: int
    content_type: str
    content: str
    success: bool
    error: Optional[str] = None


class SourceFetcher:
    """
    Fetches public HTTP/HTTPS sources for Signalpost.

    This component is deliberately separate from source discovery:
    discovery decides WHAT to fetch;
    fetcher handles HOW to fetch it.
    """

    def __init__(
        self,
        timeout: int = 15,
        max_content_size: int = 2_000_000,
    ) -> None:
        self.timeout = timeout
        self.max_content_size = max_content_size

        self.headers = {
            "User-Agent": (
                "Signalpost/0.1 "
                "(company-research-agent)"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,"
                "application/json;q=0.9,*/*;q=0.8"
            ),
        }

    def fetch(
        self,
        url: str,
    ) -> FetchedSource:

        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True,
                stream=True,
            )

            content_type = (
                response.headers.get(
                    "content-type",
                    "",
                )
                .split(";")[0]
                .strip()
                .lower()
            )

            if response.status_code >= 400:
                response.close()

                return FetchedSource(
                    url=url,
                    final_url=response.url,
                    status_code=response.status_code,
                    content_type=content_type,
                    content="",
                    success=False,
                    error=(
                        f"HTTP {response.status_code}"
                    ),
                )

            content_length = response.headers.get(
                "content-length"
            )

            if content_length:
                try:
                    if int(content_length) > self.max_content_size:
                        response.close()

                        return FetchedSource(
                            url=url,
                            final_url=response.url,
                            status_code=response.status_code,
                            content_type=content_type,
                            content="",
                            success=False,
                            error="Response exceeds maximum size.",
                        )
                except ValueError:
                    pass

            body = bytearray()

            for chunk in response.iter_content(
                chunk_size=16_384
            ):
                if not chunk:
                    continue

                body.extend(chunk)

                if len(body) > self.max_content_size:
                    response.close()

                    return FetchedSource(
                        url=url,
                        final_url=response.url,
                        status_code=response.status_code,
                        content_type=content_type,
                        content="",
                        success=False,
                        error="Response exceeds maximum size.",
                    )

            response.close()

            encoding = response.encoding or "utf-8"

            content = bytes(body).decode(
                encoding,
                errors="replace",
            )

            return FetchedSource(
                url=url,
                final_url=response.url,
                status_code=response.status_code,
                content_type=content_type,
                content=content,
                success=True,
            )

        except requests.Timeout:

            return FetchedSource(
                url=url,
                final_url=url,
                status_code=0,
                content_type="",
                content="",
                success=False,
                error="Request timed out.",
            )

        except requests.RequestException as exc:

            return FetchedSource(
                url=url,
                final_url=url,
                status_code=0,
                content_type="",
                content="",
                success=False,
                error=f"Request failed: {exc}",
            )