from dataclasses import dataclass

from backend.app.scrapers.html_cleaner import HTMLCleaner
from backend.app.scrapers.source_discovery import SourceCandidate
from backend.app.scrapers.source_fetcher import FetchedSource
from backend.app.services.fact_extractor import (
    ExtractedFact,
    FactExtractor,
)
from backend.app.services.fact_repository import FactRepository
from backend.app.services.source_repository import SourceRepository
from backend.app.verification.company_fact_verifier import (
    CompanyFactVerifier,
)
from backend.app.verification.verification_result import (
    VerificationStatus,
)


@dataclass
class EvidenceIngestionResult:
    """
    Result produced after processing one fetched source.
    """

    source_id: int
    source_url: str
    facts: list[ExtractedFact]
    clean_text: str


class EvidenceIngestionService:
    """
    Converts a successfully fetched public source into
    persisted source and fact records.

    Pipeline:

        FetchedSource
            ↓
        HTMLCleaner
            ↓
        FactExtractor
            ↓
        CompanyFactVerifier
            ↓
        SourceRepository
            ↓
        FactRepository
    """

    def __init__(
        self,
        source_repository: SourceRepository,
        fact_repository: FactRepository,
        cleaner: HTMLCleaner | None = None,
        extractor: FactExtractor | None = None,
        fact_verifier: CompanyFactVerifier | None = None,
    ) -> None:
        self.source_repository = source_repository
        self.fact_repository = fact_repository
        self.cleaner = cleaner or HTMLCleaner()
        self.extractor = extractor or FactExtractor()
        self.fact_verifier = (
            fact_verifier or CompanyFactVerifier()
        )

    def ingest(
        self,
        company_id: int,
        source: SourceCandidate,
        fetched: FetchedSource,
        target_organization_number: str | None = None,
        target_company_name: str | None = None,
        target_website: str | None = None,
        target_address: str | None = None,
    ) -> EvidenceIngestionResult:
        """
        Process and persist one successfully fetched source.

        When target company identity is supplied, extracted facts
        are verified before persistence.

        Verification behavior:

        - VERIFIED → facts are persisted as verified.
        - REVIEW → facts are persisted as review.
        - REJECTED → extracted facts are not persisted.

        The identity parameters are optional to preserve backwards
        compatibility for standalone ingestion callers and tests.
        """

        if not fetched.success:
            raise ValueError(
                "Cannot ingest a failed source fetch."
            )

        if not fetched.content.strip():
            raise ValueError(
                "Cannot ingest an empty source."
            )

        source_url = (
            fetched.final_url
            or fetched.url
            or source.url
        )

        source_record = self.source_repository.create(
            url=source_url,
            source_type=source.source_type,
            raw_content=fetched.content,
        )

        clean_text = self.cleaner.clean(
            fetched.content
        )

        extracted_facts = self.extractor.extract(
            clean_text
        )

        # -------------------------------------------------
        # Verify extracted facts against target company
        # -------------------------------------------------

        verification_status = "pending"

        if (
            target_organization_number
            and target_company_name
        ):
            verification_result = (
                self.fact_verifier.verify_facts(
                    target_organization_number=(
                        target_organization_number
                    ),
                    target_company_name=(
                        target_company_name
                    ),
                    target_website=target_website,
                    target_address=target_address,
                    facts=extracted_facts,
                )
            )

            if (
                verification_result.status
                == VerificationStatus.REJECTED
            ):
                # Do not persist potentially mismatched
                # company facts.
                return EvidenceIngestionResult(
                    source_id=source_record.id,
                    source_url=source_url,
                    facts=[],
                    clean_text=clean_text,
                )

            if (
                verification_result.status
                == VerificationStatus.VERIFIED
            ):
                verification_status = "verified"

            elif (
                verification_result.status
                == VerificationStatus.REVIEW
            ):
                verification_status = "review"

        # -------------------------------------------------
        # Persist verified/review/pending facts
        # -------------------------------------------------

        persisted_facts: list[ExtractedFact] = []

        for fact in extracted_facts:
            self.fact_repository.create(
                company_id=company_id,
                source_id=source_record.id,
                fact=fact,
                verification_status=verification_status,
            )

            persisted_facts.append(fact)

        return EvidenceIngestionResult(
            source_id=source_record.id,
            source_url=source_url,
            facts=persisted_facts,
            clean_text=clean_text,
        )