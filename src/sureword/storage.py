"""Persistent storage layer for Sureword.

Supports asynchronous SQLite (for local development, testing, and offline fixtures)
and managed PostgreSQL via asyncpg (for production serverless deployments on Vercel/Neon/Supabase).
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from typing import Any

import aiosqlite

from sureword.contracts import Draft, DraftState, FieldValue

try:
    import asyncpg
except ImportError:
    asyncpg = None  # type: ignore[assignment]


class SQLiteStorage:
    """SQLite asynchronous storage implementation."""

    def __init__(self, db_path: str = "sureword.db") -> None:
        self.db_path = db_path
        self.backend_name = "sqlite"

    async def init_db(self) -> None:
        """Create tables for drafts, fields, audit events, and committed records."""
        parent_dir = os.path.dirname(os.path.abspath(self.db_path))
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS drafts (
                    draft_id TEXT PRIMARY KEY,
                    version INTEGER NOT NULL,
                    state TEXT NOT NULL,
                    language TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    attempts_json TEXT NOT NULL,
                    active_prompt_json TEXT,
                    latest_transcript_json TEXT
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS fields (
                    draft_id TEXT NOT NULL,
                    field_key TEXT NOT NULL,
                    raw_span TEXT,
                    canonical_value TEXT,
                    status TEXT NOT NULL,
                    reasons_json TEXT NOT NULL,
                    source_turn_id INTEGER NOT NULL,
                    PRIMARY KEY (draft_id, field_key)
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    draft_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS committed_records (
                    record_id TEXT PRIMARY KEY,
                    draft_id TEXT NOT NULL,
                    idempotency_key TEXT NOT NULL UNIQUE,
                    snapshot_json TEXT NOT NULL,
                    committed_at TEXT NOT NULL
                )
            """)
            await db.commit()

    async def save_draft(self, draft: Draft, event_type: str = "DRAFT_UPDATE") -> None:
        """Save or update draft and its fields atomically with audit event."""
        now = datetime.now(UTC).isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("BEGIN TRANSACTION")
            try:
                await db.execute(
                    """
                    INSERT INTO drafts (
                        draft_id, version, state, language, created_at, updated_at,
                        attempts_json, active_prompt_json, latest_transcript_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(draft_id) DO UPDATE SET
                        version=excluded.version,
                        state=excluded.state,
                        updated_at=excluded.updated_at,
                        attempts_json=excluded.attempts_json,
                        active_prompt_json=excluded.active_prompt_json,
                        latest_transcript_json=excluded.latest_transcript_json
                    """,
                    (
                        draft.draft_id,
                        draft.version,
                        draft.state.value,
                        draft.language,
                        draft.created_at,
                        now,
                        json.dumps(draft.attempts_by_field),
                        draft.active_prompt.model_dump_json() if draft.active_prompt else None,
                        draft.latest_transcript.model_dump_json()
                        if draft.latest_transcript
                        else None,
                    ),
                )

                # Upsert fields
                for k, f in draft.fields.items():
                    await db.execute(
                        """
                        INSERT INTO fields (
                            draft_id, field_key, raw_span, canonical_value,
                            status, reasons_json, source_turn_id
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(draft_id, field_key) DO UPDATE SET
                            raw_span=excluded.raw_span,
                            canonical_value=excluded.canonical_value,
                            status=excluded.status,
                            reasons_json=excluded.reasons_json,
                            source_turn_id=excluded.source_turn_id
                        """,
                        (
                            draft.draft_id,
                            k,
                            f.raw_span,
                            f.canonical_value,
                            f.status.value,
                            json.dumps(f.reasons),
                            f.source_turn_id,
                        ),
                    )

                # Add audit event
                await db.execute(
                    """
                    INSERT INTO audit_events (draft_id, event_type, version, payload_json, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        draft.draft_id,
                        event_type,
                        draft.version,
                        draft.model_dump_json(),
                        now,
                    ),
                )
                await db.commit()
            except Exception:
                await db.execute("ROLLBACK")
                raise

    async def get_draft(self, draft_id: str) -> Draft | None:
        """Fetch draft and reconstitute all fields."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM drafts WHERE draft_id = ?", (draft_id,)) as cursor:
                d_row = await cursor.fetchone()
                if not d_row:
                    return None

            fields: dict[str, FieldValue] = {}
            async with db.execute("SELECT * FROM fields WHERE draft_id = ?", (draft_id,)) as cursor:
                async for f_row in cursor:
                    fields[f_row["field_key"]] = FieldValue(
                        key=f_row["field_key"],
                        raw_span=f_row["raw_span"],
                        canonical_value=f_row["canonical_value"],
                        status=f_row["status"],
                        reasons=json.loads(f_row["reasons_json"]),
                        source_turn_id=f_row["source_turn_id"],
                    )

            active_prompt = None
            if d_row["active_prompt_json"]:
                active_prompt = json.loads(d_row["active_prompt_json"])

            latest_transcript = None
            if d_row["latest_transcript_json"]:
                latest_transcript = json.loads(d_row["latest_transcript_json"])

            return Draft(
                draft_id=d_row["draft_id"],
                version=d_row["version"],
                created_at=d_row["created_at"],
                language=d_row["language"],
                fields=fields,
                state=DraftState(d_row["state"]),
                attempts_by_field=json.loads(d_row["attempts_json"]),
                active_prompt=active_prompt,
                latest_transcript=latest_transcript,
            )

    async def record_committed(self, record_id: str, draft: Draft, idempotency_key: str) -> bool:
        """Atomically commit draft with idempotency key.

        Returns True if newly inserted, False if idempotent replay.
        """
        now = datetime.now(UTC).isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT record_id FROM committed_records WHERE idempotency_key = ?",
                (idempotency_key,),
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return False

            await db.execute(
                """
                INSERT INTO committed_records (
                    record_id, draft_id, idempotency_key, snapshot_json, committed_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    record_id,
                    draft.draft_id,
                    idempotency_key,
                    draft.model_dump_json(),
                    now,
                ),
            )
            await db.commit()
            return True

    async def delete_draft(self, draft_id: str) -> None:
        """Delete draft and associated session fields."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM fields WHERE draft_id = ?", (draft_id,))
            await db.execute("DELETE FROM drafts WHERE draft_id = ?", (draft_id,))
            await db.commit()

    async def list_committed_records(self, limit: int = 50) -> list[dict[str, Any]]:
        """List recently committed visit records for frontline audit."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """
                SELECT record_id, draft_id, idempotency_key, snapshot_json, committed_at
                FROM committed_records
                ORDER BY committed_at DESC
                LIMIT ?
                """,
                (limit,),
            ) as cursor:
                rows = await cursor.fetchall()
                results: list[dict[str, Any]] = []
                for r in rows:
                    try:
                        snapshot = json.loads(r["snapshot_json"])
                    except Exception:
                        snapshot = {}
                    results.append(
                        {
                            "record_id": r["record_id"],
                            "draft_id": r["draft_id"],
                            "idempotency_key": r["idempotency_key"],
                            "snapshot": snapshot,
                            "committed_at": r["committed_at"],
                        }
                    )
                return results

    async def close(self) -> None:
        """No-op for connection-per-query SQLite."""
        pass


class PostgresStorage:
    """Managed PostgreSQL storage implementation with async connection pooling."""

    def __init__(self, db_url: str) -> None:
        if asyncpg is None:
            raise RuntimeError(
                "asyncpg is not installed. Install it with `pip install asyncpg` to use PostgreSQL."
            )
        # Normalize postgres:// to postgresql:// for asyncpg
        if db_url.startswith("postgres://"):
            db_url = "postgresql://" + db_url[len("postgres://") :]
        self.db_url = db_url
        self.backend_name = "postgres"
        self._pool: Any = None

    async def get_pool(self) -> Any:
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                self.db_url,
                min_size=1,
                max_size=10,
                command_timeout=15,
            )
        return self._pool

    async def init_db(self) -> None:
        """Create PostgreSQL tables if they do not exist."""
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS drafts (
                    draft_id VARCHAR(64) PRIMARY KEY,
                    version INTEGER NOT NULL,
                    state VARCHAR(32) NOT NULL,
                    language VARCHAR(16) NOT NULL,
                    created_at VARCHAR(64) NOT NULL,
                    updated_at VARCHAR(64) NOT NULL,
                    attempts_json TEXT NOT NULL,
                    active_prompt_json TEXT,
                    latest_transcript_json TEXT
                );
                CREATE TABLE IF NOT EXISTS fields (
                    draft_id VARCHAR(64) NOT NULL,
                    field_key VARCHAR(64) NOT NULL,
                    raw_span TEXT,
                    canonical_value TEXT,
                    status VARCHAR(32) NOT NULL,
                    reasons_json TEXT NOT NULL,
                    source_turn_id INTEGER NOT NULL,
                    PRIMARY KEY (draft_id, field_key)
                );
                CREATE TABLE IF NOT EXISTS audit_events (
                    id BIGSERIAL PRIMARY KEY,
                    draft_id VARCHAR(64) NOT NULL,
                    event_type VARCHAR(64) NOT NULL,
                    version INTEGER NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at VARCHAR(64) NOT NULL
                );
                CREATE TABLE IF NOT EXISTS committed_records (
                    record_id VARCHAR(64) PRIMARY KEY,
                    draft_id VARCHAR(64) NOT NULL,
                    idempotency_key VARCHAR(128) NOT NULL UNIQUE,
                    snapshot_json TEXT NOT NULL,
                    committed_at VARCHAR(64) NOT NULL
                );
            """)

    async def save_draft(self, draft: Draft, event_type: str = "DRAFT_UPDATE") -> None:
        """Save or update draft and fields in a PostgreSQL transaction."""
        now = datetime.now(UTC).isoformat()
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    """
                    INSERT INTO drafts (
                        draft_id, version, state, language, created_at, updated_at,
                        attempts_json, active_prompt_json, latest_transcript_json
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    ON CONFLICT(draft_id) DO UPDATE SET
                        version = EXCLUDED.version,
                        state = EXCLUDED.state,
                        updated_at = EXCLUDED.updated_at,
                        attempts_json = EXCLUDED.attempts_json,
                        active_prompt_json = EXCLUDED.active_prompt_json,
                        latest_transcript_json = EXCLUDED.latest_transcript_json
                    """,
                    draft.draft_id,
                    draft.version,
                    draft.state.value,
                    draft.language,
                    draft.created_at,
                    now,
                    json.dumps(draft.attempts_by_field),
                    draft.active_prompt.model_dump_json() if draft.active_prompt else None,
                    draft.latest_transcript.model_dump_json() if draft.latest_transcript else None,
                )

                for k, f in draft.fields.items():
                    await conn.execute(
                        """
                        INSERT INTO fields (
                            draft_id, field_key, raw_span, canonical_value,
                            status, reasons_json, source_turn_id
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                        ON CONFLICT(draft_id, field_key) DO UPDATE SET
                            raw_span = EXCLUDED.raw_span,
                            canonical_value = EXCLUDED.canonical_value,
                            status = EXCLUDED.status,
                            reasons_json = EXCLUDED.reasons_json,
                            source_turn_id = EXCLUDED.source_turn_id
                        """,
                        draft.draft_id,
                        k,
                        f.raw_span,
                        f.canonical_value,
                        f.status.value,
                        json.dumps(f.reasons),
                        f.source_turn_id,
                    )

                await conn.execute(
                    """
                    INSERT INTO audit_events (draft_id, event_type, version, payload_json, created_at)
                    VALUES ($1, $2, $3, $4, $5)
                    """,
                    draft.draft_id,
                    event_type,
                    draft.version,
                    draft.model_dump_json(),
                    now,
                )

    async def get_draft(self, draft_id: str) -> Draft | None:
        """Fetch draft and reconstitute all fields from PostgreSQL."""
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            d_row = await conn.fetchrow("SELECT * FROM drafts WHERE draft_id = $1", draft_id)
            if not d_row:
                return None

            f_rows = await conn.fetch("SELECT * FROM fields WHERE draft_id = $1", draft_id)
            fields: dict[str, FieldValue] = {}
            for f_row in f_rows:
                fields[f_row["field_key"]] = FieldValue(
                    key=f_row["field_key"],
                    raw_span=f_row["raw_span"],
                    canonical_value=f_row["canonical_value"],
                    status=f_row["status"],
                    reasons=json.loads(f_row["reasons_json"]),
                    source_turn_id=f_row["source_turn_id"],
                )

            active_prompt = None
            if d_row["active_prompt_json"]:
                active_prompt = json.loads(d_row["active_prompt_json"])

            latest_transcript = None
            if d_row["latest_transcript_json"]:
                latest_transcript = json.loads(d_row["latest_transcript_json"])

            return Draft(
                draft_id=d_row["draft_id"],
                version=d_row["version"],
                created_at=d_row["created_at"],
                language=d_row["language"],
                fields=fields,
                state=DraftState(d_row["state"]),
                attempts_by_field=json.loads(d_row["attempts_json"]),
                active_prompt=active_prompt,
                latest_transcript=latest_transcript,
            )

    async def record_committed(self, record_id: str, draft: Draft, idempotency_key: str) -> bool:
        """Atomically commit draft with idempotency key in PostgreSQL."""
        now = datetime.now(UTC).isoformat()
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            async with conn.transaction():
                row = await conn.fetchrow(
                    "SELECT record_id FROM committed_records WHERE idempotency_key = $1",
                    idempotency_key,
                )
                if row:
                    return False

                await conn.execute(
                    """
                    INSERT INTO committed_records (
                        record_id, draft_id, idempotency_key, snapshot_json, committed_at
                    ) VALUES ($1, $2, $3, $4, $5)
                    """,
                    record_id,
                    draft.draft_id,
                    idempotency_key,
                    draft.model_dump_json(),
                    now,
                )
                return True

    async def delete_draft(self, draft_id: str) -> None:
        """Delete draft and associated session fields."""
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("DELETE FROM fields WHERE draft_id = $1", draft_id)
                await conn.execute("DELETE FROM drafts WHERE draft_id = $1", draft_id)

    async def list_committed_records(self, limit: int = 50) -> list[dict[str, Any]]:
        """List recently committed visit records from PostgreSQL."""
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT record_id, draft_id, idempotency_key, snapshot_json, committed_at
                FROM committed_records
                ORDER BY committed_at DESC
                LIMIT $1
                """,
                limit,
            )
            results: list[dict[str, Any]] = []
            for r in rows:
                try:
                    snapshot = json.loads(r["snapshot_json"])
                except Exception:
                    snapshot = {}
                results.append(
                    {
                        "record_id": r["record_id"],
                        "draft_id": r["draft_id"],
                        "idempotency_key": r["idempotency_key"],
                        "snapshot": snapshot,
                        "committed_at": r["committed_at"],
                    }
                )
            return results

    async def close(self) -> None:
        """Close connection pool."""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None


class Storage:
    """Unified storage interface routing dynamically between PostgreSQL and SQLite."""

    def __init__(
        self,
        db_path: str = "sureword.db",
        database_url: str | None = None,
    ) -> None:
        target = (
            database_url
            or os.getenv("DATABASE_URL")
            or db_path
            or os.getenv("DATABASE_PATH")
            or "sureword.db"
        )
        self._target_url: str = target
        self._backend = self._create_backend(self._target_url)

    def _create_backend(self, url: str) -> SQLiteStorage | PostgresStorage:
        if url.startswith("postgres://") or url.startswith("postgresql://"):
            return PostgresStorage(db_url=url)
        return SQLiteStorage(db_path=url)

    @property
    def db_path(self) -> str:
        if isinstance(self._backend, SQLiteStorage):
            return self._backend.db_path
        if isinstance(self._backend, PostgresStorage):
            return self._backend.db_url
        return self._target_url

    @db_path.setter
    def db_path(self, val: str) -> None:
        self._target_url = val
        self._backend = self._create_backend(val)

    @property
    def backend_name(self) -> str:
        return self._backend.backend_name

    async def init_db(self) -> None:
        await self._backend.init_db()

    async def save_draft(self, draft: Draft, event_type: str = "DRAFT_UPDATE") -> None:
        await self._backend.save_draft(draft=draft, event_type=event_type)

    async def get_draft(self, draft_id: str) -> Draft | None:
        return await self._backend.get_draft(draft_id=draft_id)

    async def record_committed(self, record_id: str, draft: Draft, idempotency_key: str) -> bool:
        return await self._backend.record_committed(
            record_id=record_id, draft=draft, idempotency_key=idempotency_key
        )

    async def delete_draft(self, draft_id: str) -> None:
        await self._backend.delete_draft(draft_id=draft_id)

    async def list_committed_records(self, limit: int = 50) -> list[dict[str, Any]]:
        return await self._backend.list_committed_records(limit=limit)

    async def close(self) -> None:
        await self._backend.close()
