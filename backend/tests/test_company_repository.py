from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database.database import Base
from backend.app.models.company import Company
from backend.app.scrapers.brreg_client import RegistryCompany
from backend.app.services.company_repository import CompanyRepository


def create_test_database():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(bind=engine)

    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    return session_factory()


def sample_company():
    return RegistryCompany(
        organization_number="123456789",
        legal_name="Example AS",
        company_type="Aksjeselskap",
        address="Example Street 1",
        postal_code="0001",
        city="Oslo",
        municipality="Oslo",
        industry_code="62.010",
        industry_description="Computer programming",
        website="https://example.com",
    )


def test_company_is_created():
    db = create_test_database()

    repository = CompanyRepository(db)

    company = repository.create_or_update(
        sample_company()
    )

    assert company.id is not None
    assert company.organization_number == "123456789"
    assert company.legal_name == "Example AS"

    db.close()


def test_existing_company_is_updated():
    db = create_test_database()

    repository = CompanyRepository(db)

    first = repository.create_or_update(
        sample_company()
    )

    updated = RegistryCompany(
        organization_number="123456789",
        legal_name="Example Updated AS",
        company_type="Aksjeselskap",
        address="New Street 10",
        postal_code="0002",
        city="Oslo",
        municipality="Oslo",
        industry_code="62.010",
        industry_description="Updated industry",
        website="https://updated-example.com",
    )

    second = repository.create_or_update(
        updated
    )

    assert first.id == second.id
    assert second.legal_name == "Example Updated AS"
    assert second.address == "New Street 10"
    assert second.website == "https://updated-example.com"

    db.close()


def test_same_organization_number_does_not_create_duplicate():
    db = create_test_database()

    repository = CompanyRepository(db)

    repository.create_or_update(
        sample_company()
    )

    repository.create_or_update(
        sample_company()
    )

    companies = (
        db.query(Company)
        .filter(
            Company.organization_number
            == "123456789"
        )
        .all()
    )

    assert len(companies) == 1

    db.close()