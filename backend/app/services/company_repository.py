from sqlalchemy.orm import Session

from backend.app.models.company import Company
from backend.app.scrapers.brreg_client import RegistryCompany


class CompanyRepository:
    """Database operations for Signalpost companies."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_organization_number(
        self,
        organization_number: str,
    ) -> Company | None:

        return (
            self.db.query(Company)
            .filter(
                Company.organization_number
                == organization_number
            )
            .first()
        )

    def create_or_update(
        self,
        registry_company: RegistryCompany,
    ) -> Company:

        existing = self.get_by_organization_number(
            registry_company.organization_number
        )

        if existing:
            existing.legal_name = registry_company.legal_name
            existing.company_type = registry_company.company_type
            existing.website = registry_company.website
            existing.address = registry_company.address
            existing.industry = (
                registry_company.industry_description
            )

            self.db.commit()
            self.db.refresh(existing)

            return existing

        company = Company(
            organization_number=(
                registry_company.organization_number
            ),
            legal_name=registry_company.legal_name,
            company_type=registry_company.company_type,
            website=registry_company.website,
            address=registry_company.address,
            industry=registry_company.industry_description,
        )

        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)

        return company