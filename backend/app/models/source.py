from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database.database import Base


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    title: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    source_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    publisher: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    retrieved_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    content_hash: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    raw_content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )