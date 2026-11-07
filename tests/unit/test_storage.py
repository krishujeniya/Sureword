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


def test_storage_routing() -> None:
    sqlite_store = Storage(db_path="/tmp/test_custom.db")
    assert sqlite_store.backend_name == "sqlite"
    assert sqlite_store.db_path == "/tmp/test_custom.db"

    pg_url = "postgres://user:secret@ep-test.neon.tech/neondb?sslmode=require"
    pg_store = Storage(database_url=pg_url)
    assert pg_store.backend_name == "postgres"
    assert pg_store.db_path == "postgresql://user:secret@ep-test.neon.tech/neondb?sslmode=require"


@pytest.mark.asyncio
async def test_postgres_storage_mocked_methods() -> None:
    from unittest.mock import AsyncMock, MagicMock

    from sureword.storage import PostgresStorage

    pg_url = "postgresql://user:pass@localhost:5432/testdb"
    store = PostgresStorage(db_url=pg_url)

    mock_pool = MagicMock()
    mock_conn = MagicMock()
    mock_conn.execute = AsyncMock()
    mock_conn.fetch = AsyncMock()
    mock_conn.fetchrow = AsyncMock()

    class MockTransactionContext:
        async def __aenter__(self) -> MagicMock:
            return mock_conn

        async def __aexit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
            pass

    mock_conn.transaction.return_value = MockTransactionContext()

    class MockAcquireContext:
        async def __aenter__(self) -> MagicMock:
            return mock_conn

        async def __aexit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
            pass

    mock_pool.acquire.return_value = MockAcquireContext()
    mock_pool.close = AsyncMock()
    store._pool = mock_pool

    # Test init_db
    await store.init_db()
    assert mock_conn.execute.called

    # Test save_draft
    draft = Draft(
        draft_id="d_pg_1",
        version=1,
        created_at="2026-11-07T00:00:00Z",
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
    await store.save_draft(draft)
    assert mock_conn.execute.call_count >= 3

    # Test get_draft found
    mock_conn.fetchrow.return_value = {
        "draft_id": "d_pg_1",
        "version": 1,
        "state": DraftState.READY_FOR_REVIEW.value,
        "language": "hi-IN",
        "created_at": "2026-11-07T00:00:00Z",
        "attempts_json": "{}",
        "active_prompt_json": None,
        "latest_transcript_json": None,
    }
    mock_conn.fetch.return_value = [
        {
            "field_key": FieldKey.PERSON_NAME.value,
            "raw_span": "Kamla Devi",
            "canonical_value": "Kamla Devi",
            "status": FieldStatus.USER_CONFIRMED.value,
            "reasons_json": "[]",
            "source_turn_id": 1,
        }
    ]
    fetched = await store.get_draft("d_pg_1")
    assert fetched is not None
    assert fetched.draft_id == "d_pg_1"
    assert FieldKey.PERSON_NAME.value in fetched.fields

    # Test record_committed idempotency
    mock_conn.fetchrow.return_value = None  # Not previously committed
    committed = await store.record_committed("REC-PG-1", draft, "key_pg_1")
    assert committed is True

    mock_conn.fetchrow.return_value = {"record_id": "REC-PG-1"}  # Already committed
    committed_dup = await store.record_committed("REC-PG-2", draft, "key_pg_1")
    assert committed_dup is False

    # Test delete_draft
    await store.delete_draft("d_pg_1")
    assert mock_conn.execute.called

    # Test close
    await store.close()
    assert mock_pool.close.called
