from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database.database import Base
from backend.app.models.company import Company
from backend.app.models.fact import CompanyFact
from backend.app.models.source import Source
from backend.app.services.fact_extractor import ExtractedFact
from backend.app.services.fact_repository import FactRepository


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


def create_test_source(db):
    source = Source(
        url="https://example.com/company",
        source_type="company_website",
        title="Example Company",
        publisher="Example",
        raw_content="Example company information.",
        content_hash="test-hash",
    )

    db.add(source)
    db.commit()
    db.refresh(source)

    return source


def test_create_fact():
    db = create_test_database()

    company = create_test_company(db)
    source = create_test_source(db)

    repository = FactRepository(db)

    extracted_fact = ExtractedFact(
        field_name="legal_name",
        value="Example AS",
        evidence_text="Company name: Example AS",
        confidence=0.95,
    )

    fact = repository.create(
        company_id=company.id,
        source_id=source.id,
        fact=extracted_fact,
        verification_status="verified",
    )

    assert fact.id is not None
    assert fact.company_id == company.id
    assert fact.source_id == source.id
    assert fact.field_name == "legal_name"
    assert fact.value == "Example AS"
    assert fact.evidence_text == "Company name: Example AS"
    assert fact.confidence == 0.95
    assert fact.verification_status == "verified"

    db.close()


def test_get_fact_by_id():
    db = create_test_database()

    company = create_test_company(db)
    source = create_test_source(db)

    repository = FactRepository(db)

    extracted_fact = ExtractedFact(
        field_name="industry",
        value="Computer programming",
        evidence_text="Industry: Computer programming",
        confidence=0.90,
    )

    created = repository.create(
        company_id=company.id,
        source_id=source.id,
        fact=extracted_fact,
    )

    found = repository.get_by_id(created.id)

    assert found is not None
    assert found.id == created.id
    assert found.value == "Computer programming"

    db.close()


def test_get_facts_by_company():
    db = create_test_database()

    company = create_test_company(db)
    source = create_test_source(db)

    repository = FactRepository(db)

    repository.create(
        company_id=company.id,
        source_id=source.id,
        fact=ExtractedFact(
            field_name="legal_name",
            value="Example AS",
            evidence_text="Company name: Example AS",
            confidence=0.95,
        ),
    )

    repository.create(
        company_id=company.id,
        source_id=source.id,
        fact=ExtractedFact(
            field_name="industry",
            value="Computer programming",
            evidence_text="Industry: Computer programming",
            confidence=0.90,
        ),
    )

    facts = repository.get_by_company(company.id)

    assert len(facts) == 2
    assert facts[0].field_name == "legal_name"
    assert facts[1].field_name == "industry"

    db.close()


def test_get_facts_by_company_and_field():
    db = create_test_database()

    company = create_test_company(db)
    source = create_test_source(db)

    repository = FactRepository(db)

    repository.create(
        company_id=company.id,
        source_id=source.id,
        fact=ExtractedFact(
            field_name="legal_name",
            value="Example AS",
            evidence_text="Company name: Example AS",
            confidence=0.95,
        ),
    )

    repository.create(
        company_id=company.id,
        source_id=source.id,
        fact=ExtractedFact(
            field_name="industry",
            value="Computer programming",
            evidence_text="Industry: Computer programming",
            confidence=0.90,
        ),
    )

    legal_name_facts = repository.get_by_company_and_field(
        company.id,
        "legal_name",
    )

    assert len(legal_name_facts) == 1
    assert legal_name_facts[0].value == "Example AS"

    db.close()


def test_get_facts_by_source():
    db = create_test_database()

    company = create_test_company(db)
    source = create_test_source(db)

    repository = FactRepository(db)

    repository.create(
        company_id=company.id,
        source_id=source.id,
        fact=ExtractedFact(
            field_name="legal_name",
            value="Example AS",
            evidence_text="Company name: Example AS",
            confidence=0.95,
        ),
    )

    repository.create(
        company_id=company.id,
        source_id=source.id,
        fact=ExtractedFact(
            field_name="website",
            value="https://example.com",
            evidence_text="Website: https://example.com",
            confidence=0.95,
        ),
    )

    facts = repository.get_by_source(source.id)

    assert len(facts) == 2
    assert all(
        fact.source_id == source.id
        for fact in facts
    )

    db.close()


def test_value_year_is_preserved():
    db = create_test_database()

    company = create_test_company(db)
    source = create_test_source(db)

    repository = FactRepository(db)

    extracted_fact = ExtractedFact(
        field_name="revenue",
        value="1000000",
        evidence_text="Revenue in 2025: 1000000",
        confidence=0.90,
        value_year=2025,
    )

    fact = repository.create(
        company_id=company.id,
        source_id=source.id,
        fact=extracted_fact,
    )

    assert fact.value_year == 2025

    db.close()