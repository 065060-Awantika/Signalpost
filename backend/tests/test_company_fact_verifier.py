from backend.app.services.fact_extractor import ExtractedFact
from backend.app.verification.company_fact_verifier import (
    CompanyFactVerifier,
)
from backend.app.verification.verification_result import (
    VerificationStatus,
)


def test_matching_facts_are_verified():
    verifier = CompanyFactVerifier()

    facts = [
        ExtractedFact(
            field_name="organization_number",
            value="123456789",
            evidence_text=(
                "Organization number: 123456789"
            ),
            confidence=0.98,
        ),
        ExtractedFact(
            field_name="legal_name",
            value="Example AS",
            evidence_text=(
                "Company name: Example AS"
            ),
            confidence=0.90,
        ),
        ExtractedFact(
            field_name="website",
            value="https://example.com",
            evidence_text=(
                "Website: https://example.com"
            ),
            confidence=0.95,
        ),
    ]

    result = verifier.verify_facts(
        target_organization_number="123456789",
        target_company_name="Example AS",
        target_website="https://example.com",
        facts=facts,
    )

    assert result.status == (
        VerificationStatus.VERIFIED
    )

    assert result.organization_number_match is True
    assert result.company_name_match is True
    assert result.website_match is True

    assert verifier.should_persist(
        result
    ) is True


def test_conflicting_organization_number_is_rejected():
    verifier = CompanyFactVerifier()

    facts = [
        ExtractedFact(
            field_name="organization_number",
            value="987654321",
            evidence_text=(
                "Organization number: 987654321"
            ),
            confidence=0.98,
        ),
        ExtractedFact(
            field_name="legal_name",
            value="Example AS",
            evidence_text=(
                "Company name: Example AS"
            ),
            confidence=0.90,
        ),
    ]

    result = verifier.verify_facts(
        target_organization_number="123456789",
        target_company_name="Example AS",
        facts=facts,
    )

    assert result.status == (
        VerificationStatus.REJECTED
    )

    assert result.organization_number_match is False

    assert verifier.should_persist(
        result
    ) is False


def test_insufficient_identity_evidence_requires_review():
    verifier = CompanyFactVerifier()

    facts = [
        ExtractedFact(
            field_name="employee_count",
            value="250",
            evidence_text=(
                "The company has 250 employees."
            ),
            confidence=0.90,
        )
    ]

    result = verifier.verify_facts(
        target_organization_number="123456789",
        target_company_name="Example AS",
        facts=facts,
    )

    assert result.status == (
        VerificationStatus.REVIEW
    )

    assert verifier.should_persist(
        result
    ) is True


def test_supporting_identity_facts_can_verify_without_org_number():
    verifier = CompanyFactVerifier()

    facts = [
        ExtractedFact(
            field_name="legal_name",
            value="Example AS",
            evidence_text=(
                "Company name: Example AS"
            ),
            confidence=0.90,
        ),
        ExtractedFact(
            field_name="website",
            value="https://example.com",
            evidence_text=(
                "Website: https://example.com"
            ),
            confidence=0.95,
        ),
    ]

    result = verifier.verify_facts(
        target_organization_number="123456789",
        target_company_name="Example AS",
        target_website="https://example.com",
        facts=facts,
    )

    assert result.status == (
        VerificationStatus.VERIFIED
    )

    assert result.company_name_match is True
    assert result.website_match is True