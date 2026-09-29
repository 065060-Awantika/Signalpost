from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database.database import Base
from backend.app.models.company import Company
from backend.app.models.fact import CompanyFact
from backend.app.models.source import Source
from backend.app.scrapers.brreg_client import RegistryCompany
from backend.app.scrapers.source_discovery import SourceCandidate
from backend.app.scrapers.source_fetcher import FetchedSource
from backend.app.services.company_research_service import (
    CompanyResearchService,
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

    return session_factory()


def sample_registry_company():
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


class FakeBrregClient:
    def get_company(self, organization_number):
        assert organization_number == "123456789"
        return sample_registry_company()


class FakeSourceDiscovery:
    def discover(self, company):
        assert company.organization_number == "123456789"

        return [
            SourceCandidate(
                url=(
                    "https://data.brreg.no/"
                    "enhetsregisteret/api/enheter/"
                    "123456789"
                ),
                source_type="official_registry",
                priority=1,
                reason="Official registry.",
            ),
            SourceCandidate(
                url="https://example.com/company",
                source_type="company_website",
                priority=1,
                reason="Company website.",
            ),
        ]


class FakeSourceFetcher:
    def fetch(self, url):
        assert url == "https://example.com/company"

        content = """
        <html>
            <head>
                <title>Example AS</title>
            </head>
            <body>
                <main>
                    <h1>Example AS</h1>
                    <p>Company name: Example AS</p>
                    <p>
                        Organization number: 123456789
                    </p>
                    <p>
                        Website: https://example.com
                    </p>
                    <p>
                        Industry: Computer programming
                    </p>
                    <p>
                        Address: Example Street 1
                    </p>
                    <p>
                        City: Oslo
                    </p>
                </main>
            </body>
        </html>
        """

        return FetchedSource(
            url=url,
            final_url=url,
            status_code=200,
            content_type="text/html",
            content=content,
            success=True,
        )


def test_research_creates_company_and_registry_facts():
    db = create_test_database()

    service = CompanyResearchService(
        db=db,
        brreg_client=FakeBrregClient(),
        source_discovery=FakeSourceDiscovery(),
        source_fetcher=FakeSourceFetcher(),
    )

    result = service.research(
        "123456789"
    )

    assert result.company_id is not None
    assert result.organization_number == "123456789"
    assert result.legal_name == "Example AS"

    # The registry extractor can evolve as additional
    # official BRREG fields are added.
    assert result.registry_fact_count >= 10

    company = (
        db.query(Company)
        .filter(
            Company.organization_number
            == "123456789"
        )
        .first()
    )

    assert company is not None
    assert company.legal_name == "Example AS"

    # Find the official BRREG source specifically.
    registry_source = (
        db.query(Source)
        .filter(
            Source.source_type
            == "official_registry"
        )
        .first()
    )

    assert registry_source is not None

    # Only facts belonging to the BRREG source should
    # be counted as registry facts.
    registry_facts = (
        db.query(CompanyFact)
        .filter(
            CompanyFact.company_id == company.id,
            CompanyFact.source_id == registry_source.id,
            CompanyFact.verification_status
            == "verified",
        )
        .all()
    )

    assert len(registry_facts) == result.registry_fact_count

    db.close()


def test_research_ingests_and_verifies_website_facts():
    db = create_test_database()

    service = CompanyResearchService(
        db=db,
        brreg_client=FakeBrregClient(),
        source_discovery=FakeSourceDiscovery(),
        source_fetcher=FakeSourceFetcher(),
    )

    result = service.research(
        "123456789"
    )

    assert len(result.sources) == 1

    website_result = result.sources[0]

    assert website_result.success is True
    assert (
        website_result.url
        == "https://example.com/company"
    )
    assert website_result.source_id is not None

    # The fake source contains multiple identity and
    # company facts, all belonging to the target company.
    assert website_result.fact_count >= 4

    company_facts = (
        db.query(CompanyFact)
        .filter(
            CompanyFact.company_id
            == result.company_id
        )
        .all()
    )

    website_facts = [
        fact
        for fact in company_facts
        if fact.source_id
        == website_result.source_id
    ]

    assert len(website_facts) >= 4

    # The source contains the correct organization number,
    # company name and website, so its facts should now be
    # automatically verified rather than left pending.
    assert all(
        fact.verification_status == "verified"
        for fact in website_facts
    )

    db.close()


def test_registry_source_is_not_fetched_twice():
    db = create_test_database()

    service = CompanyResearchService(
        db=db,
        brreg_client=FakeBrregClient(),
        source_discovery=FakeSourceDiscovery(),
        source_fetcher=FakeSourceFetcher(),
    )

    service.research(
        "123456789"
    )

    sources = (
        db.query(Source)
        .order_by(Source.id)
        .all()
    )

    registry_sources = [
        source
        for source in sources
        if source.source_type
        == "official_registry"
    ]

    website_sources = [
        source
        for source in sources
        if source.source_type
        == "company_website"
    ]

    assert len(registry_sources) == 1
    assert len(website_sources) == 1

    db.close()


def test_failed_website_does_not_fail_entire_research():
    db = create_test_database()

    class FailingSourceFetcher:
        def fetch(self, url):
            return FetchedSource(
                url=url,
                final_url=url,
                status_code=500,
                content_type="text/html",
                content="",
                success=False,
                error="HTTP 500",
            )

    service = CompanyResearchService(
        db=db,
        brreg_client=FakeBrregClient(),
        source_discovery=FakeSourceDiscovery(),
        source_fetcher=FailingSourceFetcher(),
    )

    result = service.research(
        "123456789"
    )

    assert result.company_id is not None
    assert result.registry_fact_count >= 10

    assert len(result.sources) == 1
    assert result.sources[0].success is False
    assert result.sources[0].error == "HTTP 500"

    db.close()


def test_total_fact_count_includes_registry_and_website_facts():
    db = create_test_database()

    service = CompanyResearchService(
        db=db,
        brreg_client=FakeBrregClient(),
        source_discovery=FakeSourceDiscovery(),
        source_fetcher=FakeSourceFetcher(),
    )

    result = service.research(
        "123456789"
    )

    assert result.registry_fact_count >= 10
    assert result.sources[0].fact_count >= 4

    assert (
        result.total_fact_count
        == (
            result.registry_fact_count
            + result.sources[0].fact_count
        )
    )

    db.close()