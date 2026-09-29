from backend.app.verification.entity_verifier import EntityVerifier
from backend.app.verification.verification_result import VerificationStatus


def test_matching_company_is_verified():
    verifier = EntityVerifier()

    result = verifier.verify(
        target_organization_number="123456789",
        target_company_name="Example AS",
        target_website="https://www.example.no",
        target_address="Oslo",
        source_organization_number="123456789",
        source_company_name="Example AS",
        source_website="https://www.example.no",
        source_address="Oslo",
    )

    assert result.status == VerificationStatus.VERIFIED
    assert result.organization_number_match is True
    assert result.company_name_match is True
    assert result.website_match is True


def test_wrong_organization_number_is_rejected():
    verifier = EntityVerifier()

    result = verifier.verify(
        target_organization_number="123456789",
        target_company_name="Example AS",
        target_website="https://www.example.no",
        source_organization_number="987654321",
        source_company_name="Example AS",
        source_website="https://www.example.no",
    )

    assert result.status == VerificationStatus.REJECTED
    assert result.organization_number_match is False


def test_partial_identity_requires_review():
    verifier = EntityVerifier()

    result = verifier.verify(
        target_organization_number="123456789",
        target_company_name="Example AS",
        source_company_name="Example AS",
    )

    assert result.status == VerificationStatus.REVIEW