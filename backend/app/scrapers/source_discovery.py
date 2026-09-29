from dataclasses import dataclass
from urllib.parse import urlparse

from backend.app.scrapers.brreg_client import RegistryCompany


@dataclass
class SourceCandidate:
    url: str
    source_type: str
    priority: int
    reason: str


class SourceDiscovery:
    """
    Generates candidate public sources for a company.

    This component only discovers sources.
    It does NOT download or scrape them yet.
    """

    def discover(
        self,
        company: RegistryCompany,
    ) -> list[SourceCandidate]:

        sources: list[SourceCandidate] = []

        # ---------------------------------------------------------
        # 1. Official Brønnøysund Registry
        # ---------------------------------------------------------

        brreg_url = (
            "https://data.brreg.no/enhetsregisteret/api/enheter/"
            f"{company.organization_number}"
        )

        sources.append(
            SourceCandidate(
                url=brreg_url,
                source_type="official_registry",
                priority=1,
                reason="Official Norwegian company registry record.",
            )
        )

        # ---------------------------------------------------------
        # 2. Official company website
        # ---------------------------------------------------------

        if company.website:
            website = self._normalize_website(
                company.website
            )

            sources.append(
                SourceCandidate(
                    url=website,
                    source_type="company_website",
                    priority=1,
                    reason="Company website listed by the official registry.",
                )
            )

        # ---------------------------------------------------------
        # 3. Common company-site pages
        # ---------------------------------------------------------

        if company.website:
            website = self._normalize_website(
                company.website
            ).rstrip("/")

            common_pages = [
                ("about", "Potential company/about information."),
                ("company", "Potential company information."),
                ("investors", "Potential investor information."),
                ("news", "Potential company news."),
                ("contact", "Potential company contact information."),
            ]

            for path, reason in common_pages:
                sources.append(
                    SourceCandidate(
                        url=f"{website}/{path}",
                        source_type="company_website",
                        priority=2,
                        reason=reason,
                    )
                )

        return self._deduplicate(sources)

    @staticmethod
    def _normalize_website(
        website: str,
    ) -> str:

        website = website.strip()

        if not website:
            return website

        if not website.startswith(
            ("http://", "https://")
        ):
            website = f"https://{website}"

        parsed = urlparse(website)

        if not parsed.netloc:
            raise ValueError(
                f"Invalid website URL: {website}"
            )

        return (
            f"{parsed.scheme}://"
            f"{parsed.netloc}"
        )

    @staticmethod
    def _deduplicate(
        sources: list[SourceCandidate],
    ) -> list[SourceCandidate]:

        seen: set[str] = set()
        unique_sources: list[SourceCandidate] = []

        for source in sources:
            normalized_url = source.url.rstrip("/")

            if normalized_url in seen:
                continue

            seen.add(normalized_url)
            unique_sources.append(source)

        return unique_sources