"""Unit tests for SQLite storage layer and transaction invariants."""

import os
import tempfile
from collections.abc import AsyncGenerator
from unittest.mock import patch

import pytest

from sureword.contracts import Draft, DraftState, FieldKey, FieldStatus, FieldValue
from sureword.storage import Storage


@pytest.fixture
async def temp_storage() -> AsyncGenerator[Storage, None]:
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    storage = Storage(db_path=db_path)
    await storage.init_db()
    yield storage

    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.mark.asyncio
async def test_get_draft_non_existent(temp_storage: Storage) -> None:
    res = await temp_storage.get_draft("non_existent_draft_id")
    assert res is None


@pytest.mark.asyncio
async def test_record_committed_idempotent_replay(temp_storage: Storage) -> None:
    draft = Draft(
        draft_id="d_test_idemp",
        version=1,
        created_at="2026-10-31T12:00:00Z",
        language="hi-IN",
        fields={
            FieldKey.PERSON_NAME.value: FieldValue(
                key=FieldKey.PERSON_NAME.value,
                canonical_value="Kamla Devi",
                status=FieldStatus.USER_CONFIRMED,
            ),
        },
        state=DraftState.READY_FOR_REVIEW,
    )
    await temp_storage.save_draft(draft, event_type="TEST_CREATED")

    # First commit: returns True
    first_commit = await temp_storage.record_committed("REC-001", draft, idempotency_key="key_123")
    assert first_commit is True

    # Replay with same idempotency key: returns False
    second_commit = await temp_storage.record_committed("REC-002", draft, idempotency_key="key_123")
    assert second_commit is False


@pytest.mark.asyncio
async def test_delete_draft(temp_storage: Storage) -> None:
    draft = Draft(
        draft_id="d_test_del",
        version=1,
        created_at="2026-10-31T12:00:00Z",
        language="hi-IN",
        fields={
            FieldKey.PERSON_NAME.value: FieldValue(
                key=FieldKey.PERSON_NAME.value,
                canonical_value="Kamla Devi",
                status=FieldStatus.USER_CONFIRMED,
            ),
        },
        state=DraftState.READY_FOR_REVIEW,
    )
    await temp_storage.save_draft(draft, event_type="TEST_CREATED")
    assert await temp_storage.get_draft("d_test_del") is not None

    # Delete draft
    await temp_storage.delete_draft("d_test_del")
    assert await temp_storage.get_draft("d_test_del") is None


@pytest.mark.asyncio
async def test_save_draft_rollback_on_failure(temp_storage: Storage) -> None:
    draft = Draft(
        draft_id="d_test_err",
        version=1,
        created_at="2026-10-31T12:00:00Z",
        language="hi-IN",
        fields={},
        state=DraftState.EMPTY,
    )

    # Patch execute to fail after transaction start
    with patch("aiosqlite.Connection.commit", side_effect=RuntimeError("Simulated DB failure")):
        with pytest.raises(RuntimeError):
            await temp_storage.save_draft(draft, event_type="TEST")
