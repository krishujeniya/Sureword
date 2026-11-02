"""SQLite asynchronous storage and event auditing for Sureword."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from typing import Any

import aiosqlite

from sureword.contracts import Draft, DraftState, FieldValue


class Storage:
    def __init__(self, db_path: str = "sureword.db") -> None:
        self.db_path = db_path

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
            # Check existing idempotency key
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
