"""FastAPI application for Sureword."""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, Request, Response, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from sureword.audio import AudioValidationError, convert_and_normalize_audio
from sureword.contracts import (
    AudioProcessResponse,
    CommitRequest,
    CommitResponse,
    Draft,
    DraftCreateResponse,
    DraftState,
    FieldKey,
    FieldStatus,
    FieldValue,
    Transcript,
)
from sureword.languages import GNANI_LANGUAGES
from sureword.parser import (
    parse_age,
    parse_date,
    parse_person_name,
    parse_village,
    parse_visit_form,
)
from sureword.providers.gnani import GnaniClient, GnaniProviderError
from sureword.state import DraftStateMachine, StateTransitionError
from sureword.storage import Storage

# Paths & Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
default_db = (
    "/tmp/sureword.db"
    if (os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))
    else "sureword.db"
)
DATABASE_URL = os.getenv("DATABASE_URL")
DB_PATH = os.getenv("DATABASE_PATH", default_db)
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", "10485760"))

# Components
storage = Storage(db_path=DB_PATH, database_url=DATABASE_URL)
state_machine = DraftStateMachine(storage=storage)
gnani_client = GnaniClient()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize database tables on startup and release connections on shutdown."""
    await storage.init_db()
    yield
    await storage.close()


app = FastAPI(
    title="Sureword API",
    description="Selective voice-to-form clarification for frontline healthcare visit entry",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS Middleware (GitHub Pages + Local Development Support)
cors_origins_env = os.getenv("CORS_ORIGINS", "")
allowed_origins = [
    "https://krishujeniya.github.io",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]
if cors_origins_env:
    for origin in cors_origins_env.split(","):
        cleaned = origin.strip()
        if cleaned and cleaned not in allowed_origins:
            allowed_origins.append(cleaned)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"^https://([a-zA-Z0-9-]+\.)*github\.io$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["Content-Length", "X-Draft-Version", "Content-Type"],
    max_age=86400,
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next: Callable[[Request], Any]) -> Response:
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response


@app.api_route("/healthz", methods=["GET", "HEAD"])
async def health_check() -> dict[str, str | bool]:
    """Health check endpoint without expensive third-party calls."""
    db_status = "postgres_ready" if storage.backend_name == "postgres" else "sqlite_ready"
    return {
        "status": "healthy",
        "database": db_status,
        "storage_backend": storage.backend_name,
        "gnani_configured": gnani_client.has_credentials(),
        "allow_fixture_fallback": gnani_client.allow_fixture_fallback,
    }


@app.post("/api/drafts", response_model=DraftCreateResponse)
async def create_draft(
    request: Request,
    language: str | None = None,
) -> DraftCreateResponse:
    """Create a new visit draft session."""
    selected_lang = language
    if not selected_lang:
        content_type = request.headers.get("content-type", "")
        if (
            "application/x-www-form-urlencoded" in content_type
            or "multipart/form-data" in content_type
        ):
            try:
                form = await request.form()
                val = form.get("language")
                if val and isinstance(val, str):
                    selected_lang = val
            except Exception:
                pass
        elif "application/json" in content_type:
            try:
                body = await request.json()
                val = body.get("language")
                if val and isinstance(val, str):
                    selected_lang = val
            except Exception:
                pass

    if not selected_lang or not isinstance(selected_lang, str):
        selected_lang = "hi-IN"

    draft = await state_machine.create_draft(language=selected_lang)
    return DraftCreateResponse(
        draft_id=draft.draft_id,
        version=draft.version,
        state=draft.state,
    )


@app.get("/api/drafts/{draft_id}", response_model=Draft)
async def get_draft(draft_id: str) -> Draft:
    """Get current draft state and fields."""
    draft = await storage.get_draft(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return draft


@app.post("/api/drafts/{draft_id}/audio", response_model=AudioProcessResponse)
async def process_draft_audio(
    draft_id: str,
    expected_version: int = Form(...),
    audio_file: UploadFile | None = File(None),
    simulated_transcript: str | None = Form(None),
) -> AudioProcessResponse:
    """Process dictated speech: normalize audio -> Prisma STT -> parse fields -> update state."""
    draft = await storage.get_draft(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    if simulated_transcript and simulated_transcript.strip():
        transcript = Transcript(
            text=simulated_transcript.strip(),
            provider="gnani_prisma",
            requested_model="prisma-v3",
            effective_model="prisma-v3-preset",
            request_id=f"preset-{draft_id[:8]}",
            duration_ms=185.0,
            confidence=0.96,
            source="preset",
        )
    else:
        if not audio_file:
            raise HTTPException(
                status_code=400, detail="Must provide either audio_file or simulated_transcript"
            )
        raw_bytes = await audio_file.read()
        if len(raw_bytes) > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"Audio payload exceeds limit of {MAX_UPLOAD_BYTES // (1024 * 1024)}MB",
            )
        try:
            audio_info = convert_and_normalize_audio(raw_bytes)
        except AudioValidationError as ave:
            raise HTTPException(status_code=400, detail=str(ave)) from ave

        try:
            transcript = await gnani_client.transcribe_audio(
                audio_info.wav_bytes, language=draft.language
            )
        except GnaniProviderError as gpe:
            status_code = gpe.status_code if gpe.status_code and gpe.status_code >= 400 else 502
            raise HTTPException(
                status_code=status_code, detail=f"Speech-to-text error: {gpe}"
            ) from gpe

    # Deterministic extraction of the 4 fields
    parsed_fields = parse_visit_form(transcript.text)

    try:
        updated_draft = await state_machine.apply_audio_parse(
            draft_id=draft_id,
            expected_version=expected_version,
            transcript=transcript,
            parsed_fields=parsed_fields,
        )
    except StateTransitionError as ste:
        if ste.code == "STALE_VERSION":
            raise HTTPException(status_code=409, detail=str(ste)) from ste
        raise HTTPException(status_code=400, detail=str(ste)) from ste

    next_act = "CLARIFY" if updated_draft.state == DraftState.NEEDS_CLARIFICATION else "REVIEW"

    return AudioProcessResponse(
        draft=updated_draft,
        transcript=transcript,
        next_action=next_act,
    )


@app.post("/api/drafts/{draft_id}/clarify", response_model=Draft)
async def clarify_field(
    draft_id: str,
    target_field: str = Form(...),
    expected_version: int = Form(...),
    manual_value: str | None = Form(None),
    audio_file: UploadFile | None = File(None),
) -> Draft:
    """Apply targeted clarification via typed manual edit or repeated voice."""
    draft = await storage.get_draft(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    if not manual_value and not audio_file:
        raise HTTPException(
            status_code=400, detail="Must provide either manual_value or audio_file"
        )

    if manual_value is not None and manual_value.strip():
        # Manual edit takes precedence
        updated_field = FieldValue(
            key=target_field,
            raw_span=manual_value.strip(),
            canonical_value=manual_value.strip(),
            status=FieldStatus.MANUALLY_EDITED,
            reasons=["Manually edited and verified by user"],
        )
    else:
        # Audio repeat of single field
        assert audio_file is not None
        raw_bytes = await audio_file.read()
        if len(raw_bytes) > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"Audio payload exceeds limit of {MAX_UPLOAD_BYTES // (1024 * 1024)}MB",
            )
        try:
            audio_info = convert_and_normalize_audio(raw_bytes)
        except AudioValidationError as ave:
            raise HTTPException(status_code=400, detail=str(ave)) from ave

        try:
            transcript = await gnani_client.transcribe_audio(
                audio_info.wav_bytes, language=draft.language
            )
        except GnaniProviderError as gpe:
            raise HTTPException(
                status_code=502, detail=f"Speech clarification error: {gpe}"
            ) from gpe

        # Targeted parser for specific field
        if target_field == FieldKey.PERSON_NAME.value:
            updated_field = parse_person_name(transcript.text)
        elif target_field == FieldKey.AGE.value:
            updated_field = parse_age(transcript.text)
        elif target_field == FieldKey.VILLAGE.value:
            updated_field = parse_village(transcript.text)
        elif target_field == FieldKey.VISIT_DATE.value:
            updated_field = parse_date(transcript.text)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown target field: {target_field}")

        if updated_field.status == FieldStatus.PROPOSED:
            updated_field.status = FieldStatus.USER_CONFIRMED
            updated_field.reasons.append("Clarified and confirmed via spoken repeat")

    try:
        updated_draft = await state_machine.apply_clarification(
            draft_id=draft_id,
            expected_version=expected_version,
            target_field=target_field,
            updated_field=updated_field,
        )
    except StateTransitionError as ste:
        if ste.code == "STALE_VERSION":
            raise HTTPException(status_code=409, detail=str(ste)) from ste
        raise HTTPException(status_code=400, detail=str(ste)) from ste

    return updated_draft


@app.post("/api/drafts/{draft_id}/speech")
async def get_clarification_speech(draft_id: str) -> Response:
    """Return synthesized Timbre TTS audio for the draft's active clarification prompt."""
    draft = await storage.get_draft(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    if not draft.active_prompt:
        raise HTTPException(status_code=400, detail="Draft has no active clarification prompt")

    try:
        audio_bytes = await gnani_client.synthesize_speech(
            text=draft.active_prompt.prompt_text,
            language=draft.language,
        )
    except GnaniProviderError as gpe:
        raise HTTPException(status_code=502, detail=f"Text-to-speech error: {gpe}") from gpe

    return Response(content=audio_bytes, media_type="audio/wav")


@app.post("/api/drafts/{draft_id}/commit", response_model=CommitResponse)
async def commit_draft(
    draft_id: str,
    req: CommitRequest,
) -> CommitResponse:
    """Explicit whole-form review and idempotent commit."""
    try:
        record_id, draft = await state_machine.commit_draft(
            draft_id=draft_id,
            expected_version=req.expected_version,
            idempotency_key=req.idempotency_key,
        )
    except StateTransitionError as ste:
        if ste.code == "STALE_VERSION":
            raise HTTPException(status_code=409, detail=str(ste)) from ste
        raise HTTPException(status_code=400, detail=str(ste)) from ste

    return CommitResponse(
        record_id=record_id,
        status="COMMITTED",
        draft=draft,
    )


@app.delete("/api/drafts/{draft_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_draft(draft_id: str) -> None:
    """Delete draft session."""
    await storage.delete_draft(draft_id)


@app.get("/api/records")
async def get_committed_records() -> list[dict[str, Any]]:
    """List recent committed visit records for frontline audit and reporting."""
    return await storage.list_committed_records()


@app.get("/api/languages")
async def get_supported_languages() -> list[dict[str, str]]:
    """Return all 11 Indic and English languages supported by Gnani Prisma & Timbre."""
    return [
        {
            "code": meta.code,
            "name": meta.name,
            "native_name": meta.native_name,
            "script": meta.script,
            "sample_script": meta.sample_script,
        }
        for meta in GNANI_LANGUAGES.values()
    ]


# Mount static assets
STATIC_ASSETS = {
    "styles.css": "text/css",
    "design.css": "text/css",
    "app.js": "application/javascript",
    "experience.js": "application/javascript",
    "logo.svg": "image/svg+xml",
    "favicon.svg": "image/svg+xml",
}

if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    app.mount("/Sureword", StaticFiles(directory=STATIC_DIR, html=True), name="sureword_preview")


@app.get("/")
async def serve_index() -> FileResponse:
    """Serve the single-page application UI."""
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    raise HTTPException(status_code=404, detail="UI index.html not found")


@app.api_route("/{asset_name}", methods=["GET", "HEAD"])
async def serve_root_asset(asset_name: str) -> FileResponse:
    """Serve root-relative static assets for decoupled frontend hosting compatibility."""
    if asset_name in STATIC_ASSETS:
        asset_path = os.path.join(STATIC_DIR, asset_name)
        if os.path.isfile(asset_path):
            return FileResponse(asset_path, media_type=STATIC_ASSETS[asset_name])
    raise HTTPException(status_code=404, detail="Not Found")
