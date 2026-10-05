from dataclasses import dataclass


@dataclass(frozen=True)
class FactObservation:
    field_name: str
    value: str
    fact_id: int | None = None


@dataclass(frozen=True)
class FactChangeResult:
    field_name: str
    change_type: str
    previous_value: str | None
    current_value: str | None
    previous_fact_id: int | None
    current_fact_id: int | None


class FactChangeDetector:
    """
    Compares two observations of company facts.

    The detector is intentionally deterministic.
    No LLM is required to determine whether a value changed.
    """

    ADDED = "added"
    MODIFIED = "modified"
    REMOVED = "removed"
    UNCHANGED = "unchanged"

    def compare(
        self,
        previous_facts: list[FactObservation],
        current_facts: list[FactObservation],
    ) -> list[FactChangeResult]:
        previous_map = self._build_map(previous_facts)
        current_map = self._build_map(current_facts)

        fields = sorted(
            set(previous_map) | set(current_map)
        )

        changes: list[FactChangeResult] = []

        for field_name in fields:
            previous = previous_map.get(field_name)
            current = current_map.get(field_name)

            if previous is None and current is not None:
                changes.append(
                    FactChangeResult(
                        field_name=field_name,
                        change_type=self.ADDED,
                        previous_value=None,
                        current_value=current.value,
                        previous_fact_id=None,
                        current_fact_id=current.fact_id,
                    )
                )
                continue

            if previous is not None and current is None:
                changes.append(
                    FactChangeResult(
                        field_name=field_name,
                        change_type=self.REMOVED,
                        previous_value=previous.value,
                        current_value=None,
                        previous_fact_id=previous.fact_id,
                        current_fact_id=None,
                    )
                )
                continue

            if previous is None or current is None:
                continue

            if self._normalize_value(
                previous.value
            ) == self._normalize_value(
                current.value
            ):
                changes.append(
                    FactChangeResult(
                        field_name=field_name,
                        change_type=self.UNCHANGED,
                        previous_value=previous.value,
                        current_value=current.value,
                        previous_fact_id=previous.fact_id,
                        current_fact_id=current.fact_id,
                    )
                )
            else:
                changes.append(
                    FactChangeResult(
                        field_name=field_name,
                        change_type=self.MODIFIED,
                        previous_value=previous.value,
                        current_value=current.value,
                        previous_fact_id=previous.fact_id,
                        current_fact_id=current.fact_id,
                    )
                )

        return changes

    @staticmethod
    def _build_map(
        facts: list[FactObservation],
    ) -> dict[str, FactObservation]:
        result: dict[str, FactObservation] = {}

        for fact in facts:
            field_name = fact.field_name.strip().lower()

            if not field_name:
                continue

            result[field_name] = fact

        return result

    @staticmethod
    def _normalize_value(value: str | None) -> str:
        if value is None:
            return ""

        return " ".join(
            str(value)
            .strip()
            .lower()
            .split()
        )