from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database.database import Base
from backend.app.models.company import Company
from backend.app.models.fact import CompanyFact
from backend.app.models.source import Source
from backend.app.scrapers.source_discovery import SourceCandidate
from backend.app.scrapers.source_fetcher import FetchedSource
from backend.app.services.evidence_ingestion import (
    EvidenceIngestionService,
)
from backend.app.services.fact_extractor import (
    FactExtractor,
)
from backend.app.services.fact_repository import FactRepository
from backend.app.services.source_repository import SourceRepository


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


def create_test_company(db):
    company = Company(
        organization_number="123456789",
        legal_name="Example AS",
        company_type="Aksjeselskap",
        address="Example Street 1",
        website="https://example.com",
        industry="Computer programming",
    )

    db.add(company)
    db.commit()
    db.refresh(company)

    return company


def create_service(db):
    return EvidenceIngestionService(
        source_repository=SourceRepository(db),
        fact_repository=FactRepository(db),
        extractor=FactExtractor(),
    )


def create_source_candidate():
    return SourceCandidate(
        url="https://example.com/company",
        source_type="company_website",
        priority=1,
        reason="Company website.",
    )


def create_fetched_source():
    content = """
    <html>
        <head>
            <title>Example Company</title>
        </head>
        <body>
            <main>
                <h1>Example AS</h1>
                <p>Company name: Example AS</p>
                <p>Organization number: 123456789</p>
                <p>Website: https://example.com</p>
                <p>Industry: Computer programming</p>
                <p>Address: Example Street 1</p>
                <p>City: Oslo</p>
            </main>
        </body>
    </html>
    """

    return FetchedSource(
        url="https://example.com/company",
        final_url="https://example.com/company",
        status_code=200,
        content_type="text/html",
        content=content,
        success=True,
    )


def test_ingestion_creates_source_and_facts():
    db = create_test_database()

    company = create_test_company(db)

    service = create_service(db)

    result = service.ingest(
        company_id=company.id,
        source=create_source_candidate(),
        fetched=create_fetched_source(),
    )

    assert result.source_id is not None
    assert result.source_url == "https://example.com/company"
    assert result.clean_text

    source = (
        db.query(Source)
        .filter(Source.id == result.source_id)
        .first()
    )

    assert source is not None
    assert source.url == "https://example.com/company"
    assert source.source_type == "company_website"
    assert source.raw_content

    facts = (
        db.query(CompanyFact)
        .filter(
            CompanyFact.company_id == company.id
        )
        .all()
    )

    assert len(facts) >= 4

    db.close()


def test_all_facts_link_to_same_source():
    db = create_test_database()

    company = create_test_company(db)

    service = create_service(db)

    result = service.ingest(
        company_id=company.id,
        source=create_source_candidate(),
        fetched=create_fetched_source(),
    )

    facts = (
        db.query(CompanyFact)
        .filter(
            CompanyFact.company_id == company.id
        )
        .all()
    )

    assert len(facts) >= 4

    assert all(
        fact.source_id == result.source_id
        for fact in facts
    )

    db.close()


def test_ingested_facts_start_as_pending():
    db = create_test_database()

    company = create_test_company(db)

    service = create_service(db)

    result = service.ingest(
        company_id=company.id,
        source=create_source_candidate(),
        fetched=create_fetched_source(),
    )

    facts = (
        db.query(CompanyFact)
        .filter(
            CompanyFact.company_id == company.id
        )
        .all()
    )

    assert len(facts) >= 4

    assert all(
        fact.verification_status == "pending"
        for fact in facts
    )

    db.close()


def test_failed_fetch_is_rejected():
    db = create_test_database()

    company = create_test_company(db)

    service = create_service(db)

    failed_source = FetchedSource(
        url="https://example.com/company",
        final_url="https://example.com/company",
        status_code=500,
        content_type="text/html",
        content="",
        success=False,
        error="HTTP 500",
    )

    try:
        service.ingest(
            company_id=company.id,
            source=create_source_candidate(),
            fetched=failed_source,
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "failed source fetch" in str(exc)

    db.close()


def test_empty_source_is_rejected():
    db = create_test_database()

    company = create_test_company(db)

    service = create_service(db)

    empty_source = FetchedSource(
        url="https://example.com/company",
        final_url="https://example.com/company",
        status_code=200,
        content_type="text/html",
        content="",
        success=True,
    )

    try:
        service.ingest(
            company_id=company.id,
            source=create_source_candidate(),
            fetched=empty_source,
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "empty source" in str(exc)

    db.close()


def test_final_url_is_used_for_source_record():
    db = create_test_database()

    company = create_test_company(db)

    service = create_service(db)

    fetched = FetchedSource(
        url="https://example.com",
        final_url="https://example.com/company",
        status_code=200,
        content_type="text/html",
        content="""
        <html>
            <body>
                <main>
                    <p>Company name: Example AS</p>
                </main>
            </body>
        </html>
        """,
        success=True,
    )

    result = service.ingest(
        company_id=company.id,
        source=SourceCandidate(
            url="https://example.com",
            source_type="company_website",
            priority=1,
            reason="Company website.",
        ),
        fetched=fetched,
    )

    source = (
        db.query(Source)
        .filter(Source.id == result.source_id)
        .first()
    )

    assert source is not None
    assert source.url == "https://example.com/company"

    db.close()