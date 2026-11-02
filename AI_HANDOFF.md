# AI Handoff — Sureword (Great Indian AI Internship Challenge 2026)

> **Last Updated:** 2026-11-02 20:49 IST  
> **Branch:** `main`  
> **Status:** 10/10 (100%) Production Standard with Full 11-Language Gnani.ai API Support (Prisma STT & Timbre TTS), ADR-0006 Pure Voice-Recognized Submission, Clinical Field Expansion (Gender & Symptoms), Suffix Village & Honorific Parsing, and 70/70 tests passing (93% coverage).

---

## 1. Current State & Verification Summary

- **Production Deployment:** Verified live on Vercel Serverless (`https://sureword.vercel.app`, 8/8 deployment smoke steps passed) with full multi-lingual capability across all 11 Indian & regional languages supported by the Gnani.ai API:
  1. `hi-IN` — Hindi (हिन्दी)
  2. `en-IN` — Indian English (English)
  3. `mr-IN` — Marathi (मराठी)
  4. `bn-IN` — Bengali (বাংলা)
  5. `gu-IN` — Gujarati (ગુજરાતી)
  6. `pa-IN` — Punjabi (ਪੰਜਾਬੀ)
  7. `ta-IN` — Tamil (தமிழ்)
  8. `te-IN` — Telugu (తెలుగు)
  9. `kn-IN` — Kannada (ಕನ್ನಡ)
  10. `ml-IN` — Malayalam (മലയാളം)
  11. `or-IN` — Odia (ଓଡ଼ିଆ)
- **ADR-0006: Pure Voice-Recognized Submission & Clinical Field Expansion:**
  - **Voice-Only Recognized Submission:** Removed manual typing input boxes from the form fields (`readonly input-readonly-voice`) and removed manual text inputs from the clarification banner. The user records or selects a sample, reviews the recognized values, and submits verified records with zero keyboard typing friction.
  - **Clinical Field Expansion:** Added optional voice-recognized fields for **Gender** (`gender`: Female / Male / Other) and **Chief Complaints / Symptoms** (`symptoms`: Fever, Cough, Cold, Headache, Body Pain, Diarrhea, Weakness) across all 11 languages.
  - **Deterministic Accuracy Upgrades:** Suffix village detection (`रामपुर गाँव`, `Rampur village`), expanded honorific cleaning (`श्रीमती`, `श्री`, `सुश्री`, `डॉ.`), multi-lingual symptom matching, and zero-risk exemption for optional fields in Policy P.
  - **Encounter Summary & Registry:** Extended 6-column encounter summary card and registry table with Gender, Symptoms, CSV export, and localized column headers.
- **Test & Quality Gates (`verification-loop`):**
  - `pytest tests/`: **70 passed** in 7.55s, **93% total coverage** (100% on `parser.py`, `contracts.py`, `languages.py`, `policy.py`).
  - `ruff check src tests scripts api`: All checks passed (0 errors, 0 warnings).
  - `ruff format --check src tests scripts api`: 27 files verified and formatted.
  - `mypy src tests api`: 0 issues found across 20 files.

---

## 2. Changed Files

- `docs/adr/0006-voice-only-recognized-submission-and-clinical-field-expansion.md` (**new**): Architectural decision record for voice-only submission and clinical field expansion.
- `docs/adr/README.md`: Index updated with ADR-0006.
- `src/sureword/contracts.py`: Added `GENDER` and `SYMPTOMS` to `FieldKey`.
- `src/sureword/parser.py`: Added `parse_gender()`, `parse_symptoms()`, suffix village marker extraction, and 6-field `parse_visit_form()`.
- `src/sureword/policy.py`: Added `GENDER` and `SYMPTOMS` prompt templates; exempt optional fields from clarification budget ($Risk = 0.0$).
- `src/sureword/static/index.html`: Non-editable voice-captured inputs, added Gender and Symptoms fields, pure voice clarification action, and 9-column registry table.
- `src/sureword/static/styles.css`: 6-column responsive encounter summary, `.input-readonly-voice`, and `.opt-tag` styles.
- `src/sureword/static/app.js`: 11-language I18N for gender/symptoms, non-editable voice-only submission wiring, 6-field encounter summary, and CSV export.
- `tests/unit/test_parser.py`: Added unit tests for `parse_gender`, `parse_symptoms`, suffix village markers, and clinical expansion.

---

## 3. Pending Steps to Win & Submit (Before Nov 10, 2026)

1. **Step 1: Record 60-Second Video Demo (T19)**
   - Run the rehearsal helper: `uv run python scripts/demo_runner.py`
   - Capture screen + microphone demonstrating voice-to-form and multi-lingual switching (e.g. Hindi, English, Tamil).
2. **Step 2: Publish Public Video Post (T21)**
   - Post to LinkedIn or X with both required hashtags: `#GnaniAI` `#GreatIndianAIInternshipChallenge`.
   - Copy LinkedIn/X text draft directly from `docs/specifications/SUBMISSION_PACK.md`.
3. **Step 3: Submit Official Nomination Form (T21)**
   - Fill out [Gnani Challenge Submission Form](https://www.gnani.ai/great-indian-ai-internship-registration-form).
   - Use pre-drafted technical answers from `docs/specifications/SUBMISSION_PACK.md`.
4. **Step 4: Technical Defense Preparation (T22)**
   - Rehearse the 14-question defense pack in `docs/specifications/SUBMISSION_PACK.md`.

---

## 4. Exact Next Command

To launch the local demo server:
```bash
uv run python -m uvicorn sureword.app:app --host 127.0.0.1 --port 8000 --reload
```
