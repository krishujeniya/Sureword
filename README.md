# FieldCheck

> **Voice-to-Form Frontline Visit Entry with Selective Clarification**  
> Built for the Great Indian AI Internship Challenge 2026.  
> Real speech-to-text via **Gnani Prisma** and spoken clarification via **Gnani Timbre**.

---

## 1. Overview & Problem

In Indian frontline healthcare workflows (such as ASHA household survey visits and ANM tablet entry), workers collect critical structured information under noisy conditions and time pressure. Standard automated speech recognition (ASR) outputs often look fluent while silently transcribing critical fields incorrectly—such as patient name, age, village, or visit date.

**FieldCheck** introduces a selective clarification reliability layer:
1. Dictation of visit details in conversational Hindi-English code-mix.
2. Transcription via **Gnani Prisma**.
3. Deterministic parsing and physiological/format validation into four core fields (`person_name`, `age`, `village`, `visit_date`).
4. Risk ranking: evaluating missingness, parse ambiguity, out-of-range bounds, and dictionary conflicts.
5. Focused spoken clarification via **Gnani Timbre**: asking the user to repeat *only* the single most uncertain field within a fixed clarification budget, rather than re-dictating the whole form.
6. Explicit human review and idempotent local commit before saving.

---

## 2. Architecture & Contracts

FieldCheck uses an async Python service (FastAPI + Pydantic v2 + SQLite) with an accessible, lightweight web interface:

```text
Browser Mic / Audio Upload
        │
        ▼
   Audio Validation (16kHz mono WAV normalization, max 20s, ffmpeg)
        │
        ▼
   Gnani Prisma Adapter (live STT / cached / fixture fallback)
        │
        ▼
   Deterministic Field Parser & Normalizer
   - person_name: title-case normalization, marker extraction
   - age: Hindi number words, Devanagari numerals, range check (1-120)
   - village: directory lookup & context boundary
   - visit_date: ISO 8601 validation (YYYY-MM-DD), rejection of invalid calendar dates
        │
        ▼
   Selective Risk Policy (identifies single highest-uncertainty field)
        │
        ├─▶ Uncertain: Spoken prompt generated via Gnani Timbre TTS
        │             User repeats field ──▶ Field updated with provenance
        │
        └─▶ Valid: Draft enters READY_FOR_REVIEW
                    Explicit user confirmation ──▶ Idempotent local SQLite commit
```

### Core API Endpoints

- `POST /api/drafts`: Initialize a new draft session.
- `POST /api/drafts/{id}/audio`: Process raw audio through Prisma STT and field parser.
- `POST /api/drafts/{id}/clarify`: Submit spoken or typed clarification for a targeted field.
- `POST /api/drafts/{id}/speech`: Retrieve spoken clarification audio via Timbre TTS.
- `POST /api/drafts/{id}/commit`: Explicitly review and save the final draft.
- `GET /healthz`: Service health and capability check.

---

## 3. Quickstart

### Prerequisites
- Python 3.11+
- `ffmpeg` installed on the system path
- `uv` package manager (recommended) or standard `pip`

### Setup

```bash
# Clone and enter directory
cd /path/to/gnani

# Create virtual environment and install dependencies
uv venv --python python3.11
source .venv/bin/activate
uv pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env and supply your GNANI_API_KEY if testing live API calls
```

### Run the Application

```bash
python -m uvicorn fieldcheck.app:app --host 127.0.0.1 --port 8000 --reload
```

Open `http://127.0.0.1:8000` in your web browser.

---

## 4. Verification & Testing

FieldCheck adheres to strict verification discipline:

```bash
# Unit tests (parser, risk ranking, state machine, audio normalizer)
pytest tests/unit -v

# Integration tests (Gnani adapter, failure handling, timeouts, retries)
pytest tests/integration -v

# Static analysis and type checking
ruff check src tests scripts
mypy src/fieldcheck
```

---

## 5. Research Protocol & Hypotheses

- **Primary Research Question:** At an equal clarification budget (maximum 1 prompt per form), does selective uncertainty-ranked clarification reduce accepted critical-field errors compared to simple sequential verification?
- **Baselines Evaluated:**
  - `B0`: Raw Prisma transcript without verification.
  - `B1`: Schema violations first, then fixed field order.
  - `B2`: Seeded random field selection.
  - `B3`: Full confirmation of every field (unconstrained upper bound).
  - `P`: Proposed field-aware risk ranking.
- **Metrics Reported:**
  - Primary Accepted-Field Error (`wrong_accepted / total_accepted`)
  - Automatic Coverage (`accepted_fields / expected_fields`)
  - Whole-Record Correctness
  - Realized Clarification Burden (prompts / form)

---

## 6. Responsible Disclosure & Limitations

1. **Simulated Workflow:** The prototype uses fictional role-play data. It is not approved for actual clinical diagnosis, triage, or live medical records.
2. **Privacy by Design:** Temporary audio is normalized, processed, and immediately removed. No raw audio is retained in public logs or persistent storage.
3. **No Fabricated Performance:** Live API calls require a valid `GNANI_API_KEY`. When running in offline or fixture mode, provenance is clearly labeled in both the UI and JSON responses.
