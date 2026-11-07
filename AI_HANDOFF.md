# Sureword handoff

Updated 2026-11-07. Branch: main. Delivery: Decoupled production architecture with GitHub Pages frontend (`https://krishujeniya.github.io/Sureword/`), Vercel FastAPI backend (`https://sureword.vercel.app/`), and persistent PostgreSQL database support.

Task: Migrate Sureword into a fully decoupled production architecture without breaking existing Vercel deployment:
- Static frontend extracted and validated for GitHub Pages hosting under base path `/Sureword/`.
- Relative asset paths configured for `./styles.css`, `./design.css`, `./app.js`, `./experience.js`, `./logo.svg`, `./favicon.svg`.
- Centralized `API_CONFIG` and `apiFetch()` with timeout support, domain detection (`*.github.io`), and configurable backend URL.
- FastAPI backend configured with `CORSMiddleware` (allowing `https://krishujeniya.github.io` and regex for GitHub Pages), security headers, preflight cache, and cache-control `no-store` for sensitive visit records.
- Hybrid persistent storage engine: SQLite for local development and PostgreSQL (`asyncpg`) for serverless cloud execution via `DATABASE_URL`.
- GitHub Actions workflow `.github/workflows/deploy-frontend.yml` configured for automated Pages deployments.
- Build and validation pipeline `scripts/build_frontend.py` with secret prevention and asset path checks.

Changed/added source:
- `src/sureword/static/index.html` (relative asset paths, runtime configuration script, metadata)
- `src/sureword/static/app.js` (centralized `API_CONFIG`, `apiFetch` with timeout and auto-detection)
- `src/sureword/app.py` (CORS middleware, security headers, upload limit validation, root asset routes)
- `src/sureword/storage.py` (dual-engine PostgreSQL `PostgresStorage` via `asyncpg` + `SQLiteStorage`)
- `src/sureword/audio.py` (timeout exception safety)
- `pyproject.toml` & `requirements.txt` (added `asyncpg`)
- `.env.example` (documented `DATABASE_URL`, `CORS_ORIGINS`)
- `scripts/build_frontend.py` (standalone frontend builder and security validator)
- `.github/workflows/deploy-frontend.yml` (automated GitHub Pages deployment workflow)
- `docs/GITHUB_PAGES_DEPLOYMENT.md` (deployment and local testing guide)
- `docs/MIGRATION_VERIFICATION.md` (audit, architecture, and verification report)
- `tests/unit/test_storage.py` & `tests/integration/test_app.py` (added storage and CORS integration tests)

Checks run:
- Pytest: 77 tests pass (increased from 71).
- Ruff check and format: all checks pass.
- Mypy: 0 errors in 10 source files.
- Node JS syntax check: `app.js` and `experience.js` both pass cleanly.
- Static build validator: `scripts/build_frontend.py --check-only` passes with 0 errors.
- Playwright E2E browser tests: `scripts/qa_site.py` passes 100% across all 8 viewport widths, user workflows, and error states.

Next local command:
```bash
.venv/bin/python -m uvicorn sureword.app:app --host 127.0.0.1 --port 8000
```
