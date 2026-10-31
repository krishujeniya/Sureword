"""Selective risk policies and clarification ranking for FieldCheck."""

from __future__ import annotations

import random
from typing import NamedTuple

from fieldcheck.contracts import ClarificationPrompt, FieldKey, FieldStatus, FieldValue


class FieldRiskAssessment(NamedTuple):
    key: str
    risk_score: float
    reasons: list[str]


PROMPT_TEMPLATES: dict[str, str] = {
    FieldKey.PERSON_NAME.value: "कृपया मरीज़ का पूरा नाम दोबारा बोलिए। (Please repeat the person's full name)",
    FieldKey.AGE.value: "कृपया मरीज़ की सही उम्र दोबारा बोलिए। (Please repeat the person's age in completed years)",
    FieldKey.VILLAGE.value: "कृपया गाँव का नाम दोबारा बोलिए। (Please repeat the village name)",
    FieldKey.VISIT_DATE.value: "कृपया विज़िट की सही तारीख दोबारा बोलिए। (Please repeat the visit date)",
}


def compute_field_risk(field: FieldValue) -> FieldRiskAssessment:
    """Compute deterministic risk score for a field.

    Scores range from 0.0 (safe/confirmed) to 1.0 (missing/invalid).
    """
    reasons = list(field.reasons)

    if field.status in {FieldStatus.USER_CONFIRMED, FieldStatus.MANUALLY_EDITED}:
        return FieldRiskAssessment(field.key, 0.0, ["Field explicitly confirmed by user"])

    if field.status == FieldStatus.MISSING or field.canonical_value is None:
        reasons.append("Field value is missing")
        return FieldRiskAssessment(field.key, 1.0, reasons)

    if field.status == FieldStatus.NEEDS_REPEAT:
        reasons.append("Field violates format, range, or detected conflicting mentions")
        return FieldRiskAssessment(field.key, 0.9, reasons)

    # For proposed unconfirmed fields, assess risk factors
    base_risk = 0.35
    if "Out-of-dictionary" in " ".join(field.reasons):
        base_risk += 0.35
        reasons.append("Entity was not in verified dictionary")

    # Lower risk slightly for common well-formatted canonical values
    if field.key == FieldKey.VISIT_DATE.value and field.canonical_value:
        base_risk -= 0.1
    elif field.key == FieldKey.AGE.value and field.canonical_value:
        base_risk -= 0.05

    return FieldRiskAssessment(field.key, round(base_risk, 2), reasons)


def rank_fields_by_risk(fields: dict[str, FieldValue]) -> list[FieldRiskAssessment]:
    """Rank fields in descending order of risk."""
    assessments = [compute_field_risk(f) for f in fields.values()]
    # Sort by risk descending; tie-break by key for determinism
    return sorted(assessments, key=lambda a: (-a.risk_score, a.key))


def select_clarification_field_p(
    fields: dict[str, FieldValue],
    attempts_by_field: dict[str, int],
    max_attempts: int = 2,
    risk_threshold: float = 0.3,
) -> ClarificationPrompt | None:
    """Proposed Policy P: Select the single highest-risk field needing clarification."""
    ranked = rank_fields_by_risk(fields)

    for assessment in ranked:
        if assessment.risk_score < risk_threshold:
            # Field is sufficiently reliable; do not prompt
            continue

        attempts = attempts_by_field.get(assessment.key, 0)
        if attempts >= max_attempts:
            # Reached max attempts for this field; cannot ask again
            continue

        prompt_text = PROMPT_TEMPLATES.get(
            assessment.key,
            f"Please clarify {assessment.key}."
        )
        return ClarificationPrompt(
            target_field=assessment.key,
            prompt_text=prompt_text,
            attempt_number=attempts + 1,
        )

    return None


def select_clarification_field_b1(
    fields: dict[str, FieldValue],
    attempts_by_field: dict[str, int],
    max_attempts: int = 1,
) -> ClarificationPrompt | None:
    """Baseline B1: Schema violations/missing first, then fixed alphabetical order."""
    field_order = [
        FieldKey.PERSON_NAME.value,
        FieldKey.AGE.value,
        FieldKey.VILLAGE.value,
        FieldKey.VISIT_DATE.value,
    ]

    # First check missing or invalid
    for k in field_order:
        f = fields.get(k)
        if f and (f.status in {FieldStatus.MISSING, FieldStatus.NEEDS_REPEAT}):
            if attempts_by_field.get(k, 0) < max_attempts:
                return ClarificationPrompt(
                    target_field=k,
                    prompt_text=PROMPT_TEMPLATES[k],
                    attempt_number=attempts_by_field.get(k, 0) + 1,
                )

    # Next check proposed unconfirmed in fixed order
    for k in field_order:
        f = fields.get(k)
        if f and f.status == FieldStatus.PROPOSED:
            if attempts_by_field.get(k, 0) < max_attempts:
                return ClarificationPrompt(
                    target_field=k,
                    prompt_text=PROMPT_TEMPLATES[k],
                    attempt_number=attempts_by_field.get(k, 0) + 1,
                )

    return None


def select_clarification_field_b2(
    fields: dict[str, FieldValue],
    attempts_by_field: dict[str, int],
    seed: int = 42,
    max_attempts: int = 1,
) -> ClarificationPrompt | None:
    """Baseline B2: Seeded random field selection from eligible fields."""
    rng = random.Random(seed)
    eligible = [
        k for k, f in fields.items()
        if f.status != FieldStatus.USER_CONFIRMED and attempts_by_field.get(k, 0) < max_attempts
    ]
    if not eligible:
        return None

    selected_key = rng.choice(sorted(eligible))
    return ClarificationPrompt(
        target_field=selected_key,
        prompt_text=PROMPT_TEMPLATES[selected_key],
        attempt_number=attempts_by_field.get(selected_key, 0) + 1,
    )
