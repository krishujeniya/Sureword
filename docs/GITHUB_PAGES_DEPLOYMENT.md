# GitHub Pages Frontend Deployment Guide

Sureword runs as a fully decoupled web application:
- **Frontend**: Static single-page application hosted on **GitHub Pages** (`https://krishujeniya.github.io/Sureword/`).
- **Backend**: Serverless FastAPI application with Gnani Prisma and Timbre provider integrations hosted on **Vercel** (`https://sureword.vercel.app/`).
- **Database**: Dual-engine persistence layer supporting local SQLite and managed PostgreSQL (e.g., Neon serverless Postgres).

---

## 1. Architecture Overview

```
Browser Client (https://krishujeniya.github.io/Sureword/)
       │
       ├─────────────────────────────────┐
       ▼                                 ▼
Static Asset Requests             Cross-Origin API Requests
(HTML, CSS, JS, SVG)             (HTTPS with CORS & Security Headers)
       │                                 │
       ▼                                 ▼
GitHub Pages CDN                 Vercel Serverless Gateway
(Fast Edge Cache)                (https://sureword.vercel.app)
                                         │
                                         ├─────────────────────────┐
                                         ▼                         ▼
                                   FastAPI Engine           Gnani Speech APIs
                                 (Prisma STT / Timbre TTS)  (Server-to-Server)
                                         │
                                         ▼
                             Persistent Storage (PostgreSQL)
                             or Local / Ephemeral SQLite
```

---

## 2. Base Path Resolution

GitHub Pages serves repository projects under the repository subpath `/Sureword/`.

### Asset Paths
All asset links in `index.html` use relative paths:
- Stylesheets: `./styles.css`, `./design.css`
- JavaScript: `./app.js`, `./experience.js`
- Favicon & Icons: `./favicon.svg`, `./logo.svg`

The build tool `scripts/build_frontend.py` enforces this invariant:
- Rewrites any root-relative `/static/` references to relative paths (`./`).
- Generates a `.nojekyll` file to prevent GitHub Pages from discarding files starting with special characters.
- Sets `<base href="/Sureword/">` and updates canonical and OpenGraph URLs to `https://krishujeniya.github.io/Sureword/`.

---

## 3. Centralized API Configuration

The frontend client in `src/sureword/static/app.js` resolves the backend API target using the following resolution chain:

1. **URL Query Parameter Override**:  
   `?api_base=https://staging.sureword.app` (ideal for testing pull requests or local tunnels).
2. **Local Storage Override**:  
   `localStorage.setItem("sureword_api_base", "http://127.0.0.1:8000")`.
3. **Injected Global Configuration**:  
   `window.SUREWORD_CONFIG.apiBaseUrl` set in `index.html`.
4. **Domain Auto-Detection**:  
   When hosted on `krishujeniya.github.io` or any `*.github.io` domain, defaults to `"https://sureword.vercel.app"`.
5. **Same-Origin Fallback**:  
   When hosted directly on Vercel or locally via uvicorn, uses `""` (relative paths) so all existing functionality remains intact.

All network operations route through `apiFetch()`, which adds:
- Request timeout protection (30s default with `AbortController`).
- Centralized URL construction.
- Zero client-side API key exposure (Gnani credentials remain strictly server-side).

---

## 4. Frontend Build & Distribution

The standalone static distribution is prepared via:

```bash
python scripts/build_frontend.py --source src/sureword/static --output dist-static --api-base https://sureword.vercel.app --base-href /Sureword/
```

### Pre-Deployment Verification
```bash
python scripts/build_frontend.py --output dist-static --check-only
```

The build validator checks:
1. Presence of all 7 core static assets (`index.html`, `styles.css`, `design.css`, `app.js`, `experience.js`, `logo.svg`, `favicon.svg`).
2. Absence of backend source code (`.py`, `.pyc`), databases (`.db`, `.sqlite`), or secrets (`.env*`).
3. Complete substitution of root-relative paths (`/static/` -> `./`).
4. Absence of hardcoded private keys or `GNANI_API_KEY`.

---

## 5. GitHub Actions Automated Deployment

Workflow file: `.github/workflows/deploy-frontend.yml`

### Trigger Conditions
- Push to `main` branch when changes touch `src/sureword/static/**`, `scripts/build_frontend.py`, or the workflow file itself.
- Manual trigger via GitHub Actions `workflow_dispatch`.

### Pipeline Execution Steps
1. **Checkout**: Retrieves repository source.
2. **Setup**: Configures Python 3.11 environment.
3. **Syntax Validation**: Runs `node --check` against `app.js` and `experience.js`.
4. **Build**: Executes `scripts/build_frontend.py` targeting `dist-static`.
5. **Security & Path Audit**: Runs validator with zero-tolerance checks.
6. **Artifact Generation**: Packs `dist-static` using `actions/upload-pages-artifact@v3`.
7. **Deployment**: Deploys to GitHub Pages via `actions/deploy-pages@v4`.

---

## 6. Local Testing of Decoupled Setup

To run and test the frontend and backend independently on your local machine:

### Terminal 1: Run Backend API
```bash
.venv/bin/python -m uvicorn sureword.app:app --host 127.0.0.1 --port 8000
```

### Terminal 2: Run Static Frontend on a Different Port (Cross-Origin)
```bash
python3 scripts/build_frontend.py --output dist-static --api-base http://127.0.0.1:8000
python3 -m http.server 5500 --directory dist-static
```

Open `http://localhost:5500/` in your browser. All API calls, speech presets, clarification flows, and records will execute across origins to `http://127.0.0.1:8000/` with verified CORS preflights.
