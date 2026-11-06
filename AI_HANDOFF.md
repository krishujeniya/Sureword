# Sureword handoff

Updated 2026-11-06. Branch: main. Base revision: 65fec83. Delivery: user authorized a GitHub push of this implementation. This handoff accompanies the implementation commit; use `git log -1` to identify its final revision. No deployment verification is implied.

Task: build original site around existing FastAPI voice-to-form app. Light blue/navy identity, particle-led conceptual hero, real workspace, stage selector and FAQ implemented. Preserve 11 localized workspace languages and voice-only entry; fictional sample answer uses existing clarification API. No invented pricing or clinical claims. Page is deliberately noindex because it includes the unauthenticated registry.

Changed/added source: static/index.html, static/app.js, static/design.css, static/experience.js; audio.py canonical PCM validation fast path; test_audio.py regression; scripts/qa_site.py. Docs: README, DESIGN_SYSTEM, PRODUCT_INVENTORY, QA_REPORT, ADR 0007 and index. Local evidence: artifacts/design-qa (fictional data only).

Checks run: uv build (wheel/static payload inspected); Ruff lint/format; Mypy; both JS syntax checks; 71 pytest tests pass. Browser: all eight widths no overflow, actual sample/clarification/save/registry/exports, keyboard stages/workspace/FAQ, reduced motion, no-JS, throttled network, permission/error recovery. Evidence schema checker passes. See QA_REPORT for real measured Lighthouse and explicit unrun checks.

Gaps: mobile Lighthouse performance below 90; intentional noindex lowers SEO; no real-device/assistive speech/live speech provider QA. Pre-push Gitleaks 8.30.1 staged-diff scan passed with redacted output; 71 tests passed again before commit. Unauthenticated prototype and ephemeral serverless SQLite remain unsuited to patient records. No paid calls or deployment verification performed. Prior handoff's production rating is historical and does not certify these edits.

Next local command:
```bash
.venv/bin/python -m uvicorn sureword.app:app --host 127.0.0.1 --port 8000
```

The current review server may already occupy port 8000. Browser automation requires an isolated fixture server (`GNANI_API_KEY=`, `ALLOW_FIXTURE_FALLBACK=true`, disposable DATABASE_PATH); it creates fictional records. Prior challenge submission/video publication steps remain outside this website task and were not performed.
