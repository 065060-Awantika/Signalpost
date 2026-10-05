from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.database.database import get_db
from backend.app.models.company import Company
from backend.app.models.fact import CompanyFact
from backend.app.models.source import Source


router = APIRouter(
    prefix="/companies",
    tags=["intelligence"],
)


def normalize_url(url: str) -> str:
    """
    Normalize URLs so technically identical URLs are treated
    as the same source.
    """
    normalized = url.strip().rstrip("/")

    if normalized.startswith("https://"):
        normalized = normalized[:-1] if normalized.endswith("/") else normalized

    return normalized


def source_timestamp(source: Source) -> datetime:
    return source.retrieved_at or datetime.min


def fact_priority(fact: CompanyFact) -> tuple:
    """
    Prefer stronger records when duplicate facts exist.
    """
    status_priority = {
        "verified": 3,
        "review": 2,
        "pending": 1,
        "rejected": 0,
    }

    return (
        status_priority.get(
            (fact.verification_status or "").lower(),
            0,
        ),
        fact.confidence or 0.0,
        fact.id,
    )


@router.get("/{organization_number}/facts")
def get_company_intelligence(
    organization_number: str,
    db: Session = Depends(get_db),
):
    normalized_number = "".join(
        character
        for character in organization_number
        if character.isdigit()
    )

    if len(normalized_number) != 9:
        raise HTTPException(
            status_code=400,
            detail=(
                "Norwegian organization number must "
                "contain exactly 9 digits."
            ),
        )

    company = db.scalar(
        select(Company).where(
            Company.organization_number == normalized_number
        )
    )

    if company is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Company {normalized_number} "
                "has not been researched yet."
            ),
        )

    rows = db.execute(
        select(CompanyFact, Source)
        .join(
            Source,
            CompanyFact.source_id == Source.id,
        )
        .where(
            CompanyFact.company_id == company.id
        )
    ).all()

    # ---------------------------------------------------------
    # SOURCE DEDUPLICATION
    # ---------------------------------------------------------
    #
    # Multiple research runs can create multiple Source rows
    # pointing to the same URL. Keep the latest source record
    # for the API response.
    #
    source_by_url: dict[str, Source] = {}

    for _, source in rows:
        key = normalize_url(source.url)

        existing = source_by_url.get(key)

        if existing is None:
            source_by_url[key] = source
            continue

        if source_timestamp(source) > source_timestamp(existing):
            source_by_url[key] = source

    # ---------------------------------------------------------
    # FACT DEDUPLICATION
    # ---------------------------------------------------------
    #
    # Keep separate facts when the evidence comes from
    # different sources. Remove only repeated copies of the
    # same field + value + source URL.
    #
    fact_by_key: dict[tuple, CompanyFact] = {}

    for fact, source in rows:
        source_key = normalize_url(source.url)

        key = (
            fact.field_name.strip().lower(),
            fact.value.strip().lower(),
            source_key,
        )

        existing = fact_by_key.get(key)

        if existing is None:
            fact_by_key[key] = fact
            continue

        if fact_priority(fact) > fact_priority(existing):
            fact_by_key[key] = fact

    # ---------------------------------------------------------
    # BUILD SOURCE RESPONSE
    # ---------------------------------------------------------

    source_map = {}

    for source in source_by_url.values():
        source_map[source.id] = {
            "id": source.id,
            "url": source.url,
            "title": source.title,
            "source_type": source.source_type,
            "publisher": source.publisher,
            "published_at": (
                source.published_at.isoformat()
                if isinstance(
                    source.published_at,
                    datetime,
                )
                else None
            ),
            "retrieved_at": (
                source.retrieved_at.isoformat()
                if isinstance(
                    source.retrieved_at,
                    datetime,
                )
                else None
            ),
            "fact_count": 0,
        }

    # ---------------------------------------------------------
    # BUILD FACT RESPONSE
    # ---------------------------------------------------------

    facts = []

    for fact in sorted(
        fact_by_key.values(),
        key=lambda item: (
            item.field_name.lower(),
            item.id,
        ),
    ):
        source = db.get(
            Source,
            fact.source_id,
        )

        if source is None:
            continue

        # If the source was deduplicated away, attach the fact
        # to the canonical/latest source URL.
        canonical_source = source_by_url.get(
            normalize_url(source.url)
        )

        if canonical_source is None:
            continue

        source_entry = source_map.get(
            canonical_source.id
        )

        if source_entry is not None:
            source_entry["fact_count"] += 1

        facts.append(
            {
                "id": fact.id,
                "field_name": fact.field_name,
                "value": fact.value,
                "value_year": fact.value_year,
                "evidence_text": fact.evidence_text,
                "confidence": fact.confidence,
                "verification_status": fact.verification_status,
                "source": {
                    "id": canonical_source.id,
                    "url": canonical_source.url,
                    "title": canonical_source.title,
                    "source_type": canonical_source.source_type,
                    "publisher": canonical_source.publisher,
                    "published_at": (
                        canonical_source.published_at.isoformat()
                        if isinstance(
                            canonical_source.published_at,
                            datetime,
                        )
                        else None
                    ),
                    "retrieved_at": (
                        canonical_source.retrieved_at.isoformat()
                        if isinstance(
                            canonical_source.retrieved_at,
                            datetime,
                        )
                        else None
                    ),
                },
            }
        )

    # Remove sources that have no surviving facts.
    sources = [
        source
        for source in source_map.values()
        if source["fact_count"] > 0
    ]

    # ---------------------------------------------------------
    # SUMMARY METRICS
    # ---------------------------------------------------------

    verified_facts = sum(
        1
        for fact in facts
        if fact["verification_status"] == "verified"
    )

    review_facts = sum(
        1
        for fact in facts
        if fact["verification_status"] == "review"
    )

    pending_facts = sum(
        1
        for fact in facts
        if fact["verification_status"] == "pending"
    )

    rejected_facts = sum(
        1
        for fact in facts
        if fact["verification_status"] == "rejected"
    )

    registry_source_ids = {
        source["id"]
        for source in sources
        if source["source_type"] == "official_registry"
    }

    registry_fact_count = sum(
        1
        for fact in facts
        if fact["source"]["id"] in registry_source_ids
    )

    return {
        "company": {
            "id": company.id,
            "organization_number": company.organization_number,
            "legal_name": company.legal_name,
            "company_type": company.company_type,
            "website": company.website,
            "address": company.address,
            "industry": company.industry,
            "created_at": (
                company.created_at.isoformat()
                if isinstance(
                    company.created_at,
                    datetime,
                )
                else None
            ),
            "updated_at": (
                company.updated_at.isoformat()
                if isinstance(
                    company.updated_at,
                    datetime,
                )
                else None
            ),
        },
        "facts": facts,
        "sources": sources,
        "summary": {
            "total_facts": len(facts),
            "registry_facts": registry_fact_count,
            "verified_facts": verified_facts,
            "review_facts": review_facts,
            "pending_facts": pending_facts,
            "rejected_facts": rejected_facts,
            "sources_checked": len(sources),
        },
    }