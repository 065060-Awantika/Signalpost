from backend.app.services.change_detector import (
    FactChangeDetector,
    FactObservation,
)


def test_detects_modified_fact():
    detector = FactChangeDetector()

    previous = [
        FactObservation(
            field_name="employee_count",
            value="24,000",
            fact_id=1,
        )
    ]

    current = [
        FactObservation(
            field_name="employee_count",
            value="25,000",
            fact_id=2,
        )
    ]

    changes = detector.compare(
        previous,
        current,
    )

    assert len(changes) == 1

    change = changes[0]

    assert change.field_name == "employee_count"
    assert change.change_type == "modified"
    assert change.previous_value == "24,000"
    assert change.current_value == "25,000"
    assert change.previous_fact_id == 1
    assert change.current_fact_id == 2


def test_detects_added_fact():
    detector = FactChangeDetector()

    previous = []

    current = [
        FactObservation(
            field_name="website",
            value="https://example.com",
            fact_id=2,
        )
    ]

    changes = detector.compare(
        previous,
        current,
    )

    assert len(changes) == 1
    assert changes[0].change_type == "added"
    assert changes[0].previous_value is None
    assert changes[0].current_value == "https://example.com"


def test_detects_removed_fact():
    detector = FactChangeDetector()

    previous = [
        FactObservation(
            field_name="phone",
            value="+47 12345678",
            fact_id=1,
        )
    ]

    current = []

    changes = detector.compare(
        previous,
        current,
    )

    assert len(changes) == 1
    assert changes[0].change_type == "removed"
    assert changes[0].previous_value == "+47 12345678"
    assert changes[0].current_value is None


def test_detects_unchanged_fact():
    detector = FactChangeDetector()

    previous = [
        FactObservation(
            field_name="legal_name",
            value="EQUINOR ASA",
            fact_id=1,
        )
    ]

    current = [
        FactObservation(
            field_name="legal_name",
            value="  Equinor   ASA ",
            fact_id=2,
        )
    ]

    changes = detector.compare(
        previous,
        current,
    )

    assert len(changes) == 1
    assert changes[0].change_type == "unchanged"


def test_compares_multiple_fields():
    detector = FactChangeDetector()

    previous = [
        FactObservation(
            field_name="employee_count",
            value="24,000",
            fact_id=1,
        ),
        FactObservation(
            field_name="industry",
            value="Oil",
            fact_id=2,
        ),
    ]

    current = [
        FactObservation(
            field_name="employee_count",
            value="25,000",
            fact_id=3,
        ),
        FactObservation(
            field_name="industry",
            value="Oil",
            fact_id=4,
        ),
        FactObservation(
            field_name="website",
            value="https://example.com",
            fact_id=5,
        ),
    ]

    changes = detector.compare(
        previous,
        current,
    )

    result = {
        change.field_name: change.change_type
        for change in changes
    }

    assert result == {
        "employee_count": "modified",
        "industry": "unchanged",
        "website": "added",
    }