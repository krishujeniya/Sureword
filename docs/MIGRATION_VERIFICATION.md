# Sureword Migration & Verification Report

## 1. Executive Summary

Sureword was audited, refactored, and verified for production decoupled hosting:
- **Frontend**: Static single-page application hosted independently on GitHub Pages (`https://krishujeniya.github.io/Sureword/`).
- **Backend**: FastAPI serverless service hosted on Vercel (`https://sureword.vercel.app/`).
- **Persistence**: Hybrid transactional storage engine supporting local/ephemeral SQLite and production-grade managed PostgreSQL (`asyncpg`).
- **AI Integrations**: Gnani Prisma STT and Timbre TTS called exclusively server-side without exposing API keys to the browser.
- **Backward Compatibility**: The existing Vercel deployment continues serving both API endpoints and the full web UI at `https://sureword.vercel.app/` without disruption.

---

## 2. Phase-by-Phase Verification Matrix

| Phase | Description | Status | Evidence / Artifact |
|---|---|---|---|
| **Phase 1** | Repository Audit | Verified | Complete inspection of static assets, FastAPI routes, contracts, audio pipeline, and existing test suite. |
| **Phase 2** | Static Frontend Migration | Verified | Assets decoupled into standalone bundle; root-relative `/static/` paths converted to relative references; `/Sureword/` base path configured. |
| **Phase 3** | API Integration | Verified | Centralized `API_CONFIG` and `apiFetch()` with timeout, configurable base URL, and domain auto-detection (`*.github.io` -> `https://sureword.vercel.app`). |
| **Phase 4** | Persistent Backend Storage | Verified | PostgreSQL adapter via `asyncpg` added alongside SQLite; transaction boundaries, optimistic locking, and commit idempotency preserved across 77 tests. |
| **Phase 5** | Frontend & Backend Security | Verified | Strict CORS middleware (`CORSMiddleware`), preflight `OPTIONS` handling, upload payload limits (10MB), no-cache headers for sensitive visit records, zero frontend secrets. |
| **Phase 6** | GitHub Actions Pipeline | Verified | `.github/workflows/deploy-frontend.yml` created with syntax checks, asset validation, secret scanning, and automated Pages deployment. |
| **Phase 7** | Functional & Browser Validation | Verified | 77 pytest tests pass; Playwright test suite passes across 8 viewports, keyboard navigation, and error recovery states. |

---

## 3. Storage Layer Architecture (Phase 4)

Vercel functions run in ephemeral serverless execution sandboxes where `/tmp` is wiped between cold starts and instances do not share state.

### Dual-Engine Storage Design
`src/sureword/storage.py` implements a unified `Storage` interface that dynamically routes based on the configured connection string:

```
                  ┌──────────────────────┐
                  │   Storage Interface  │
                  └──────────┬───────────┘
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
   DATABASE_URL present?              DATABASE_URL empty
(postgres:// or postgresql://)        or SQLite file path
            │                                 │
            ▼                                 ▼
┌──────────────────────┐           ┌──────────────────────┐
│   PostgresStorage    │           │    SQLiteStorage     │
│   (asyncpg pool)     │           │     (aiosqlite)      │
│  - Neon / Supabase   │           │  - Local dev / tests │
│  - Persistent prod   │           │  - Offline fixtures  │
└──────────────────────┘           └──────────────────────┘
```

### Invariants Maintained
1. **Schema Parity**:
   - `drafts`: stores session state, language, turn attempts, active prompt, and transcript JSON.
   - `fields`: stores field key, raw span, canonical value, verification status, and parse reasons.
   - `audit_events`: chronological append-only audit trail.
   - `committed_records`: final records keyed by cryptographic `record_id` and unique `idempotency_key`.
2. **Commit Idempotency**:
   Both backends enforce `idempotency_key` uniqueness at the database level. Replay requests return `False` and preserve previous commits without duplication.
3. **Optimistic Locking**:
   Version checks (`expected_version == draft.version`) prevent race conditions between simultaneous updates.

---

## 4. Security Verification (Phase 5)

### CORS & Preflight Controls
FastAPI is configured with `CORSMiddleware`:
- Allowed origins: `https://krishujeniya.github.io`, localhost variations (`127.0.0.1:8000`, `localhost:8000`, `localhost:5500`, etc.), and configurable `CORS_ORIGINS`.
- Origin regex: `r"^https://([a-zA-Z0-9-]+\.)*github\.io$"` (allows user forks and PR preview deployments).
- Preflight: `OPTIONS` requests return `Access-Control-Allow-Origin`, `Access-Control-Allow-Methods`, and `Access-Control-Max-Age: 86400`.

### Sensitive Data & Cache Control
- All responses matching `/api/*` send:
  ```http
  Cache-Control: no-store, no-cache, must-revalidate, max-age=0
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: strict-origin-when-cross-origin
  ```
- Upload endpoints (`/api/drafts/{id}/audio` and `/api/drafts/{id}/clarify`) enforce `MAX_UPLOAD_BYTES` (default 10MB) and return HTTP 413 if exceeded.

### Secret Isolation
- The static frontend bundle contains zero API keys, database credentials, or server secrets.
- `scripts/build_frontend.py` actively validates client bundles and will abort the build if any secret patterns or backend `.py`/`.db` files are detected.

---

## 5. Test Evidence

### 1. Automated Test Suite (Pytest)
```
============================= test session starts ==============================
collected 77 items

tests/integration/test_app.py ..................                         [ 23%]
tests/integration/test_gnani_client.py .....                             [ 29%]
tests/unit/test_audio.py .........                                       [ 41%]
tests/unit/test_contracts.py ....                                        [ 46%]
tests/unit/test_parser.py ....................                           [ 72%]
tests/unit/test_policy.py ........                                       [ 83%]
tests/unit/test_state.py .......                                         [ 92%]
tests/unit/test_storage.py ......                                        [100%]

============================== 77 passed in 2.74s ==============================
```

### 2. Browser E2E Suite (Playwright)
Real headless Chromium execution via `scripts/qa_site.py`:
- **Viewport Responsiveness**: Tested across 320px, 360px, 390px, 768px, 1024px, 1280px, 1440px, and 1920px widths with 0 horizontal overflow.
- **Workflow Journey**: Voice dictation sample parsing -> selective clarification -> form commit -> registry listing -> CSV and JSON downloads.
- **Accessibility & Keyboard**: Full keyboard control on workspace tabs, workflow stages, and FAQ disclosure accordions.
- **Error Recovery**: Microphone permission denial and backend 503 errors trigger polite, visible, non-blocking feedback.
- **Zero Page Errors**: 0 unhandled JavaScript exceptions.

---

## 6. Live Speech Verification Status

- **Synthetic & Fixture Testing**: 100% passed using deterministic Indic audio files and simulated transcripts.
- **Live Provider Testing**: Live calls to Gnani Prisma STT and Timbre TTS require runtime injection of `GNANI_API_KEY` into the Vercel project environment variables. Live credentials must not be committed to the public Git repository.
