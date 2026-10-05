from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.change import FactChange


class ChangeRepository:
    """Database operations for detected fact changes."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        company_id: int,
        field_name: str,
        change_type: str,
        previous_value: str | None,
        current_value: str | None,
        previous_fact_id: int | None,
        current_fact_id: int | None,
    ) -> FactChange:
        change = FactChange(
            company_id=company_id,
            field_name=field_name,
            change_type=change_type,
            previous_value=previous_value,
            current_value=current_value,
            previous_fact_id=previous_fact_id,
            current_fact_id=current_fact_id,
        )

        self.db.add(change)
        self.db.commit()
        self.db.refresh(change)

        return change

    def get_by_company(
        self,
        company_id: int,
    ) -> list[FactChange]:
        statement = (
            select(FactChange)
            .where(
                FactChange.company_id == company_id
            )
            .order_by(
                FactChange.detected_at.desc()
            )
        )

        return list(
            self.db.scalars(statement).all()
        )

    def get_by_fact_pair(
        self,
        *,
        company_id: int,
        previous_fact_id: int,
        current_fact_id: int,
    ) -> FactChange | None:
        statement = (
            select(FactChange)
            .where(
                FactChange.company_id == company_id,
                FactChange.previous_fact_id
                == previous_fact_id,
                FactChange.current_fact_id
                == current_fact_id,
            )
        )

        return self.db.scalar(statement)