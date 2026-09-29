from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.fact import CompanyFact
from backend.app.services.fact_extractor import ExtractedFact


class FactRepository:
    """
    Handles persistence and retrieval of company facts.

    Every fact is linked to both a company and the source
    from which the evidence was extracted.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        company_id: int,
        source_id: int,
        fact: ExtractedFact,
        verification_status: str = "pending",
    ) -> CompanyFact:
        """
        Save an extracted fact and link it to its source.
        """

        company_fact = CompanyFact(
            company_id=company_id,
            source_id=source_id,
            field_name=fact.field_name,
            value=fact.value,
            value_year=fact.value_year,
            evidence_text=fact.evidence_text,
            confidence=fact.confidence,
            verification_status=verification_status,
        )

        self.db.add(company_fact)
        self.db.commit()
        self.db.refresh(company_fact)

        return company_fact

    def get_by_id(
        self,
        fact_id: int,
    ) -> CompanyFact | None:
        """
        Retrieve a fact by its database ID.
        """

        statement = select(CompanyFact).where(
            CompanyFact.id == fact_id
        )

        return self.db.execute(
            statement
        ).scalars().first()

    def get_by_company(
        self,
        company_id: int,
    ) -> list[CompanyFact]:
        """
        Retrieve all facts belonging to a company.
        """

        statement = (
            select(CompanyFact)
            .where(
                CompanyFact.company_id == company_id
            )
            .order_by(CompanyFact.id)
        )

        return list(
            self.db.execute(
                statement
            ).scalars().all()
        )

    def get_by_company_and_field(
        self,
        company_id: int,
        field_name: str,
    ) -> list[CompanyFact]:
        """
        Retrieve all observations of a particular field
        for a company.

        Keeping multiple observations allows Signalpost to
        preserve historical evidence from different sources.
        """

        statement = (
            select(CompanyFact)
            .where(
                CompanyFact.company_id == company_id,
                CompanyFact.field_name == field_name,
            )
            .order_by(
                CompanyFact.created_at.desc()
            )
        )

        return list(
            self.db.execute(
                statement
            ).scalars().all()
        )

    def get_by_source(
        self,
        source_id: int,
    ) -> list[CompanyFact]:
        """
        Retrieve all facts extracted from a particular source.
        """

        statement = (
            select(CompanyFact)
            .where(
                CompanyFact.source_id == source_id
            )
            .order_by(CompanyFact.id)
        )

        return list(
            self.db.execute(
                statement
            ).scalars().all()
        )