from dataclasses import dataclass

from backend.app.services.company_research_service import (
    CompanyResearchService,
)


@dataclass
class BulkResearchResult:
    organization_number: str
    success: bool
    legal_name: str | None
    fact_count: int
    error: str | None = None


class BulkResearchService:
    """Research multiple companies sequentially."""

    def __init__(
        self,
        research_service: CompanyResearchService,
    ) -> None:
        self.research_service = research_service

    def research_companies(
        self,
        organization_numbers: list[str],
    ) -> list[BulkResearchResult]:
        results: list[BulkResearchResult] = []

        for organization_number in organization_numbers:
            normalized = "".join(
                character
                for character in organization_number
                if character.isdigit()
            )

            if len(normalized) != 9:
                results.append(
                    BulkResearchResult(
                        organization_number=organization_number,
                        success=False,
                        legal_name=None,
                        fact_count=0,
                        error=(
                            "Invalid Norwegian organization "
                            "number."
                        ),
                    )
                )
                continue

            try:
                result = self.research_service.research(
                    normalized
                )

                results.append(
                    BulkResearchResult(
                        organization_number=normalized,
                        success=True,
                        legal_name=result.legal_name,
                        fact_count=result.total_fact_count,
                    )
                )

            except Exception as exc:
                results.append(
                    BulkResearchResult(
                        organization_number=normalized,
                        success=False,
                        legal_name=None,
                        fact_count=0,
                        error=str(exc),
                    )
                )

        return results