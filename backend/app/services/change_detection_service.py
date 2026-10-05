from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.fact import CompanyFact
from backend.app.services.change_detector import (
    FactChangeDetector,
    FactObservation,
)
from backend.app.services.change_repository import (
    ChangeRepository,
)


class ChangeDetectionService:
    """
    Connects deterministic fact comparison to the database.

    Only verified and review-quality facts are considered.
    Rejected and pending facts cannot create change alerts.
    """

    IGNORED_FIELDS = {
        "city",
    }

    ALLOWED_STATUSES = {
        "verified",
        "review",
    }

    def __init__(
        self,
        db: Session,
        detector: FactChangeDetector | None = None,
        repository: ChangeRepository | None = None,
    ) -> None:
        self.db = db
        self.detector = detector or FactChangeDetector()
        self.repository = repository or ChangeRepository(db)

    def detect_for_company(
        self,
        *,
        company_id: int,
    ) -> list:
        facts = self._get_company_facts(company_id)

        grouped = self._group_by_field(facts)

        changes = []

        for field_name, field_facts in grouped.items():
            if field_name in self.IGNORED_FIELDS:
                continue

            if len(field_facts) < 2:
                continue

            previous_fact = field_facts[-2]
            current_fact = field_facts[-1]

            previous = FactObservation(
                field_name=previous_fact.field_name,
                value=previous_fact.value,
                fact_id=previous_fact.id,
            )

            current = FactObservation(
                field_name=current_fact.field_name,
                value=current_fact.value,
                fact_id=current_fact.id,
            )

            result = self.detector.compare(
                previous_facts=[previous],
                current_facts=[current],
            )[0]

            if result.change_type == self.detector.UNCHANGED:
                continue

            if not self._is_meaningful_change(
                previous_fact,
                current_fact,
            ):
                continue

            existing_change = (
                self.repository.get_by_fact_pair(
                    company_id=company_id,
                    previous_fact_id=previous_fact.id,
                    current_fact_id=current_fact.id,
                )
            )

            if existing_change is not None:
                continue

            change = self.repository.create(
                company_id=company_id,
                field_name=result.field_name,
                change_type=result.change_type,
                previous_value=result.previous_value,
                current_value=result.current_value,
                previous_fact_id=result.previous_fact_id,
                current_fact_id=result.current_fact_id,
            )

            changes.append(change)

        return changes

    def _get_company_facts(
        self,
        company_id: int,
    ) -> list[CompanyFact]:
        statement = (
            select(CompanyFact)
            .where(
                CompanyFact.company_id == company_id,
                CompanyFact.verification_status.in_(
                    self.ALLOWED_STATUSES
                ),
            )
            .order_by(
                CompanyFact.field_name.asc(),
                CompanyFact.created_at.asc(),
                CompanyFact.id.asc(),
            )
        )

        return list(
            self.db.scalars(statement).all()
        )

    @staticmethod
    def _group_by_field(
        facts: list[CompanyFact],
    ) -> dict[str, list[CompanyFact]]:
        grouped: dict[str, list[CompanyFact]] = {}

        for fact in facts:
            field_name = fact.field_name.strip().lower()

            if not field_name:
                continue

            grouped.setdefault(
                field_name,
                [],
            ).append(fact)

        return grouped

    @staticmethod
    def _is_meaningful_change(
        previous: CompanyFact,
        current: CompanyFact,
    ) -> bool:
        previous_value = " ".join(
            (previous.value or "")
            .strip()
            .lower()
            .split()
        )

        current_value = " ".join(
            (current.value or "")
            .strip()
            .lower()
            .split()
        )

        if previous_value == current_value:
            return False

        if previous.verification_status not in {
            "verified",
            "review",
        }:
            return False

        if current.verification_status not in {
            "verified",
            "review",
        }:
            return False

        return True