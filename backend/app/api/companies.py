from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.database import get_db
from backend.app.scrapers.brreg_client import BrregClient
from backend.app.services.company_repository import (
    CompanyRepository,
)
from backend.app.services.company_research_service import (
    CompanyResearchService,
)


router = APIRouter(
    prefix="/companies",
    tags=["companies"],
)


@router.get("/{organization_number}")
def get_company(
    organization_number: str,
    db: Session = Depends(get_db),
):
    """
    Fetch a Norwegian company from BRREG,
    save/update it in our database,
    and return the company profile.
    """

    brreg = BrregClient()

    try:
        registry_company = brreg.get_company(
            organization_number
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Registry request failed: {exc}",
        )

    repository = CompanyRepository(db)

    company = repository.create_or_update(
        registry_company
    )

    return {
        "id": company.id,
        "organization_number": company.organization_number,
        "legal_name": company.legal_name,
        "company_type": company.company_type,
        "website": company.website,
        "address": company.address,
        "industry": company.industry,
    }


@router.post("/{organization_number}/research")
def research_company(
    organization_number: str,
    db: Session = Depends(get_db),
):
    """
    Run the complete Signalpost research pipeline
    for a Norwegian organization number.

    The pipeline resolves the company through BRREG,
    discovers public sources, fetches them, extracts
    facts, and persists evidence.
    """

    service = CompanyResearchService(
        db=db
    )

    try:
        result = service.research(
            organization_number
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Company research failed: {exc}",
        )

    return {
        "company_id": result.company_id,
        "organization_number": (
            result.organization_number
        ),
        "legal_name": result.legal_name,
        "registry_fact_count": (
            result.registry_fact_count
        ),
        "total_fact_count": (
            result.total_fact_count
        ),
        "sources": [
            {
                "url": source.url,
                "source_type": source.source_type,
                "success": source.success,
                "source_id": source.source_id,
                "fact_count": source.fact_count,
                "error": source.error,
            }
            for source in result.sources
        ],
    }