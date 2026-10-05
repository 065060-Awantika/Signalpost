from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database.database import Base
from backend.app.models.company import Company
from backend.app.models.fact import CompanyFact
from backend.app.models.source import Source
from backend.app.services.change_detection_service import (
    ChangeDetectionService,
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


def create_fact(
    db,
    *,
    company_id,
    source_id,
    field_name,
    value,
    evidence_text,
    created_at,
    confidence=0.90,
    verification_status="verified",
):
    fact = CompanyFact(
        company_id=company_id,
        source_id=source_id,
        field_name=field_name,
        value=value,
        evidence_text=evidence_text,
        confidence=confidence,
        verification_status=verification_status,
        created_at=created_at,
    )

    db.add(fact)
    db.commit()
    db.refresh(fact)

    return fact


def test_change_detection_service_detects_modified_fact():
    db = create_test_database()

    company = create_test_company(db)
    source = create_test_source(db)

    old_fact = create_fact(
        db,
        company_id=company.id,
        source_id=source.id,
        field_name="employee_count",
        value="24,000",
        evidence_text="Previous employee count: 24,000",
        created_at=datetime(2026, 9, 1),
        confidence=0.90,
    )

    new_fact = create_fact(
        db,
        company_id=company.id,
        source_id=source.id,
        field_name="employee_count",
        value="25,000",
        evidence_text="Current employee count: 25,000",
        created_at=datetime(2026, 9, 30),
        confidence=0.90,
    )

    service = ChangeDetectionService(
        db=db,
    )

    changes = service.detect_for_company(
        company_id=company.id,
    )

    assert len(changes) == 1

    change = changes[0]

    assert change.field_name == "employee_count"
    assert change.change_type == "modified"
    assert change.previous_value == "24,000"
    assert change.current_value == "25,000"
    assert change.previous_fact_id == old_fact.id
    assert change.current_fact_id == new_fact.id

    db.close()


def test_change_detection_service_ignores_unchanged_fact():
    db = create_test_database()

    company = create_test_company(db)
    source = create_test_source(db)

    create_fact(
        db,
        company_id=company.id,
        source_id=source.id,
        field_name="employee_count",
        value="25,000",
        evidence_text="Employee count: 25,000",
        created_at=datetime(2026, 9, 1),
    )

    create_fact(
        db,
        company_id=company.id,
        source_id=source.id,
        field_name="employee_count",
        value=" 25,000 ",
        evidence_text="Employee count: 25,000",
        created_at=datetime(2026, 9, 30),
    )

    service = ChangeDetectionService(
        db=db,
    )

    changes = service.detect_for_company(
        company_id=company.id,
    )

    assert changes == []

    db.close()


def test_change_detection_service_ignores_city_field():
    db = create_test_database()

    company = create_test_company(db)
    source = create_test_source(db)

    create_fact(
        db,
        company_id=company.id,
        source_id=source.id,
        field_name="city",
        value="STAVANGER",
        evidence_text="Official city: STAVANGER",
        created_at=datetime(2026, 9, 1),
    )

    create_fact(
        db,
        company_id=company.id,
        source_id=source.id,
        field_name="city",
        value="News Topic Country Year",
        evidence_text="News navigation text",
        created_at=datetime(2026, 9, 30),
        verification_status="review",
    )

    service = ChangeDetectionService(
        db=db,
    )

    changes = service.detect_for_company(
        company_id=company.id,
    )

    assert changes == []

    db.close()


def test_change_detection_service_ignores_pending_facts():
    db = create_test_database()

    company = create_test_company(db)
    source = create_test_source(db)

    create_fact(
        db,
        company_id=company.id,
        source_id=source.id,
        field_name="employee_count",
        value="24,000",
        evidence_text="Previous employee count",
        created_at=datetime(2026, 9, 1),
        verification_status="verified",
    )

    create_fact(
        db,
        company_id=company.id,
        source_id=source.id,
        field_name="employee_count",
        value="25,000",
        evidence_text="Unverified employee count",
        created_at=datetime(2026, 9, 30),
        verification_status="pending",
    )

    service = ChangeDetectionService(
        db=db,
    )

    changes = service.detect_for_company(
        company_id=company.id,
    )

    assert changes == []

    db.close()