import hashlib
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.source import Source


class SourceRepository:
    """
    Handles creation and retrieval of source records.

    A source represents a public page or registry record
    used as evidence for company facts.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_url(self, url: str) -> Source | None:
        """
        Return the most recently retrieved source
        for the given URL.
        """

        statement = (
            select(Source)
            .where(Source.url == url)
            .order_by(Source.retrieved_at.desc())
        )

        return self.db.execute(
            statement
        ).scalars().first()

    def create(
        self,
        url: str,
        source_type: str,
        raw_content: str | None = None,
        title: str | None = None,
        publisher: str | None = None,
        published_at: datetime | None = None,
    ) -> Source:
        """
        Create and persist a source record.
        """

        content_hash = self._generate_hash(
            raw_content
        )

        source = Source(
            url=url,
            title=title,
            source_type=source_type,
            publisher=publisher,
            published_at=published_at,
            retrieved_at=datetime.utcnow(),
            content_hash=content_hash,
            raw_content=raw_content,
        )

        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)

        return source

    @staticmethod
    def _generate_hash(
        content: str | None,
    ) -> str | None:
        """
        Generate a SHA-256 hash so Signalpost can later
        detect whether a source has changed.
        """

        if not content:
            return None

        return hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()