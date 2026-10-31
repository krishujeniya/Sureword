"""Versioned state machine and draft lifecycle transitions."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fieldcheck.contracts import (
    Draft,
    DraftState,
    FieldKey,
    FieldStatus,
    FieldValue,
    Transcript,
)
from fieldcheck.policy import select_clarification_field_p
from fieldcheck.storage import Storage


class StateTransitionError(Exception):
    """Raised when an illegal state transition or version mismatch occurs."""

    def __init__(self, message: str, code: str = "INVALID_STATE_TRANSITION") -> None:
        super().__init__(message)
        self.code = code


class DraftStateMachine:
    def __init__(self, storage: Storage) -> None:
        self.storage = storage

    async def create_draft(self, language: str = "hi-IN") -> Draft:
        """Create new empty draft with initialized default fields."""
        draft_id = f"draft_{uuid.uuid4().hex[:12]}"
        now = datetime.now(UTC).isoformat()

        initial_fields = {
            FieldKey.PERSON_NAME.value: FieldValue(key=FieldKey.PERSON_NAME.value),
            FieldKey.AGE.value: FieldValue(key=FieldKey.AGE.value),
            FieldKey.VILLAGE.value: FieldValue(key=FieldKey.VILLAGE.value),
            FieldKey.VISIT_DATE.value: FieldValue(key=FieldKey.VISIT_DATE.value),
        }

        draft = Draft(
            draft_id=draft_id,
            version=1,
            created_at=now,
            language=language,
            fields=initial_fields,
            state=DraftState.EMPTY,
            attempts_by_field={},
        )
        await self.storage.save_draft(draft, event_type="DRAFT_CREATED")
        return draft

    async def apply_audio_parse(
        self,
        draft_id: str,
        expected_version: int,
        transcript: Transcript,
        parsed_fields: dict[str, FieldValue],
    ) -> Draft:
        """Apply newly parsed fields from an audio transcription turn."""
        draft = await self.storage.get_draft(draft_id)
        if not draft:
            raise StateTransitionError(f"Draft {draft_id} not found", "DRAFT_NOT_FOUND")

        if draft.version != expected_version:
            raise StateTransitionError(
                f"Version mismatch: draft is at v{draft.version}, expected v{expected_version}",
                "STALE_VERSION",
            )

        if draft.state == DraftState.COMMITTED:
            raise StateTransitionError("Cannot modify an already committed draft", "ALREADY_COMMITTED")

        # Update fields
        for k, new_f in parsed_fields.items():
            current_f = draft.fields.get(k)
            # If current field was already manually edited or confirmed, preserve unless new turn explicitly overrides
            if current_f and current_f.status in {FieldStatus.MANUALLY_EDITED, FieldStatus.USER_CONFIRMED}:
                continue
            draft.fields[k] = new_f

        draft.latest_transcript = transcript
        draft.version += 1

        # Check whether any field requires clarification under Policy P
        prompt = select_clarification_field_p(
            draft.fields,
            draft.attempts_by_field,
            max_attempts=2,
            risk_threshold=0.3,
        )

        if prompt:
            draft.state = DraftState.NEEDS_CLARIFICATION
            draft.active_prompt = prompt
        else:
            draft.state = DraftState.READY_FOR_REVIEW
            draft.active_prompt = None

        await self.storage.save_draft(draft, event_type="AUDIO_PARSED")
        return draft

    async def apply_clarification(
        self,
        draft_id: str,
        expected_version: int,
        target_field: str,
        updated_field: FieldValue,
    ) -> Draft:
        """Apply targeted clarification (spoken repeat or manual edit)."""
        draft = await self.storage.get_draft(draft_id)
        if not draft:
            raise StateTransitionError(f"Draft {draft_id} not found", "DRAFT_NOT_FOUND")

        if draft.version != expected_version:
            raise StateTransitionError(
                f"Version mismatch: draft is at v{draft.version}, expected v{expected_version}",
                "STALE_VERSION",
            )

        if draft.state == DraftState.COMMITTED:
            raise StateTransitionError("Cannot modify an already committed draft", "ALREADY_COMMITTED")

        # Update field and track attempts
        draft.fields[target_field] = updated_field
        draft.attempts_by_field[target_field] = draft.attempts_by_field.get(target_field, 0) + 1
        draft.version += 1

        # Evaluate if another field needs clarification
        prompt = select_clarification_field_p(
            draft.fields,
            draft.attempts_by_field,
            max_attempts=2,
            risk_threshold=0.3,
        )

        if prompt:
            draft.state = DraftState.NEEDS_CLARIFICATION
            draft.active_prompt = prompt
        else:
            draft.state = DraftState.READY_FOR_REVIEW
            draft.active_prompt = None

        await self.storage.save_draft(draft, event_type="FIELD_CLARIFIED")
        return draft

    async def commit_draft(
        self, draft_id: str, expected_version: int, idempotency_key: str
    ) -> tuple[str, Draft]:
        """Validate and commit a draft."""
        draft = await self.storage.get_draft(draft_id)
        if not draft:
            raise StateTransitionError(f"Draft {draft_id} not found", "DRAFT_NOT_FOUND")

        if draft.version != expected_version:
            raise StateTransitionError(
                f"Version conflict: draft is at v{draft.version}, request sent v{expected_version}",
                "STALE_VERSION",
            )

        if draft.state == DraftState.NEEDS_CLARIFICATION:
            raise StateTransitionError(
                "Cannot commit draft while clarification is pending. Resolve uncertain fields first.",
                "CLARIFICATION_PENDING",
            )

        # Enforce all required fields are present and valid
        for k in (
            FieldKey.PERSON_NAME.value,
            FieldKey.AGE.value,
            FieldKey.VILLAGE.value,
            FieldKey.VISIT_DATE.value,
        ):
            f = draft.fields.get(k)
            if not f or f.status in {FieldStatus.MISSING, FieldStatus.NEEDS_REPEAT} or not f.canonical_value:
                raise StateTransitionError(
                    f"Cannot commit: field '{k}' is unresolved ({f.status if f else 'missing'})",
                    "UNRESOLVED_FIELD",
                )

        record_id = f"REC-{datetime.now(UTC).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        draft.state = DraftState.COMMITTED
        draft.version += 1

        await self.storage.record_committed(record_id, draft, idempotency_key)
        await self.storage.save_draft(draft, event_type="DRAFT_COMMITTED")
        return record_id, draft
