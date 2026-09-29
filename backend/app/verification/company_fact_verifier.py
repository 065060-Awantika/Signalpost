from backend.app.services.fact_extractor import ExtractedFact
from backend.app.verification.entity_verifier import EntityVerifier
from backend.app.verification.verification_result import (
    VerificationResult,
    VerificationStatus,
)


class CompanyFactVerifier:
    """
    Connects extracted source facts to the existing
    EntityVerifier.

    This class does not implement a second verification system.
    It adapts ExtractedFact objects to the existing
    EntityVerifier contract.
    """

    def __init__(
        self,
        entity_verifier: EntityVerifier | None = None,
    ) -> None:
        self.entity_verifier = (
            entity_verifier
            or EntityVerifier()
        )

    def verify_facts(
        self,
        *,
        target_organization_number: str,
        target_company_name: str,
        target_website: str | None = None,
        target_address: str | None = None,
        facts: list[ExtractedFact],
    ) -> VerificationResult:
        """
        Verify a collection of extracted facts against
        the known target company.
        """

        source_organization_number = (
            self._get_fact_value(
                facts,
                "organization_number",
            )
        )

        source_company_name = (
            self._get_fact_value(
                facts,
                "legal_name",
            )
        )

        source_website = (
            self._get_fact_value(
                facts,
                "website",
            )
        )

        source_address = (
            self._get_fact_value(
                facts,
                "address",
            )
        )

        return self.entity_verifier.verify(
            target_organization_number=(
                target_organization_number
            ),
            target_company_name=(
                target_company_name
            ),
            target_website=target_website,
            target_address=target_address,
            source_organization_number=(
                source_organization_number
            ),
            source_company_name=(
                source_company_name
            ),
            source_website=source_website,
            source_address=source_address,
        )

    @staticmethod
    def _get_fact_value(
        facts: list[ExtractedFact],
        field_name: str,
    ) -> str | None:
        """
        Return the first extracted value for a field.
        """

        for fact in facts:
            if fact.field_name == field_name:
                return fact.value

        return None

    @staticmethod
    def should_persist(
        result: VerificationResult,
    ) -> bool:
        """
        Decide whether a source's facts have passed
        automatic identity verification.

        VERIFIED facts can be persisted as verified.

        REVIEW facts may still be persisted, but must remain
        explicitly marked for review.

        REJECTED facts should not be trusted for automatic
        company-profile updates.
        """

        return result.status != (
            VerificationStatus.REJECTED
        )