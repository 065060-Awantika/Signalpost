from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.database.database import get_db
from backend.app.models.change import FactChange
from backend.app.models.company import Company


router = APIRouter(
    prefix="/companies",
    tags=["changes"],
)


@router.get("/{organization_number}/changes")
def get_company_changes(
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

    changes = list(
        db.scalars(
            select(FactChange)
            .where(
                FactChange.company_id == company.id
            )
            .order_by(
                FactChange.detected_at.desc(),
                FactChange.id.desc(),
            )
        ).all()
    )

    return {
        "company": {
            "organization_number": company.organization_number,
            "legal_name": company.legal_name,
        },
        "summary": {
            "total_changes": len(changes),
            "modified": sum(
                change.change_type == "modified"
                for change in changes
            ),
            "added": sum(
                change.change_type == "added"
                for change in changes
            ),
            "removed": sum(
                change.change_type == "removed"
                for change in changes
            ),
        },
        "changes": [
            {
                "id": change.id,
                "field_name": change.field_name,
                "change_type": change.change_type,
                "previous_value": change.previous_value,
                "current_value": change.current_value,
                "previous_fact_id": change.previous_fact_id,
                "current_fact_id": change.current_fact_id,
                "detected_at": (
                    change.detected_at.isoformat()
                    if isinstance(
                        change.detected_at,
                        datetime,
                    )
                    else None
                ),
            }
            for change in changes
        ],
    }