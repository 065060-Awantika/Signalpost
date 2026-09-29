from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database.database import Base
from backend.app.models.source import Source
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


def test_create_source():
    db = create_test_database()

    repository = SourceRepository(db)

    source = repository.create(
        url="https://example.com/company",
        source_type="company_website",
        title="Example Company",
        publisher="Example",
        raw_content="Example company information.",
    )

    assert source.id is not None
    assert source.url == "https://example.com/company"
    assert source.source_type == "company_website"
    assert source.title == "Example Company"
    assert source.publisher == "Example"
    assert source.raw_content == "Example company information."
    assert source.content_hash is not None
    assert len(source.content_hash) == 64

    db.close()


def test_source_content_hash_is_deterministic():
    db = create_test_database()

    repository = SourceRepository(db)

    content = "Example company information."

    source_one = repository.create(
        url="https://example.com/one",
        source_type="company_website",
        raw_content=content,
    )

    source_two = repository.create(
        url="https://example.com/two",
        source_type="company_website",
        raw_content=content,
    )

    assert source_one.content_hash == source_two.content_hash

    db.close()


def test_get_source_by_url():
    db = create_test_database()

    repository = SourceRepository(db)

    created = repository.create(
        url="https://example.com/company",
        source_type="company_website",
        raw_content="Company information.",
    )

    found = repository.get_by_url(
        "https://example.com/company"
    )

    assert found is not None
    assert found.id == created.id
    assert found.url == created.url

    db.close()


def test_get_source_by_unknown_url_returns_none():
    db = create_test_database()

    repository = SourceRepository(db)

    found = repository.get_by_url(
        "https://does-not-exist.example"
    )

    assert found is None

    db.close()


def test_empty_content_has_no_hash():
    db = create_test_database()

    repository = SourceRepository(db)

    source = repository.create(
        url="https://example.com/empty",
        source_type="company_website",
        raw_content=None,
    )

    assert source.content_hash is None

    db.close()