from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database.database import Base, get_db
from backend.app.main import app
from backend.app.scrapers.brreg_client import (
    RegistryCompany,
)
from backend.app.services.company_research_service import (
    CompanyResearchResult,
    ResearchSourceResult,
)


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

    return engine, session_factory


def test_research_endpoint():
    engine, session_factory = create_test_database()

    def override_get_db():
        db = session_factory()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[
        get_db
    ] = override_get_db

    class FakeResearchService:
        def __init__(self, db):
            self.db = db

        def research(self, organization_number):
            assert organization_number == "123456789"

            return CompanyResearchResult(
                company_id=1,
                organization_number="123456789",
                legal_name="Example AS",
                registry_fact_count=10,
                sources=[
                    ResearchSourceResult(
                        url=(
                            "https://example.com"
                        ),
                        source_type="company_website",
                        success=True,
                        source_id=1,
                        fact_count=4,
                    )
                ],
            )

    original_service = (
        __import__(
            "backend.app.api.companies",
            fromlist=[
                "CompanyResearchService"
            ],
        )
    )

    original_class = (
        original_service.CompanyResearchService
    )

    original_service.CompanyResearchService = (
        FakeResearchService
    )

    try:
        client = TestClient(app)

        response = client.post(
            "/companies/123456789/research"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["company_id"] == 1
        assert (
            data["organization_number"]
            == "123456789"
        )
        assert (
            data["legal_name"]
            == "Example AS"
        )
        assert (
            data["registry_fact_count"]
            == 10
        )
        assert (
            data["total_fact_count"]
            == 14
        )

        assert len(data["sources"]) == 1

        assert (
            data["sources"][0]["url"]
            == "https://example.com"
        )

        assert (
            data["sources"][0]["fact_count"]
            == 4
        )

    finally:
        original_service.CompanyResearchService = (
            original_class
        )
        app.dependency_overrides.clear()
        engine.dispose()


def test_research_endpoint_returns_404_for_invalid_company():
    engine, session_factory = create_test_database()

    def override_get_db():
        db = session_factory()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[
        get_db
    ] = override_get_db

    class FailingResearchService:
        def __init__(self, db):
            self.db = db

        def research(self, organization_number):
            raise ValueError(
                "Company with organization number "
                f"{organization_number} was not found."
            )

    companies_module = __import__(
        "backend.app.api.companies",
        fromlist=[
            "CompanyResearchService"
        ],
    )

    original_class = (
        companies_module.CompanyResearchService
    )

    companies_module.CompanyResearchService = (
        FailingResearchService
    )

    try:
        client = TestClient(app)

        response = client.post(
            "/companies/999999999/research"
        )

        assert response.status_code == 404

        data = response.json()

        assert "not found" in data["detail"]

    finally:
        companies_module.CompanyResearchService = (
            original_class
        )
        app.dependency_overrides.clear()
        engine.dispose()