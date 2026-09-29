import re
from urllib.parse import urlparse

from backend.app.verification.verification_result import (
    VerificationResult,
    VerificationStatus,
)


class EntityVerifier:
    """
    Deterministic company identity verifier.

    The verifier compares source identity facts against the target company
    and produces a single verification result.

    Verification rules:
    - A conflicting organization number always rejects the source.
    - A matching organization number strongly verifies the source.
    - Company name + website together can verify the source even when
      an organization number is unavailable.
    - Partial or weak evidence goes to review.
    """

    def verify(
        self,
        *,
        target_organization_number: str,
        target_company_name: str,
        target_website: str | None = None,
        target_address: str | None = None,
        source_organization_number: str | None = None,
        source_company_name: str | None = None,
        source_website: str | None = None,
        source_address: str | None = None,
    ) -> VerificationResult:
        reasons: list[str] = []

        org_match = self._match_organization_number(
            target_organization_number,
            source_organization_number,
        )

        name_match = self._match_company_name(
            target_company_name,
            source_company_name,
        )

        website_match = self._match_website(
            target_website,
            source_website,
        )

        address_match = self._match_text(
            target_address,
            source_address,
        )

        # Explain the identity evidence.
        if source_organization_number:
            if org_match:
                reasons.append("Organization number matches the target company.")
            else:
                reasons.append("Organization number conflicts with the target company.")

        if source_company_name:
            if name_match:
                reasons.append("Company name matches the target company.")
            else:
                reasons.append("Company name does not match the target company.")

        if source_website:
            if website_match:
                reasons.append("Website domain matches the target company.")
            else:
                reasons.append("Website domain does not match the target company.")

        if source_address:
            if address_match:
                reasons.append("Address matches the target company.")
            else:
                reasons.append("Address does not match the target company.")

        score = self._calculate_score(
            org_match=org_match,
            name_match=name_match,
            website_match=website_match,
            address_match=address_match,
            source_organization_number=source_organization_number,
            source_company_name=source_company_name,
            source_website=source_website,
            source_address=source_address,
        )

        # A direct organization-number conflict is always rejected.
        if source_organization_number and not org_match:
            status = VerificationStatus.REJECTED
            reasons.append(
                "Source organization number conflicts with the target organization number."
            )

        # A matching organization number is the strongest identity evidence.
        elif org_match:
            status = VerificationStatus.VERIFIED

        # Two independent supporting identity signals are sufficient
        # when the organization number is unavailable.
        elif name_match and website_match:
            status = VerificationStatus.VERIFIED
            reasons.append(
                "Company name and website independently match the target company."
            )

        # Otherwise retain the existing review threshold.
        elif score >= 0.80:
            status = VerificationStatus.VERIFIED

        else:
            status = VerificationStatus.REVIEW
            reasons.append(
                "Identity evidence is insufficient for automatic verification."
            )

        return VerificationResult(
            status=status,
            score=round(score, 3),
            organization_number_match=org_match,
            company_name_match=name_match,
            website_match=website_match,
            address_match=address_match,
            reasons=reasons,
        )

    @staticmethod
    def _normalize_text(value: str | None) -> str:
        if not value:
            return ""

        value = value.lower().strip()

        value = re.sub(
            r"[^a-z0-9æøåäöüéèàç]+",
            " ",
            value,
        )

        return " ".join(value.split())

    @classmethod
    def _match_organization_number(
        cls,
        target: str | None,
        source: str | None,
    ) -> bool:
        if not target or not source:
            return False

        target_digits = "".join(character for character in target if character.isdigit())
        source_digits = "".join(character for character in source if character.isdigit())

        return (
            bool(target_digits)
            and bool(source_digits)
            and target_digits == source_digits
        )

    @classmethod
    def _match_company_name(
        cls,
        target: str | None,
        source: str | None,
    ) -> bool:
        if not target or not source:
            return False

        normalized_target = cls._normalize_text(target)
        normalized_source = cls._normalize_text(source)

        if not normalized_target or not normalized_source:
            return False

        if normalized_target == normalized_source:
            return True

        return (
            normalized_target in normalized_source
            or normalized_source in normalized_target
        )

    @staticmethod
    def _extract_domain(value: str | None) -> str:
        if not value:
            return ""

        candidate = value.strip()

        if not candidate.startswith(("http://", "https://")):
            candidate = f"https://{candidate}"

        try:
            parsed = urlparse(candidate)
        except ValueError:
            return ""

        domain = parsed.netloc.lower().strip()

        if domain.startswith("www."):
            domain = domain[4:]

        return domain

    @classmethod
    def _match_website(
        cls,
        target: str | None,
        source: str | None,
    ) -> bool:
        if not target or not source:
            return False

        target_domain = cls._extract_domain(target)
        source_domain = cls._extract_domain(source)

        return (
            bool(target_domain)
            and bool(source_domain)
            and target_domain == source_domain
        )

    @classmethod
    def _match_text(
        cls,
        target: str | None,
        source: str | None,
    ) -> bool:
        if not target or not source:
            return False

        normalized_target = cls._normalize_text(target)
        normalized_source = cls._normalize_text(source)

        if not normalized_target or not normalized_source:
            return False

        return (
            normalized_target in normalized_source
            or normalized_source in normalized_target
        )

    @staticmethod
    def _calculate_score(
        *,
        org_match: bool,
        name_match: bool,
        website_match: bool,
        address_match: bool,
        source_organization_number: str | None,
        source_company_name: str | None,
        source_website: str | None,
        source_address: str | None,
    ) -> float:
        score = 0.0

        if org_match:
            score += 0.60
        elif source_organization_number:
            score -= 0.60

        if name_match:
            score += 0.20
        elif source_company_name:
            score -= 0.20

        if website_match:
            score += 0.15
        elif source_website:
            score -= 0.15

        if address_match:
            score += 0.05
        elif source_address:
            score -= 0.05

        return max(0.0, min(1.0, score))