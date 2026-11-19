# Sureword handoff

Updated 2026-11-19. Branch: main. Delivery: Offline-First PWA Architecture with ServiceWorker caching, client-side IndexedDB persistence, background sync queue, backend `/health` endpoint parity, and automated GitHub Pages deployment.

Task: Implement offline-first frontline healthcare resilience for Sureword:
- Service Worker (`src/sureword/static/sw.js`) pre-caches shell assets (`index.html`, `styles.css`, `design.css`, `app.js`, `experience.js`, `logo.svg`, `favicon.svg`, `manifest.json`) for instant boot without network.
- Web App Manifest (`src/sureword/static/manifest.json`) configured with standalone display and monochrome 3D health branding.
- IndexedDB database engine `SurewordDB` in `app.js` storing offline drafts, audio upload intents, and committed records.
- Synchronization engine replaying pending offline commits and audio uploads when back online, with manual sync trigger in the registry.
- Accessible offline banner with ARIA live region notifying frontline workers of local storage mode.
- FastAPI backend `/health` route alias in `app.py` matching container orchestrator health checks in `DEPLOYMENT.md`.
- `scripts/build_frontend.py` updated to validate `manifest.json` and `sw.js` in static distribution.
- `.github/workflows/deploy-frontend.yml` updated with `node --check src/sureword/static/sw.js`.
- Integration tests in `tests/integration/test_app.py` verifying `/health` and `/healthz` endpoints.

Changed/added source:
- `src/sureword/static/sw.js` (Service Worker cache-first static shell and network-first API handling)
- `src/sureword/static/manifest.json` (PWA web application manifest)
- `src/sureword/static/app.js` (SurewordDB IndexedDB engine, network listeners, offline draft/commit flow, sync queue)
- `src/sureword/static/index.html` (manifest link, offline notification banner, registry sync button)
- `src/sureword/static/styles.css` (offline banner styles and accessible status badges)
- `src/sureword/app.py` (added `/health` route alias and static asset MIME types for manifest/sw)
- `scripts/build_frontend.py` (added manifest.json and sw.js to required build distribution)
- `.github/workflows/deploy-frontend.yml` (added syntax verification for sw.js)
- `tests/integration/test_app.py` (tests for `/health` GET and HEAD responses)

Next local command:
```bash
git diff --check
```
