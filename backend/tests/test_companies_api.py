from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.main import app
from backend.app.database.database import Base, get_db
from backend.app.scrapers.brreg_client import RegistryCompany


# ---------------------------------------------------------
# Test database
# ---------------------------------------------------------

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def override_get_db():
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# ---------------------------------------------------------
# Fake Brreg response
# ---------------------------------------------------------

def fake_get_company(
    self,
    organization_number: str,
):
    return RegistryCompany(
        organization_number="123456789",
        legal_name="Test Company AS",
        company_type="Aksjeselskap",
        address="Test Street 1",
        postal_code="0001",
        city="Oslo",
        municipality="Oslo",
        industry_code="62.010",
        industry_description="Computer programming",
        website="https://testcompany.no",
    )


# ---------------------------------------------------------
# Tests
# ---------------------------------------------------------

def test_get_company_returns_company(
    monkeypatch,
):

    monkeypatch.setattr(
        "backend.app.api.companies.BrregClient.get_company",
        fake_get_company,
    )

    response = client.get(
        "/companies/123456789"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["organization_number"] == "123456789"
    assert data["legal_name"] == "Test Company AS"
    assert data["company_type"] == "Aksjeselskap"
    assert data["website"] == "https://testcompany.no"


def test_get_company_creates_database_record(
    monkeypatch,
):

    monkeypatch.setattr(
        "backend.app.api.companies.BrregClient.get_company",
        fake_get_company,
    )

    response = client.get(
        "/companies/123456789"
    )

    assert response.status_code == 200
    assert response.json()["id"] is not None


def test_invalid_registry_company_returns_404(
    monkeypatch,
):

    def fake_not_found(
        self,
        organization_number: str,
    ):
        raise ValueError(
            "Company with organization number "
            "999999999 was not found."
        )

    monkeypatch.setattr(
        "backend.app.api.companies.BrregClient.get_company",
        fake_not_found,
    )

    response = client.get(
        "/companies/999999999"
    )

    assert response.status_code == 404