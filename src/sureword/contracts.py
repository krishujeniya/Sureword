"""Typed Pydantic contracts and domain models for Sureword."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class FieldStatus(StrEnum):
    MISSING = "missing"
    PROPOSED = "proposed"
    NEEDS_REPEAT = "needs_repeat"
    USER_CONFIRMED = "user_confirmed"
    MANUALLY_EDITED = "manually_edited"


class DraftState(StrEnum):
    EMPTY = "EMPTY"
    CAPTURING = "CAPTURING"
    TRANSCRIBING = "TRANSCRIBING"
    DRAFT = "DRAFT"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    COMMITTED = "COMMITTED"
    ERROR = "ERROR"


class FieldKey(StrEnum):
    PERSON_NAME = "person_name"
    AGE = "age"
    VILLAGE = "village"
    VISIT_DATE = "visit_date"
    GENDER = "gender"
    SYMPTOMS = "symptoms"


class FieldValue(BaseModel):
    key: str
    raw_span: str | None = None
    canonical_value: str | None = None
    status: FieldStatus = FieldStatus.MISSING
    reasons: list[str] = Field(default_factory=list)
    source_turn_id: int = 0


class Transcript(BaseModel):
    text: str
    provider: str = "gnani_prisma"
    requested_model: str = "prisma-v3"
    effective_model: str | None = None
    request_id: str | None = None
    duration_ms: float = 0.0
    confidence: float | None = None
    source: str = "live"  # "live", "cache", or "fixture"


class ClarificationPrompt(BaseModel):
    target_field: str
    prompt_text: str
    tts_audio_base64: str | None = None
    attempt_number: int = 1


class Draft(BaseModel):
    draft_id: str
    version: int = 1
    created_at: str
    language: str = "hi-IN"
    fields: dict[str, FieldValue] = Field(default_factory=dict)
    state: DraftState = DraftState.EMPTY
    attempts_by_field: dict[str, int] = Field(default_factory=dict)
    active_prompt: ClarificationPrompt | None = None
    latest_transcript: Transcript | None = None


class DraftCreateResponse(BaseModel):
    draft_id: str
    version: int
    state: DraftState


class AudioProcessResponse(BaseModel):
    draft: Draft
    transcript: Transcript
    next_action: str  # "CLARIFY" | "REVIEW" | "ERROR"


class ClarifyRequest(BaseModel):
    target_field: str
    expected_version: int
    manual_value: str | None = None


class CommitRequest(BaseModel):
    expected_version: int
    idempotency_key: str


class CommitResponse(BaseModel):
    record_id: str
    status: str
    draft: Draft


class ErrorDetail(BaseModel):
    code: str
    retryable: bool
    user_message: str
    request_id: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)
