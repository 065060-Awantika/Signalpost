from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database.database import Base


class FactChange(Base):
    __tablename__ = "fact_changes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"),
        nullable=False,
        index=True,
    )

    field_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    change_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    previous_value: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    current_value: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    previous_fact_id: Mapped[int | None] = mapped_column(
        ForeignKey("company_facts.id"),
        nullable=True,
    )

    current_fact_id: Mapped[int | None] = mapped_column(
        ForeignKey("company_facts.id"),
        nullable=True,
    )

    detected_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )