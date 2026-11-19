# Sureword handoff

Updated 2026-11-19. Branch: main. Delivery: Clinical Vitals Expansion (Blood Pressure, Blood Glucose, Pregnancy Trimester) + Dictation Audio Review Playback, Offline-First PWA, and CI/CD Automation.

Task: Implement clinical NCD screening vitals and dictation audio playback:
- Extended contracts with `blood_pressure`, `blood_glucose`, and `pregnancy_trimester` in `src/sureword/contracts.py`.
- Deterministic extraction and physiological boundary validation in `src/sureword/parser.py`:
  - Blood Pressure: systolic (60–260) / diastolic (40–150), systolic > diastolic, NHM/WHO stage categorization.
  - Blood Glucose: fasting, random, post-prandial context detection and 30–600 mg/dL physiological limits.
  - Pregnancy Trimester: extraction of trimesters 1, 2, and 3 from ordinal and gestational month mentions.
- Risk ranking and prompt synthesis in `src/sureword/policy.py`: optional clinical fields remain risk 0.0 unless contradictory (NEEDS_REPEAT triggers risk 0.85).
- Frontline UI in `index.html` and `styles.css`: dedicated vitals fields with status tags, in-browser dictation audio review player (`#dictation-audio-player`).
- Saved registry in `app.js`: table headers, rows, and CSV/JSON exports include BP and Glucose data.
- Unit and integration tests in `tests/unit/test_contracts.py`, `tests/unit/test_parser.py`, `tests/unit/test_policy.py`, and `tests/integration/test_app.py`.

Changed/added source:
- `src/sureword/contracts.py` (added clinical field keys)
- `src/sureword/parser.py` (added parse_blood_pressure, parse_blood_glucose, parse_pregnancy_trimester)
- `src/sureword/policy.py` (prompt templates and clinical risk rules)
- `src/sureword/static/index.html` (clinical inputs, audio player, registry headers)
- `src/sureword/static/styles.css` (audio player review styling)
- `src/sureword/static/app.js` (clinical keys, audio player binding, registry columns, CSV/JSON export)
- `tests/unit/test_contracts.py` (contract tests for clinical keys)
- `tests/unit/test_parser.py` (unit tests for BP, glucose, trimester parsing and bounds)
- `tests/unit/test_policy.py` (policy tests for clinical risk ranking)
- `tests/integration/test_app.py` (end-to-end integration lifecycle with clinical vitals)
- `scripts/evaluate.py` (scoped evaluation policies to critical benchmark keys)
- `.github/workflows/ci.yml` (optimized ffmpeg runner check to eliminate apt mirror latency)

Next local command:
```bash
git diff --check
```
