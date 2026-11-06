# Sureword

> **Voice-to-Form Frontline Visit Entry with Selective Clarification**  
> Built for the Great Indian AI Internship Challenge 2026.  
> Real speech-to-text via **Gnani Prisma** and spoken clarification via **Gnani Timbre**.

---

## 1. Overview & Problem

In Indian frontline healthcare workflows (such as ASHA household survey visits and ANM tablet entry), workers collect critical structured information under noisy conditions and time pressure. Standard automated speech recognition (ASR) outputs often look fluent while silently transcribing critical fields incorrectly—such as patient name, age, village, or visit date.

**Sureword** introduces a selective clarification reliability layer:
1. Dictation of visit details in conversational Hindi-English code-mix.
2. Transcription via **Gnani Prisma**.
3. Deterministic parsing and physiological/format validation into four core fields (`person_name`, `age`, `village`, `visit_date`).
4. Risk ranking: evaluating missingness, parse ambiguity, out-of-range bounds, and dictionary conflicts.
5. Focused spoken clarification via **Gnani Timbre**: asking the user to repeat *only* the single most uncertain field within a fixed clarification budget, rather than re-dictating the whole form.
6. Explicit human review and idempotent local commit before saving.

---

## 2. Production Repository Structure

This repository follows production-grade FAANG/Tier-1 engineering standards, using the modern PyPA `src-layout`, PEP 561 inline typing, and segregated documentation hierarchies:

```text
.
├── Makefile                      # Developer operations & CI parity automation
├── pyproject.toml                # Build configuration, dependency specs & tool configs
├── Dockerfile                    # Production container image definition
├── docker-compose.yml            # Local orchestration
├── .dockerignore                 # Container build exclusion rules
├── .editorconfig                 # Cross-IDE code style enforcement
├── .gitignore                    # Version control ignore rules
├── .env.example                  # Environment configuration template
├── LICENSE                       # MIT License
├── README.md                     # Project overview and entrypoint
│
├── .github/
│   └── workflows/
│       └── ci.yml                # Automated CI pipeline (lint, typecheck, test, benchmark)
│
├── configs/                      # Runtime policies and experiment configurations
│   ├── experiment.json           # Evaluation hyperparameters & policy ablation specs
│   ├── policy.json               # Risk thresholds & uncertainty penalty weights
│   └── schema.json               # Canonical entity definitions & validation boundaries
│
├── data/                         # Evaluation manifests and datasets
│   └── manifests/
│       ├── dev.jsonl             # 8-sample development calibration set
│       └── test.jsonl            # 8-sample frozen held-out evaluation set
│
├── docs/                         # Structured technical documentation
│   ├── README.md                 # Documentation catalog and navigation map
│   ├── architecture/
│   │   └── SYSTEM_DESIGN.md      # Architecture diagrams, state machines, and contracts
│   ├── specifications/
│   │   ├── SUBMISSION_PACK.md    # Contest submission answers & interview defense
│   │   └── WORKFLOW_VALIDATION.md# ASHA/ANM operational guidelines & usability trial protocol
│   ├── research/
│   │   ├── CONTEST_BRIEF.md      # Governing challenge specifications & operational boundaries
│   │   ├── RESEARCH_DOSSIER_PRIOR_ART.md # Prior art analysis & Indian frontline speech context
│   │   ├── RESEARCH_DOSSIER_SYSTEMS.md   # Systems-level research formulation & hypotheses
│   │   └── Gnani_AI_Challenge_Research_Dossier.pdf # Original 63-page research dossier
│   └── planning/
│       └── TRACKER.md            # Execution tracker, task milestones, and evidence ledger
│
├── src/                          # Application source code (PyPA src-layout)
│   └── sureword/
│       ├── py.typed              # PEP 561 inline type indicator
│       ├── __init__.py           # Package initialization
│       ├── app.py                # FastAPI endpoints, lifespan, and static mounting
│       ├── audio.py              # Audio normalization (16kHz mono WAV) & duration guards
│       ├── contracts.py          # Pydantic v2 domain schemas, FieldValue, & Transcript
│       ├── parser.py             # Deterministic Hindi-English entity parser & normalizer
│       ├── policy.py             # Uncertainty ranking engine (Policies B0, B1, B2, B3, P)
│       ├── state.py              # Finite state machine (EMPTY -> COMMITTED)
│       ├── storage.py            # Async SQLite transactional storage (aiosqlite)
│       ├── providers/
│       │   └── gnani.py          # Gnani Prisma STT and Timbre TTS provider adapter
│       └── static/
│           ├── index.html        # Accessible frontline web interface
│           ├── styles.css        # Responsive styling
│           └── app.js            # Client-side state machine and audio recorder
│
├── tests/                        # Comprehensive test suite (pytest)
│   ├── conftest.py               # Shared pytest fixtures and configuration
│   ├── unit/                     # Unit test suite
│   │   ├── test_audio.py         # Audio converter and validation tests
│   │   ├── test_contracts.py     # Schema boundary and constraint tests
│   │   ├── test_parser.py        # Entity extraction and numeral parsing tests
│   │   ├── test_policy.py        # Uncertainty ranking and policy selection tests
│   │   └── test_state.py         # State machine lifecycle and transition tests
│   └── integration/              # Integration test suite
│       ├── test_app.py           # FastAPI endpoint integration tests
│       └── test_gnani_client.py  # Gnani API provider adapter & fallback tests
│
├── scripts/                      # Operational automation & benchmarking tools
│   ├── capture_demo_walkthrough.py # Playwright automated visual walkthrough capture
│   ├── demo_runner.py            # Local CLI demo runner
│   ├── evaluate.py               # Benchmark evaluation engine across 5 policies
│   ├── generate_charts.py        # Evaluation visualization generator (matplotlib)
│   ├── smoke_gnani.py            # Live/offline Gnani API probe
│   ├── validate_manifest.py      # Split leakage & schema integrity validator
│   └── verify_deployment.py      # Deployment health & capability verification
│
└── artifacts/                    # Frozen evaluation artifacts & demonstration media
    ├── demo/                     # UI walkthrough screenshots and preview HTML
    ├── evaluation/               # Policy comparison figures and benchmark results JSON
    └── smoke/                    # Audio smoke probe outputs
```

---

## 3. Quickstart

### Prerequisites
- Python 3.11+
- `ffmpeg` installed on system path
- `uv` package manager (recommended) or standard `pip`

### Developer Setup

```bash
# Clone and enter directory
git clone https://github.com/krishujeniya/Sureword.git
cd Sureword

# Quick setup with Makefile (creates venv and installs all dependencies)
make install

# Configure environment
cp .env.example .env
# Edit .env and supply your GNANI_API_KEY if testing live API calls
```

### Run the Application

```bash
# Using Makefile
make dev

# Or directly with Uvicorn
uv run python -m uvicorn sureword.app:app --host 127.0.0.1 --port 8000 --reload
```

Open `http://127.0.0.1:8000` in your web browser.

---

## 4. Verification & Testing

Sureword adheres to strict verification discipline:

```bash
# Run unit and integration tests
make test

# Static analysis and linting (Ruff)
make lint

# Strict static type analysis (Mypy)
make typecheck

# Validate dataset manifest integrity
make validate

# Run deterministic benchmark evaluation
make evaluate
```

---

## 5. Research Protocol & Hypotheses

- **Primary Research Question:** At an equal clarification budget (maximum 1 prompt per form), does selective uncertainty-ranked clarification reduce accepted critical-field errors compared to simple sequential verification?
- **Baselines Evaluated:**
  - `B0`: Raw Prisma transcript without verification.
  - `B1`: Schema violations first, then fixed alphabetical field order.
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

## Site and workspace

The FastAPI app now serves a light, blue/navy product introduction and the working visit workspace at `/`. Use **Open workspace** or `/#workspace` to start; `/docs` and `/redoc` remain generated API documentation. The page includes a labeled SVG/Canvas illustration, optional particle motion, a keyboard-operable Speak / Clarify / Review explanation, and a native FAQ. No frontend bundler or Node production runtime is required.

Use **fictional details only**. Sample chips supply simulated transcripts, and **Use fictional sample answer** resolves a sample question through the real clarification API. Recording and spoken prompts require browser permissions and configured speech infrastructure. Prompts play only after an explicit request. Saved demo records are unauthenticated; the app page is deliberately `noindex`. Vercel's `/tmp` SQLite is ephemeral, not durable storage.

Design and content: [design system and 93-effect audit](docs/DESIGN_SYSTEM.md), [product inventory](docs/PRODUCT_INVENTORY.md), [QA results and remaining limits](docs/QA_REPORT.md). Current local captures: `artifacts/design-qa/`.

```bash
# Build the Python source distribution and wheel, including static assets
uv build
# Existing checks
make lint
make typecheck
make test
# Optional local browser QA: install Playwright in the dev environment first
uv pip install playwright
.venv/bin/python scripts/qa_site.py
```

Browser QA expects an isolated fixture server on port 8000 and Chrome at `/opt/google/chrome/chrome`; it saves fictional records to that server. Run the server with `GNANI_API_KEY=` and a disposable `DATABASE_PATH` to avoid provider calls and existing records. The Playwright package is optional tooling, not a production dependency.

Deployment: use the existing Dockerfile/Compose on a Python runtime with ffmpeg, or the existing `vercel.json` Python adapter. Install the project requirements, configure server-only Gnani credentials for authorized live testing, and supply durable storage/authentication before any real-data deployment. No push or deployment was performed for this redesign. Follow local QA before an explicitly approved deployment; do not infer deployment acceptance from the wheel build.
