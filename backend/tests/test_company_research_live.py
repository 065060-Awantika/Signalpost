from backend.app.database.database import Base
from backend.app.database.database import SessionLocal
from backend.app.services.company_research_service import (
    CompanyResearchService,
)


def test_live_company_research():
    """
    Real integration test.

    This test makes public HTTP requests to BRREG and
    discovered company website sources.
    """

    db = SessionLocal()

    try:
        service = CompanyResearchService(
            db=db
        )

        result = service.research(
            "923609016"
        )

        print(
            "\n========== SIGNALPOST LIVE RESEARCH =========="
        )

        print(
            "Company:",
            result.legal_name,
        )

        print(
            "Organization number:",
            result.organization_number,
        )

        print(
            "Company ID:",
            result.company_id,
        )

        print(
            "Registry facts:",
            result.registry_fact_count,
        )

        print(
            "Total facts:",
            result.total_fact_count,
        )

        print(
            "\n========== SOURCES =========="
        )

        for source in result.sources:
            print(
                "\nURL:",
                source.url,
            )

            print(
                "Type:",
                source.source_type,
            )

            print(
                "Success:",
                source.success,
            )

            print(
                "Source ID:",
                source.source_id,
            )

            print(
                "Facts:",
                source.fact_count,
            )

            if source.error:
                print(
                    "Error:",
                    source.error,
                )

        print(
            "\n=============================================="
        )

        assert result.organization_number == (
            "923609016"
        )

        assert result.legal_name == (
            "EQUINOR ASA"
        )

        assert result.company_id is not None

        assert result.registry_fact_count > 0

        assert result.total_fact_count >= (
            result.registry_fact_count
        )

    finally:
        db.close()