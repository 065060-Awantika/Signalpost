from dataclasses import dataclass, field

from backend.app.scrapers.brreg_client import BrregClient
from backend.app.scrapers.source_discovery import (
    SourceCandidate,
    SourceDiscovery,
)
from backend.app.scrapers.source_fetcher import (
    SourceFetcher,
)
from backend.app.services.company_repository import (
    CompanyRepository,
)
from backend.app.services.evidence_ingestion import (
    EvidenceIngestionService,
)
from backend.app.services.fact_repository import FactRepository
from backend.app.services.registry_fact_extractor import (
    RegistryFactExtractor,
)
from backend.app.services.source_repository import (
    SourceRepository,
)


@dataclass
class ResearchSourceResult:
    """
    Result for one discovered source.
    """

    url: str
    source_type: str
    success: bool
    source_id: int | None = None
    fact_count: int = 0
    error: str | None = None


@dataclass
class CompanyResearchResult:
    """
    Complete result of a Signalpost company research run.
    """

    company_id: int
    organization_number: str
    legal_name: str
    registry_fact_count: int
    sources: list[ResearchSourceResult] = field(
        default_factory=list
    )

    @property
    def total_fact_count(self) -> int:
        """
        Total number of facts discovered during this run.
        """

        website_facts = sum(
            source.fact_count
            for source in self.sources
        )

        return (
            self.registry_fact_count
            + website_facts
        )


class CompanyResearchService:
    """
    Orchestrates the Signalpost company research pipeline.

    Pipeline:

        Organization Number
                ↓
             BRREG
                ↓
          Company Identity
                ↓
        Registry Facts
                ↓
        Source Discovery
                ↓
         Source Fetching
                ↓
        Evidence Ingestion
                ↓
        Entity Verification
                ↓
         Persisted Facts
    """

    def __init__(
        self,
        db,
        brreg_client: BrregClient | None = None,
        source_discovery: SourceDiscovery | None = None,
        source_fetcher: SourceFetcher | None = None,
        registry_fact_extractor: (
            RegistryFactExtractor | None
        ) = None,
        source_repository: SourceRepository | None = None,
        fact_repository: FactRepository | None = None,
        evidence_ingestion: (
            EvidenceIngestionService | None
        ) = None,
    ) -> None:
        self.db = db

        self.brreg_client = (
            brreg_client
            or BrregClient()
        )

        self.source_discovery = (
            source_discovery
            or SourceDiscovery()
        )

        self.source_fetcher = (
            source_fetcher
            or SourceFetcher()
        )

        self.registry_fact_extractor = (
            registry_fact_extractor
            or RegistryFactExtractor()
        )

        self.source_repository = (
            source_repository
            or SourceRepository(db)
        )

        self.fact_repository = (
            fact_repository
            or FactRepository(db)
        )

        self.evidence_ingestion = (
            evidence_ingestion
            or EvidenceIngestionService(
                source_repository=self.source_repository,
                fact_repository=self.fact_repository,
            )
        )

        self.company_repository = CompanyRepository(
            db
        )

    def research(
        self,
        organization_number: str,
    ) -> CompanyResearchResult:
        """
        Run the complete research process for one
        Norwegian organization number.
        """

        # -------------------------------------------------
        # 1. Resolve company identity through BRREG
        # -------------------------------------------------

        registry_company = (
            self.brreg_client.get_company(
                organization_number
            )
        )

        company = (
            self.company_repository.create_or_update(
                registry_company
            )
        )

        # -------------------------------------------------
        # 2. Persist official BRREG facts
        # -------------------------------------------------

        registry_facts = (
            self.registry_fact_extractor.extract(
                registry_company
            )
        )

        registry_source_url = (
            "https://data.brreg.no/"
            "enhetsregisteret/api/enheter/"
            f"{registry_company.organization_number}"
        )

        registry_source = (
            self.source_repository.create(
                url=registry_source_url,
                source_type="official_registry",
                title=(
                    "Norwegian Register of Business "
                    "Enterprises"
                ),
                publisher="BRREG",
            )
        )

        for fact in registry_facts:
            self.fact_repository.create(
                company_id=company.id,
                source_id=registry_source.id,
                fact=fact,
                verification_status="verified",
            )

        # -------------------------------------------------
        # 3. Discover public sources
        # -------------------------------------------------

        source_candidates = (
            self.source_discovery.discover(
                registry_company
            )
        )

        source_results: list[
            ResearchSourceResult
        ] = []

        # -------------------------------------------------
        # 4. Fetch and ingest discovered sources
        # -------------------------------------------------

        for candidate in source_candidates:

            # BRREG is already handled above.
            if (
                candidate.source_type
                == "official_registry"
            ):
                continue

            try:
                fetched = self.source_fetcher.fetch(
                    candidate.url
                )

                if not fetched.success:
                    source_results.append(
                        ResearchSourceResult(
                            url=candidate.url,
                            source_type=(
                                candidate.source_type
                            ),
                            success=False,
                            error=fetched.error,
                        )
                    )
                    continue

                ingestion_result = (
                    self.evidence_ingestion.ingest(
                        company_id=company.id,
                        source=candidate,
                        fetched=fetched,
                        target_organization_number=(
                            registry_company.organization_number
                        ),
                        target_company_name=(
                            registry_company.legal_name
                        ),
                        target_website=(
                            registry_company.website
                        ),
                        target_address=(
                            registry_company.address
                        ),
                    )
                )

                source_results.append(
                    ResearchSourceResult(
                        url=(
                            ingestion_result.source_url
                        ),
                        source_type=(
                            candidate.source_type
                        ),
                        success=True,
                        source_id=(
                            ingestion_result.source_id
                        ),
                        fact_count=len(
                            ingestion_result.facts
                        ),
                    )
                )

            except Exception as exc:
                source_results.append(
                    ResearchSourceResult(
                        url=candidate.url,
                        source_type=(
                            candidate.source_type
                        ),
                        success=False,
                        error=str(exc),
                    )
                )

        return CompanyResearchResult(
            company_id=company.id,
            organization_number=(
                company.organization_number
            ),
            legal_name=company.legal_name,
            registry_fact_count=len(
                registry_facts
            ),
            sources=source_results,
        )