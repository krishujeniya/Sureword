"""Unit tests for risk assessment and clarification selection policies."""

from fieldcheck.contracts import FieldStatus, FieldValue
from fieldcheck.policy import (
    compute_field_risk,
    rank_fields_by_risk,
    select_clarification_field_b1,
    select_clarification_field_b2,
    select_clarification_field_p,
)


def test_compute_field_risk_levels() -> None:
    # Confirmed field has 0.0 risk
    f_confirmed = FieldValue(key="age", canonical_value="45", status=FieldStatus.USER_CONFIRMED)
    assert compute_field_risk(f_confirmed).risk_score == 0.0

    # Missing field has 1.0 risk
    f_missing = FieldValue(key="person_name", status=FieldStatus.MISSING)
    assert compute_field_risk(f_missing).risk_score == 1.0

    # Out-of-bounds / needs_repeat has 0.9 risk
    f_invalid = FieldValue(key="age", canonical_value="150", status=FieldStatus.NEEDS_REPEAT)
    assert compute_field_risk(f_invalid).risk_score == 0.9


def test_rank_fields_by_risk() -> None:
    fields = {
        "person_name": FieldValue(key="person_name", canonical_value="Kamla Devi", status=FieldStatus.PROPOSED),
        "age": FieldValue(key="age", status=FieldStatus.MISSING),
        "village": FieldValue(key="village", canonical_value="Rampur", status=FieldStatus.USER_CONFIRMED),
        "visit_date": FieldValue(key="visit_date", canonical_value="2026-10-30", status=FieldStatus.PROPOSED),
    }

    ranked = rank_fields_by_risk(fields)
    assert ranked[0].key == "age"  # Missing field is highest risk (1.0)
    assert ranked[-1].key == "village"  # Confirmed field is lowest risk (0.0)


def test_select_clarification_p() -> None:
    fields = {
        "person_name": FieldValue(key="person_name", canonical_value="Kamla Devi", status=FieldStatus.PROPOSED),
        "age": FieldValue(key="age", status=FieldStatus.NEEDS_REPEAT),
        "village": FieldValue(key="village", canonical_value="Rampur", status=FieldStatus.USER_CONFIRMED),
        "visit_date": FieldValue(key="visit_date", canonical_value="2026-10-30", status=FieldStatus.USER_CONFIRMED),
    }
    attempts = {}

    prompt = select_clarification_field_p(fields, attempts, max_attempts=2, risk_threshold=0.3)
    assert prompt is not None
    assert prompt.target_field == "age"  # Needs repeat field selected


def test_select_clarification_b1() -> None:
    fields = {
        "person_name": FieldValue(key="person_name", canonical_value="Kamla Devi", status=FieldStatus.PROPOSED),
        "age": FieldValue(key="age", canonical_value="45", status=FieldStatus.PROPOSED),
        "village": FieldValue(key="village", canonical_value="Rampur", status=FieldStatus.PROPOSED),
        "visit_date": FieldValue(key="visit_date", canonical_value="2026-10-30", status=FieldStatus.PROPOSED),
    }
    attempts = {}

    prompt = select_clarification_field_b1(fields, attempts, max_attempts=1)
    assert prompt is not None
    assert prompt.target_field == "person_name"  # Fixed alphabetical first field


def test_select_clarification_b2() -> None:
    fields = {
        "person_name": FieldValue(key="person_name", canonical_value="Kamla Devi", status=FieldStatus.PROPOSED),
        "age": FieldValue(key="age", canonical_value="45", status=FieldStatus.PROPOSED),
    }
    attempts = {}

    prompt = select_clarification_field_b2(fields, attempts, seed=42, max_attempts=1)
    assert prompt is not None
    assert prompt.target_field in fields
