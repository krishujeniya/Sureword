# Sureword — System Architecture & Design

> **Document ID:** DOC-SW-ARCH-01  
> **Status:** Production Specification  
> **Author:** Krish Ujeniya  

---

## 1. System Overview

Sureword is an asynchronous reliability layer for voice-driven structured record entry in frontline Indian public health workflows. When frontline health workers (such as ASHAs or ANMs) dictate visit records, phonetic similarities and code-mixed speech often cause automated speech recognition (ASR) engines to silently substitute critical entities (e.g. names, ages, villages, or dates).

Sureword uses Gnani Prisma for speech-to-text, parses structured fields deterministically, computes uncertainty-driven risk scores per field, and uses Gnani Timbre to issue spoken clarification requests for *only* the single most uncertain field before committing the record.

```
┌────────────────────────────────────────────────────────┐
│                   Frontline User                       │
│        (Browser UI / Audio Dictation / Voice)          │
└───────────────────────┬────────────────────────────────┘
                        │ HTTP POST / WebSocket
                        ▼
┌────────────────────────────────────────────────────────┐
│                   FastAPI Core                         │
│               (src/sureword/app.py)                    │
└───────┬───────────────────────┬────────────────────────┘
        │                       │
        ▼                       ▼
┌───────────────┐       ┌────────────────────────────────┐
│ Audio Engine  │       │     State Machine & Storage    │
│  (audio.py)   │       │   (state.py / storage.py)      │
└───────┬───────┘       └────────────────┬───────────────┘
        │                                │
        ▼                                │
┌───────────────┐                        │
│ Gnani Provider│                        │
│(providers/    │                        │
│   gnani.py)   │                        │
└───────┬───────┘                        │
        │ STT Output                     │
        ▼                                │
┌───────────────┐                        │
│ Field Parser  │                        │
│  (parser.py)  │                        │
└───────┬───────┘                        │
        │ Parsed Fields                  │
        ▼                                │
┌───────────────┐                        │
│ Policy Engine │────────────────────────┘
│  (policy.py)  │   Targeted Clarification Prompt
└───────┬───────┘
        │ Timbre TTS
        ▼
┌───────────────┐
│ Clarification │
│    Spoken     │
└───────────────┘
```

---

## 2. Component Hierarchy & Module Boundaries

The code adheres to the standard PyPA `src-layout` with explicit boundaries:

| Module | Responsibility | Key Invariants |
|---|---|---|
| `contracts.py` | Pydantic v2 schemas, domain enums, type definitions | Pure data contracts, immutability, ISO 8601 parsing |
| `app.py` | FastAPI application endpoints, lifespans, static mounts | REST contracts, JSON error schemas, no direct DB queries |
| `state.py` | Draft lifecycle state machine (`DraftStateMachine`) | Enforces valid state transitions: `EMPTY` → `DICTATED` → `NEEDS_CLARIFICATION` → `READY_FOR_REVIEW` → `COMMITTED` |
| `storage.py` | Asynchronous SQLite persistence (`aiosqlite`) | Idempotent draft commit, transactional version incrementing |
| `audio.py` | Audio normalization (16kHz mono WAV), duration checks | 20s maximum length check, ffmpeg conversion, temporary file cleanup |
| `parser.py` | Entity extraction and deterministic field normalization | Normalizes Indic numbers, calendar dates, Indian names, village boundaries |
| `policy.py` | Risk ranking and clarification policy (`rank_fields_by_risk`) | Missing=1.0, Format violation=0.8, Dictionary conflict=0.5, Confirmed=0.0 |
| `providers/gnani.py`| Gnani Prisma STT and Timbre TTS client adapter | Timeout handling, exponential backoff, fixture fallbacks |

---

## 3. Draft State Machine Lifecycle

```
       ┌───────────┐
       │   EMPTY   │
       └─────┬─────┘
             │ Audio Dictated
             ▼
       ┌───────────┐
       │ DICTATED  │
       └─────┬─────┘
             │
      ───────┴───────
     │               │
     ▼ (Uncertain)   ▼ (All Valid)
┌─────────────┐ ┌──────────────────┐
│    NEEDS_   │ │ READY_FOR_REVIEW │
│CLARIFICATION│ └────────┬─────────┘
└──────┬──────┘          │
       │ Clarified       │ Explicit Review & Commit
       └─────▶───────────┤
                         ▼
                  ┌─────────────┐
                  │  COMMITTED  │
                  └─────────────┘
```

---

## 4. Policy Engine & Risk Ranking

Sureword implements and compares 5 policies under identical clarification constraints (max 1 prompt/turn):

1. **B0 (Raw ASR):** No clarification; all fields accepted directly from transcription.
2. **B1 (Alphabetical):** Prompts for invalid fields first, then falls back to alphabetical order.
3. **B2 (Random):** Randomly selects among unconfirmed fields.
4. **P (Selective Risk Ranking):** Prioritizes fields by composite risk score (Missing > Bounds Error > Low Confidence > Ambiguous).
5. **B3 (Full Confirmation):** Prompts for every field sequentially (unconstrained upper bound).
