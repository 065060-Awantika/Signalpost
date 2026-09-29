from backend.app.scrapers.brreg_client import RegistryCompany
from backend.app.services.fact_extractor import ExtractedFact


class RegistryFactExtractor:
    """
    Converts an official BRREG RegistryCompany record into
    structured ExtractedFact objects.

    BRREG is treated as a high-trust official source.
    """

    def extract(
        self,
        company: RegistryCompany,
    ) -> list[ExtractedFact]:

        facts: list[ExtractedFact] = []

        # ---------------------------------------------------------
        # Organization number
        # ---------------------------------------------------------

        if company.organization_number:
            facts.append(
                ExtractedFact(
                    field_name="organization_number",
                    value=company.organization_number,
                    evidence_text=(
                        "Official BRREG organization number: "
                        f"{company.organization_number}"
                    ),
                    confidence=0.99,
                )
            )

        # ---------------------------------------------------------
        # Legal name
        # ---------------------------------------------------------

        if company.legal_name:
            facts.append(
                ExtractedFact(
                    field_name="legal_name",
                    value=company.legal_name,
                    evidence_text=(
                        "Official BRREG legal name: "
                        f"{company.legal_name}"
                    ),
                    confidence=0.99,
                )
            )

        # ---------------------------------------------------------
        # Company type
        # ---------------------------------------------------------

        if company.company_type:
            facts.append(
                ExtractedFact(
                    field_name="company_type",
                    value=company.company_type,
                    evidence_text=(
                        "Official BRREG company type: "
                        f"{company.company_type}"
                    ),
                    confidence=0.99,
                )
            )

        # ---------------------------------------------------------
        # Address
        # ---------------------------------------------------------

        if company.address:
            facts.append(
                ExtractedFact(
                    field_name="address",
                    value=company.address,
                    evidence_text=(
                        "Official BRREG business address: "
                        f"{company.address}"
                    ),
                    confidence=0.98,
                )
            )

        # ---------------------------------------------------------
        # Postal code
        # ---------------------------------------------------------

        if company.postal_code:
            facts.append(
                ExtractedFact(
                    field_name="postal_code",
                    value=company.postal_code,
                    evidence_text=(
                        "Official BRREG postal code: "
                        f"{company.postal_code}"
                    ),
                    confidence=0.98,
                )
            )

        # ---------------------------------------------------------
        # City
        # ---------------------------------------------------------

        if company.city:
            facts.append(
                ExtractedFact(
                    field_name="city",
                    value=company.city,
                    evidence_text=(
                        "Official BRREG city: "
                        f"{company.city}"
                    ),
                    confidence=0.98,
                )
            )

        # ---------------------------------------------------------
        # Municipality
        # ---------------------------------------------------------

        if company.municipality:
            facts.append(
                ExtractedFact(
                    field_name="municipality",
                    value=company.municipality,
                    evidence_text=(
                        "Official BRREG municipality: "
                        f"{company.municipality}"
                    ),
                    confidence=0.98,
                )
            )

        # ---------------------------------------------------------
        # Industry code
        # ---------------------------------------------------------

        if company.industry_code:
            facts.append(
                ExtractedFact(
                    field_name="industry_code",
                    value=company.industry_code,
                    evidence_text=(
                        "Official BRREG industry code: "
                        f"{company.industry_code}"
                    ),
                    confidence=0.99,
                )
            )

        # ---------------------------------------------------------
        # Industry description
        # ---------------------------------------------------------

        if company.industry_description:
            facts.append(
                ExtractedFact(
                    field_name="industry",
                    value=company.industry_description,
                    evidence_text=(
                        "Official BRREG industry description: "
                        f"{company.industry_description}"
                    ),
                    confidence=0.99,
                )
            )

        # ---------------------------------------------------------
        # Website
        # ---------------------------------------------------------

        if company.website:
            facts.append(
                ExtractedFact(
                    field_name="website",
                    value=company.website,
                    evidence_text=(
                        "Official BRREG registered website: "
                        f"{company.website}"
                    ),
                    confidence=0.98,
                )
            )

        return facts