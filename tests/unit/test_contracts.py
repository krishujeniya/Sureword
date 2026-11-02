"""Unit tests for Sureword data contracts and models."""

from sureword.contracts import (
    CommitRequest,
    Draft,
    DraftState,
    FieldKey,
    FieldStatus,
    FieldValue,
    Transcript,
)


def test_field_value_defaults() -> None:
    fv = FieldValue(key=FieldKey.PERSON_NAME.value)
    assert fv.key == "person_name"
    assert fv.status == FieldStatus.MISSING
    assert fv.canonical_value is None
    assert fv.reasons == []


def test_draft_initialization() -> None:
    draft = Draft(
        draft_id="test_001",
        version=1,
        created_at="2026-10-31T12:00:00Z",
        language="hi-IN",
        fields={
            FieldKey.PERSON_NAME.value: FieldValue(key=FieldKey.PERSON_NAME.value),
        },
        state=DraftState.EMPTY,
    )
    assert draft.draft_id == "test_001"
    assert draft.version == 1
    assert draft.state == DraftState.EMPTY
    assert draft.fields["person_name"].status == FieldStatus.MISSING


def test_transcript_model() -> None:
    t = Transcript(
        text="मरीज का नाम कमला देवी",
        provider="gnani_prisma",
        requested_model="prisma-v3",
        duration_ms=320.5,
        confidence=0.92,
        source="fixture",
    )
    assert t.source == "fixture"
    assert t.confidence == 0.92


def test_commit_request_validation() -> None:
    cr = CommitRequest(expected_version=2, idempotency_key="idemp_123")
    assert cr.expected_version == 2
    assert cr.idempotency_key == "idemp_123"
