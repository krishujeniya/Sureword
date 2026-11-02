"""Unit tests for risk assessment and clarification selection policies."""

from sureword.contracts import FieldStatus, FieldValue
from sureword.policy import (
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

    # Out-of-dictionary village adds 0.35 risk
    f_ood = FieldValue(
        key="village",
        canonical_value="UnknownPur",
        status=FieldStatus.PROPOSED,
        reasons=["Out-of-dictionary village name extracted via marker"],
    )
    assert compute_field_risk(f_ood).risk_score >= 0.7

    # Visit date and Age canonical discounts
    f_date = FieldValue(key="visit_date", canonical_value="2026-10-31", status=FieldStatus.PROPOSED)
    assert compute_field_risk(f_date).risk_score == 0.25

    f_age = FieldValue(key="age", canonical_value="42", status=FieldStatus.PROPOSED)
    assert compute_field_risk(f_age).risk_score == 0.30


def test_rank_fields_by_risk() -> None:
    fields = {
        "person_name": FieldValue(
            key="person_name", canonical_value="Kamla Devi", status=FieldStatus.PROPOSED
        ),
        "age": FieldValue(key="age", status=FieldStatus.MISSING),
        "village": FieldValue(
            key="village", canonical_value="Rampur", status=FieldStatus.USER_CONFIRMED
        ),
        "visit_date": FieldValue(
            key="visit_date", canonical_value="2026-10-30", status=FieldStatus.PROPOSED
        ),
    }

    ranked = rank_fields_by_risk(fields)
    assert ranked[0].key == "age"  # Missing field is highest risk (1.0)
    assert ranked[-1].key == "village"  # Confirmed field is lowest risk (0.0)


def test_select_clarification_p() -> None:
    fields = {
        "person_name": FieldValue(
            key="person_name", canonical_value="Kamla Devi", status=FieldStatus.PROPOSED
        ),
        "age": FieldValue(key="age", status=FieldStatus.NEEDS_REPEAT),
        "village": FieldValue(
            key="village", canonical_value="Rampur", status=FieldStatus.USER_CONFIRMED
        ),
        "visit_date": FieldValue(
            key="visit_date", canonical_value="2026-10-30", status=FieldStatus.USER_CONFIRMED
        ),
    }
    attempts: dict[str, int] = {}

    prompt = select_clarification_field_p(fields, attempts, max_attempts=2, risk_threshold=0.3)
    assert prompt is not None
    assert prompt.target_field == "age"  # Needs repeat field selected


def test_select_clarification_b1() -> None:
    fields = {
        "person_name": FieldValue(
            key="person_name", canonical_value="Kamla Devi", status=FieldStatus.PROPOSED
        ),
        "age": FieldValue(key="age", canonical_value="45", status=FieldStatus.PROPOSED),
        "village": FieldValue(key="village", canonical_value="Rampur", status=FieldStatus.PROPOSED),
        "visit_date": FieldValue(
            key="visit_date", canonical_value="2026-10-30", status=FieldStatus.PROPOSED
        ),
    }
    attempts: dict[str, int] = {}

    prompt = select_clarification_field_b1(fields, attempts, max_attempts=1)
    assert prompt is not None
    assert prompt.target_field == "person_name"  # Fixed alphabetical first field


def test_select_clarification_b2() -> None:
    fields = {
        "person_name": FieldValue(
            key="person_name", canonical_value="Kamla Devi", status=FieldStatus.PROPOSED
        ),
        "age": FieldValue(key="age", canonical_value="45", status=FieldStatus.PROPOSED),
    }
    attempts: dict[str, int] = {}

    prompt = select_clarification_field_b2(fields, attempts, seed=42, max_attempts=1)
    assert prompt is not None
    assert prompt.target_field in fields


def test_select_clarification_p_exhausted_attempts() -> None:
    fields = {
        "person_name": FieldValue(
            key="person_name", canonical_value="Kamla Devi", status=FieldStatus.PROPOSED
        ),
        "age": FieldValue(key="age", status=FieldStatus.NEEDS_REPEAT),
    }
    # Age has already reached max attempts (2)
    attempts = {"age": 2, "person_name": 2}
    prompt = select_clarification_field_p(fields, attempts, max_attempts=2)
    assert prompt is None


def test_select_clarification_b1_missing_and_exhausted() -> None:
    fields = {
        "person_name": FieldValue(key="person_name", status=FieldStatus.MISSING),
        "age": FieldValue(key="age", canonical_value="45", status=FieldStatus.USER_CONFIRMED),
    }
    # When missing field has attempts left
    p1 = select_clarification_field_b1(fields, {}, max_attempts=1)
    assert p1 is not None
    assert p1.target_field == "person_name"

    # When all eligible fields have reached max attempts
    p2 = select_clarification_field_b1(fields, {"person_name": 1}, max_attempts=1)
    assert p2 is None


def test_select_clarification_b2_no_eligible_fields() -> None:
    fields = {
        "age": FieldValue(key="age", canonical_value="45", status=FieldStatus.USER_CONFIRMED),
    }
    prompt = select_clarification_field_b2(fields, {}, max_attempts=1)
    assert prompt is None
