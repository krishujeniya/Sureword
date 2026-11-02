"""Unit tests for draft state machine and lifecycle invariants."""

import os
import tempfile
from collections.abc import AsyncGenerator

import pytest

from sureword.contracts import DraftState, FieldKey, FieldStatus, FieldValue, Transcript
from sureword.state import DraftStateMachine, StateTransitionError
from sureword.storage import Storage


@pytest.fixture
async def temp_state_machine() -> AsyncGenerator[DraftStateMachine, None]:
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    storage = Storage(db_path=db_path)
    await storage.init_db()
    sm = DraftStateMachine(storage=storage)
    yield sm

    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.mark.asyncio
async def test_create_draft(temp_state_machine: DraftStateMachine) -> None:
    draft = await temp_state_machine.create_draft()
    assert draft.version == 1
    assert draft.state == DraftState.EMPTY
    assert len(draft.fields) == 4
    for k in [
        FieldKey.PERSON_NAME.value,
        FieldKey.AGE.value,
        FieldKey.VILLAGE.value,
        FieldKey.VISIT_DATE.value,
    ]:
        assert draft.fields[k].status == FieldStatus.MISSING


@pytest.mark.asyncio
async def test_stale_version_rejection(temp_state_machine: DraftStateMachine) -> None:
    draft = await temp_state_machine.create_draft()
    transcript = Transcript(text="test", source="fixture")
    parsed_fields = {
        FieldKey.PERSON_NAME.value: FieldValue(
            key="person_name", canonical_value="Kamla Devi", status=FieldStatus.PROPOSED
        ),
    }

    # Pass wrong expected_version
    with pytest.raises(StateTransitionError) as exc_info:
        await temp_state_machine.apply_audio_parse(
            draft_id=draft.draft_id,
            expected_version=999,  # Stale
            transcript=transcript,
            parsed_fields=parsed_fields,
        )
    assert exc_info.value.code == "STALE_VERSION"


@pytest.mark.asyncio
async def test_commit_requires_all_fields(temp_state_machine: DraftStateMachine) -> None:
    draft = await temp_state_machine.create_draft()

    # Attempting to commit empty draft must fail
    with pytest.raises(StateTransitionError) as exc_info:
        await temp_state_machine.commit_draft(
            draft_id=draft.draft_id,
            expected_version=draft.version,
            idempotency_key="idemp_1",
        )
    assert exc_info.value.code == "UNRESOLVED_FIELD"


@pytest.mark.asyncio
async def test_successful_commit_and_idempotency(temp_state_machine: DraftStateMachine) -> None:
    draft = await temp_state_machine.create_draft()

    # Populate all 4 valid fields
    valid_fields = {
        FieldKey.PERSON_NAME.value: FieldValue(
            key="person_name", canonical_value="Kamla Devi", status=FieldStatus.USER_CONFIRMED
        ),
        FieldKey.AGE.value: FieldValue(
            key="age", canonical_value="45", status=FieldStatus.USER_CONFIRMED
        ),
        FieldKey.VILLAGE.value: FieldValue(
            key="village", canonical_value="Rampur", status=FieldStatus.USER_CONFIRMED
        ),
        FieldKey.VISIT_DATE.value: FieldValue(
            key="visit_date", canonical_value="2026-10-30", status=FieldStatus.USER_CONFIRMED
        ),
    }
    transcript = Transcript(text="all valid", source="fixture")
    draft = await temp_state_machine.apply_audio_parse(
        draft_id=draft.draft_id,
        expected_version=draft.version,
        transcript=transcript,
        parsed_fields=valid_fields,
    )

    assert draft.state == DraftState.READY_FOR_REVIEW

    # Commit record
    record_id, committed_draft = await temp_state_machine.commit_draft(
        draft_id=draft.draft_id,
        expected_version=draft.version,
        idempotency_key="idemp_unique_123",
    )
    assert record_id.startswith("REC-")
    assert committed_draft.state == DraftState.COMMITTED

    # Modifying committed draft via audio must fail
    with pytest.raises(StateTransitionError) as exc_committed:
        await temp_state_machine.apply_audio_parse(
            draft_id=draft.draft_id,
            expected_version=committed_draft.version,
            transcript=transcript,
            parsed_fields={},
        )
    assert exc_committed.value.code == "ALREADY_COMMITTED"

    # Modifying committed draft via clarify must fail
    with pytest.raises(StateTransitionError) as exc_clarify_comm:
        await temp_state_machine.apply_clarification(
            draft_id=draft.draft_id,
            expected_version=committed_draft.version,
            target_field="person_name",
            updated_field=FieldValue(key="person_name", canonical_value="New Name"),
        )
    assert exc_clarify_comm.value.code == "ALREADY_COMMITTED"


@pytest.mark.asyncio
async def test_apply_audio_parse_not_found(temp_state_machine: DraftStateMachine) -> None:
    with pytest.raises(StateTransitionError) as exc:
        await temp_state_machine.apply_audio_parse(
            draft_id="non_existent_draft",
            expected_version=1,
            transcript=Transcript(text="test", source="fixture"),
            parsed_fields={},
        )
    assert exc.value.code == "DRAFT_NOT_FOUND"


@pytest.mark.asyncio
async def test_apply_clarification_errors_and_transitions(
    temp_state_machine: DraftStateMachine,
) -> None:
    # 1. Draft not found
    with pytest.raises(StateTransitionError) as exc_nf:
        await temp_state_machine.apply_clarification(
            draft_id="non_existent_id",
            expected_version=1,
            target_field="person_name",
            updated_field=FieldValue(key="person_name", canonical_value="Kamla Devi"),
        )
    assert exc_nf.value.code == "DRAFT_NOT_FOUND"

    # 2. Version mismatch
    draft = await temp_state_machine.create_draft()
    with pytest.raises(StateTransitionError) as exc_v:
        await temp_state_machine.apply_clarification(
            draft_id=draft.draft_id,
            expected_version=999,
            target_field="person_name",
            updated_field=FieldValue(key="person_name", canonical_value="Kamla Devi"),
        )
    assert exc_v.value.code == "STALE_VERSION"

    # 3. Successful clarification transition to NEEDS_CLARIFICATION for remaining fields
    updated = await temp_state_machine.apply_clarification(
        draft_id=draft.draft_id,
        expected_version=draft.version,
        target_field="person_name",
        updated_field=FieldValue(
            key="person_name",
            canonical_value="Kamla Devi",
            status=FieldStatus.USER_CONFIRMED,
        ),
    )
    assert updated.version == 2
    assert updated.fields["person_name"].status == FieldStatus.USER_CONFIRMED
    assert updated.state == DraftState.NEEDS_CLARIFICATION


@pytest.mark.asyncio
async def test_commit_draft_errors(temp_state_machine: DraftStateMachine) -> None:
    # Draft not found
    with pytest.raises(StateTransitionError) as exc_nf:
        await temp_state_machine.commit_draft(
            draft_id="non_existent_id",
            expected_version=1,
            idempotency_key="idemp_1",
        )
    assert exc_nf.value.code == "DRAFT_NOT_FOUND"

    # Version mismatch
    draft = await temp_state_machine.create_draft()
    with pytest.raises(StateTransitionError) as exc_v:
        await temp_state_machine.commit_draft(
            draft_id=draft.draft_id,
            expected_version=999,
            idempotency_key="idemp_1",
        )
    assert exc_v.value.code == "STALE_VERSION"
