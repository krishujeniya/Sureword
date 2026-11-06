# Sureword site QA — 2026-11-06

## Result

Implemented locally and verified on Chrome/Linux. Python package builds and 71 tests pass. Browser fictional sample → targeted clarification → explicit save → registry → CSV/JSON export passed. Not deployed. Not approved for patient data. Performance goal remains unmet; see measurements below.

## Executed checks

| Check | Actual result / evidence |
| --- | --- |
| Production package | `uv build`: wheel and source distribution built; ZIP inspection confirms all seven static files included |
| Python lint | `ruff check src tests scripts api`: pass |
| Python format | `ruff format --check src tests scripts api`: 28 files passed |
| Types | `mypy src tests api`: no issues in 20 source files |
| JavaScript | `node --check` for app.js and experience.js: pass; no new JS type checker configured |
| Tests | `GNANI_API_KEY= ALLOW_FIXTURE_FALLBACK=true .venv/bin/pytest tests -q`: 71 passed in 6.86s |
| Regression history | Initial suite: 69 passed / 1 failed, reproducible ffmpeg startup timeout. New canonical PCM regression failed before fix. Exact normalized PCM now validates without transcoding; final 71 pass. ADR 0007 records tradeoff. |
| Responsive | Full-page screenshots at 320/360/390/768/1024/1280/1440/1920px; no horizontal page overflow. Desktop and mobile reviewed alongside browser reference captures. |
| Keyboard | Workspace ArrowLeft/Right; stage arrows/Home/End; FAQ Enter; focus-visible styles. Browser checks pass. |
| Reduced motion | Live emulation disables continuous motion and pause control; stage switching remains usable; no delayed hidden text. `reduced-motion.png` |
| No JavaScript | Hero and all three workflow chapters remain visible; noscript explains app requirement |
| Slow network | CDP: 400ms latency, 50KB/s download, 20KB/s upload; hero readable at DOM ready; `slow-network.png` |
| Autoplay blocked | Browser launched with user-gesture-required autoplay policy; sample flow requests no speech audio, player remains paused without source |
| Media failures | Aborted logo request leaves hero readable; deliberately invalid local SVG returns 404. No product video exists; video buffering/failure controls not applicable. |
| Content states | Empty fields, partial sample plus real clarification, actual committed confirmation, injected 503 error; permission failure tested using mocked getUserMedia NotAllowedError. |
| Exports | Real browser download events produce CSV and JSON filenames; fictional test database only |
| Anchors/routes | Every internal hash target exists. `/docs`, `/redoc`, `/openapi.json`, `/healthz`, `/api/languages`: HTTP 200. Existing draft/clarify/commit/registry endpoints exercised. |
| Console/network | No uncaught page errors. One deliberate 503 in main browser run; intentionally invalid/aborted assets separately. No unexpected failed page resource observed. |
| Short/zoom | 768×360 landscape and 200% root font-size probe: no page overflow. This is a text-size probe, not a full browser zoom or real-device test. |
| Evidence gate | Skill `check-evidence.js artifacts/design-qa/evidence.json`: complete; visual correctness separately reviewed |
| Diff | `git diff --check`: pass; reviewed runtime/static diffs, no endpoint contract changes |

## Performance measurements

Lighthouse 13.6.0, local HTTP FastAPI, headless Chrome, default mobile simulated throttling, one latest lab run. `artifacts/design-qa/lighthouse-final.json` is authoritative.

| Category / metric | Measured |
| --- | --- |
| Performance | 83 |
| Accessibility | 100 |
| Best practices | 100 |
| SEO | 63 |
| LCP | 1.2 s |
| CLS | 0 |
| Total blocking time | 670 ms |

Earlier runs measured 71 then 62 performance under shared-host load; they are not represented as passes. Final target 90+ performance is **not met**. Lighthouse SEO flags deliberate `noindex` on the combined public introduction and unauthenticated app/registry. Security/visibility priority takes precedence over SEO scoring. No sitemap submitted for this app. A separate public landing route and private authenticated workspace would be needed before making this an indexable production product.

Browser requestAnimationFrame cadence sampled near 60fps for one second on this desktop; this is not a real-device particle performance guarantee. Field INP and 75th-percentile Core Web Vitals: **not run**, no field traffic or instrumentation. Deployment waterfall, mobile hardware, memory soak, high-refresh display testing: **not run**.

## Coverage and limitations

Section 18.1/18.5: **20 built, 73 skipped, 93 total**, each row in DESIGN_SYSTEM.md. Section 18.2 styles, 18.3 states, and 18.4 reduced-motion decisions are documented there. Single-product app: no product explorer/carousel/detail routes, fake pricing, newsletter, docs content ingestion, custom cursor, or autoplay video. These are explicit skips, not stub controls.

Full screen-reader speech, all eight widths at 200% real browser zoom, long translated copy at every width, Safari/Firefox/iOS/Android, all live microphone/audio/provider controls, no-sound permission, blocked-play rejection with actual synthesized audio, and physical-device performance: **not run**. Eleven workspace languages are preserved; the overview remains English. Native audio controls exist for explicit speech playback, but live TTS was not requested. No paid calls authorized or made by site QA.

Pre-push Gitleaks 8.30.1 staged-diff scan: **passed**, no leaks found (redacted output; official release checksum verified). No repository Gitleaks command was configured; this scan was run separately. Targeted changed-code review found no credential values introduced; environment files were not bundled or read into the frontend. No authentication was added: demo API and registry remain accessible, so fictional data only. Existing deployments are not current evidence for this change. External repository URL derives from README; an exhaustive external HTTP-link audit was not run.

## Files and deployment

Changed: README, AI_HANDOFF, audio.py, app.js, index.html, test_audio.py, ADR index. Added: design.css, experience.js, scripts/qa_site.py, DESIGN_SYSTEM.md, PRODUCT_INVENTORY.md, QA_REPORT.md, ADR 0007, local screenshots/JSON evidence in artifacts/design-qa.

Routes retained: `/` with `#overview`, `#workspace`, `#workflow`, `#questions`; existing FastAPI API/docs/static routes. No product route fabricated. No push, deployment, publication, or live-customer action performed.

Run `make dev` for local review. Existing Docker/Compose runtime requires ffmpeg; Vercel uses the existing Python adapter and temporary SQLite. Before an approved deployment, supply server-only credentials if live speech is intended, test actual browser audio on that runtime, and add durable storage and access control for any real-data scope. Package build does not verify those external requirements.
