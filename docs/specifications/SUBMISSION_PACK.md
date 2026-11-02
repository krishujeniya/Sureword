# Sureword — Contest Submission, Demo, and Interview Pack

> **Great Indian AI Internship Challenge 2026**  
> **Project:** Sureword  
> **Author:** Krish Ujeniya  
> **Track:** Build Sovereign AI for India  
> **Primary Target Award:** The Real Deal

---

## 1. Official Nomination Form Draft Answers

### 1. Project Title
**Sureword: Selective Voice-to-Form Clarification for Frontline Healthcare Visit Entry**

### 2. One-Line Summary
A reliability layer for frontline visit dictation that pairs Gnani Prisma speech recognition with Gnani Timbre spoken clarification to identify and verify uncertain fields before saving.

### 3. Problem Statement & Indian Frontline Context
In Indian public healthcare workflows (e.g. ASHA household surveys and ANM digital tablet entry described in NHSRC/MoHFW operational guidelines), frontline workers capture structured visit records under noisy conditions and high workloads. 

Standard end-to-end ASR often outputs fluent Hindi-English sentences that mask critical field-level errors—such as a mistranscribed person name, an erroneous age, or an altered village. When workers are forced to repeat entire paragraphs, dictation fatigue sets in. Sureword introduces an active uncertainty layer: it transcribes dictation using Gnani Prisma, deterministically validates physiological bounds and schemas, ranks fields by estimated risk, and uses Gnani Timbre to ask the speaker to repeat *only* the single most uncertain field before committing the record locally.

### 4. Technical Architecture & Gnani Integration
- **Speech Recognition:** Integrates Gnani Prisma STT (`POST https://api.vachana.ai/stt/v3`) for conversational Hindi-English speech recognition.
- **Audio Processing:** Implements server-side FFmpeg pipeline converting browser WebM/OGG audio into standardized 16 kHz mono 16-bit PCM WAV with duration bounds (0.2s–20s) and SHA-256 fingerprinting.
- **Deterministic Field Parsing:** Zero hallucination parser extracting 4 core fields (`person_name`, `age`, `village`, `visit_date`). Handles Devanagari numerals (`०-९`), Hindi number words (1–100), English words, physiological age bounds (1–120), and ISO/calendar date validation (rejecting impossible dates like Feb 30).
- **Spoken Clarification:** Integrates Gnani Timbre TTS (`POST https://api.vachana.ai/api/v1/tts/inference`) to synthesize natural, focused prompts asking the user to repeat the uncertain field.
- **Audit Storage & State Machine:** SQLite transactions enforce strict lifecycle progression (`EMPTY → CAPTURING → TRANSCRIBING → DRAFT → NEEDS_CLARIFICATION → READY_FOR_REVIEW → COMMITTED`). Rejects stale version edits (HTTP 409) and prevents saving unreviewed or unresolved records.

### 5. Research Novelty & Prior Art Boundaries
- **Prior Art Distinction:** IndicContextEval benchmarked contextual ASR; DeRAGEC explored candidate denoising; RAS studied model abstention. Sureword studies an operational systems question: at a strictly equal clarification budget (maximum 1 repeat prompt per form), does selective risk-ranked verification reduce critical-field errors compared to schema-first or random selection?
- **Controlled Baselines:** Evaluated against B0 (raw ASR without prompts), B1 (schema errors first then alphabetical), B2 (seeded random selection), and B3 (unconstrained confirm-all upper bound).

### 6. Measured Benchmark Outcomes
Evaluated on frozen, speaker-disjoint test manifests (`data/manifests/test.jsonl`):
- **Raw ASR (B0):** 6.2% primary accepted-field error (2/32), 75.0% whole-record correctness (6/8), 0.0 prompts/form.
- **Random Selection (B2, Budget 1):** 6.2% primary accepted-field error (2/32), 75.0% whole-record correctness (6/8), 1.0 prompts/form.
- **Proposed Risk Policy (P, Budget 1):** 3.1% primary accepted-field error (1/32), 87.5% whole-record correctness (7/8), 1.0 prompts/form (50% relative error reduction over raw ASR and random selection).
- **Confirm-All (B3, Unconstrained):** 0.0% primary error (0/32), 100.0% correctness (8/8), 4.0 prompts/form.

### 7. Limitations & Ethical Disclosure
- Evaluated on role-play simulation data with fictional records; not approved for live medical diagnosis or hospital record filing.
- Current benchmarks are based on small developer cohorts; population-level generalization requires larger field testing.
- Offline fixture fallback was utilized during development when live credentials were being configured.

---

## 2. Public Social Media Drafts

### LinkedIn Post Draft
```text
I built Sureword, an open-source prototype designed to make voice-based frontline visit documentation in India more reliable.

Frontline workers often dictate household visit details in Hindi and English. While automated speech recognition works well on general phrases, critical fields like names, ages, and dates can get mistranscribed. Asking workers to repeat an entire dictation is frustrating and slow.

Sureword uses Gnani Prisma for speech-to-text and deterministic parsing to validate four core fields. When a field is ambiguous or out of bounds, the system uses Gnani Timbre to ask for only that specific field through spoken audio before saving.

In our controlled benchmark on held-out test recordings:
- Raw transcription had a 6.2% accepted-field error rate.
- At a fixed budget of one prompt per form, selective clarification reduced accepted-field error to 3.1% (a 50% relative error reduction).
- Random field clarification showed no improvement over raw speech.

This is an early prototype tested on fictional data, not a clinical deployment.

Live Demo & Code: https://sureword.vercel.app | https://github.com/krishujeniya/Sureword

#GnaniAI #GreatIndianAIInternshipChallenge #SovereignAI #SpeechAI #HealthTech
```

### X (Twitter) Post Draft
```text
Sureword turns Hindi-English voice into structured visit forms using Gnani Prisma STT + Timbre TTS.

Instead of re-dictating everything when audio is uncertain, it asks you to repeat only the single most uncertain field.

Demo & code: https://sureword.vercel.app | https://github.com/krishujeniya/Sureword

#GnaniAI #GreatIndianAIInternshipChallenge
```

---

## 3. Sixty-Second Demo Walkthrough Storyboard (T19)

| Time | Visual / Screen Action | Spoken Script / Audio |
|---|---|---|
| **0:00–0:08** | Open Sureword web interface. Show blank visit form (`person_name`, `age`, `village`, `visit_date`). | *"Frontline workers dictate household visits in Hindi-English, but a single mistranscribed name or age can quietly corrupt digital records."* |
| **0:08–0:18** | Click **Start Recording**. Speak: *"मरीज का नाम कमला देवी, उम्र 150 साल, गाँव रामपुर, 30 अक्टूबर 2026"* (intentional out-of-bounds age). | *"Let's dictate a visit with a physiological error: age 150 years."* |
| **0:18–0:32** | Click **Stop Recording**. Real-time transcript appears; fields populate. Name, Village, and Date show green; **Age** badge turns red (`Needs Repeat`). | *"Gnani Prisma transcribes the audio. Our deterministic parser flags that age 150 is out of valid bounds."* |
| **0:32–0:46** | Clarification banner appears. Timbre audio plays: *"कृपया मरीज़ की सही उम्र दोबारा बोलिए।"* Click **Speak This Field** and say *"पैंतालीस साल"* (45 years). Age updates to 45 (`Confirmed`). | *"Gnani Timbre speaks up to clarify only the uncertain field. We repeat just the age, and the record updates with full provenance."* |
| **0:46–0:54** | Form transitions to `READY_FOR_REVIEW`. Click **Verify & Commit Record**. Record ID `REC-20261031-XXXX` generated with clean JSON audit. | *"The record cannot commit until all fields are verified. Review is explicit, and save is idempotent."* |
| **0:54–1:00** | Flash comparative benchmark card (6.2% → 3.1% error at 1 prompt/form). Display GitHub repository URL. | *"Sureword: selective clarification for sovereign speech workflows. Code and benchmarks on GitHub."* |

---

## 4. Technical Defense Interview Preparation Guide (T22)

### Q1: Which workflow fact did you verify, and which user assumptions remain untested?
**Answer:** Verified that Ministry of Health (MoHFW/NHSRC) operational guidelines for NCDs explicitly mandate ASHA field documentation followed by digital tablet entry by ANMs, where high manual typing burden is an acknowledged friction point. Untested assumptions: the actual acoustic noise levels in rural primary healthcare centers, whether ASHAs prefer dictating over tapping on a tablet, and real-world network connectivity stability for mobile REST calls.

### Q2: Why does this project need speech? Why Gnani, and what did the account actually support?
**Answer:** Frontline workers speak code-mixed Indic languages (Hindi-English / Hinglish) while moving between households; typing on small smartphone keyboards with local Indic scripts is slow and error-prone. Gnani is uniquely suited because Prisma is natively trained on Indian accents, 8kHz/16kHz acoustic profiles, and code-mixing. Timbre provides natural Indic TTS for spoken clarification.

### Q3: What is your contribution beyond schema validation and ordinary confirmation?
**Answer:** Ordinary systems either passively accept ASR transcripts (risking silent data errors) or ask the user to confirm every single field (causing high cognitive burden). Our contribution is an active risk ranking policy: it computes uncertainty from structural validity, range bounds, and dictionary ambiguity, selecting the single highest-uncertainty field within a strict budget constraint ($\le 1$ prompt/form), cutting accepted error by 50% relative without burdening the user.

### Q4: How do IndicContextEval, DeRAGEC, and RAS limit your novelty claim?
**Answer:** IndicContextEval benchmarked contextual entity retrieval; DeRAGEC denoised candidate spans via retrieval; RAS formulated abstention in foundational speech models. We do not claim an algorithmic invention in foundation ASR training. Our contribution is an empirical systems study demonstrating that selective conversational clarification around a commercial Indic API improves task completion and reduces errors at fixed dialogue cost.

### Q5: Why use a small REST service instead of agents, a huge model, or streaming infrastructure?
**Answer:** A frontline visit form has four concrete, structured fields. Using an unconstrained LLM agent or a 70B parameter model introduces unpredictable hallucinations, high inference latency ($>3$ seconds), and unsustainable API costs. A lightweight FastAPI service with deterministic parsing and a SQLite state machine guarantees sub-second response times, zero token hallucination, full auditability, and runs on low-cost hardware.

### Q6: How do you preserve leading zeros, mixed number words, names, and ambiguous dates without guessing?
**Answer:** By separating raw spoken spans from canonical values in `FieldValue`. We never guess missing digits. Hindi number words (*पैंतालीस*) and Devanagari numerals are converted via strict dictionary tables (`HINDI_NUMBER_WORDS` and `DEVANAGARI_DIGITS`). If a date is ambiguous (e.g. 30 February), it is marked `NEEDS_REPEAT` rather than coerced.

### Q7: Why can WER improve while a form becomes less correct?
**Answer:** Word Error Rate (WER) weights all words equally. If ASR correctly transcribes twenty filler words (*"haan to dekhiye unka naam..."*) but flips the patient's age from 45 to 15, the overall WER might be an impressive 5%, but the medical visit record is 100% wrong. Form accuracy depends on entity exact match on task-critical fields, not grammatical fluency.

### Q8: How do budget matching, coverage, and confirmation errors affect the comparison?
**Answer:** Without budget matching, a trivial baseline that confirms all four fields (B3) achieves 0% error but requires 4 prompts per form (unusable in practice). By fixing the prompt budget to at most 1 prompt per form for both B1 and P, we evaluate true ranking quality. Coverage ensures the system cannot "cheat" by abstaining on every difficult form.

### Q9: How did you prevent speaker, template, and noise-variant leakage?
**Answer:** `scripts/validate_manifest.py` statically enforces that `SPK_DEV_*` and `SPK_TEST_*` sets have zero intersection. Template structures and patient identities are strictly disjoint between splits. All derived acoustic variants of a recording stay in the same split.

### Q10: What happens on missing confidence, 429, delayed responses, repeated save, or wrong-session access?
**Answer:**
- Missing provider confidence: Treated as `None`, falling back to deterministic parse and schema risk rather than defaulting to false certainty.
- HTTP 429 / 503: Exponential backoff with jitter and retry cap (2 retries).
- Delayed/stale responses: Version monotonicity (`expected_version`) rejects outdated responses with HTTP 409 Conflict.
- Repeated save: Handled via `idempotency_key` in SQLite `committed_records`.
- Wrong session: Draft IDs are UUID-based with strict draft isolation.

### Q11: What did it cost and how was latency measured? Which observations are cached?
**Answer:** End-to-end latency is measured via `time.perf_counter()` across STT, parser, and state updates (typically 400–800ms total). Live audio runs are fingerprinted via SHA-256; for reproducible benchmark evaluations, identical provider outputs are cached to prevent redundant credit drain.

### Q12: Describe one real bug, one rejected architecture, and one disappointing result.
**Answer:**
- **Real Bug:** Initial tests failed because `parse_village` returned Devanagari string `"रामपुर"` while gold labels expected title-case Latin `"Rampur"`. Fixed by implementing bidirectional transliteration in `VILLAGE_MAP`.
- **Rejected Architecture:** An initial concept considered an LLM-based agent with LangChain to correct errors. Rejected because it took 4.2 seconds per turn, hallucinated non-existent village names, and wasted API budget.
- **Disappointing Result:** Random field selection (B2) achieved zero error reduction over raw ASR on our test set because randomly prompting a field usually asked about an already correct field, proving that untargeted clarification is wasted dialogue.

### Q13: What breaks at 10× traffic or 10× data?
**Answer:** At 10× traffic, SQLite write locking would bottleneck concurrent draft updates; this is mitigated by migrating the state store to PostgreSQL with row-level locking. Furthermore, Gnani API rate limits (such as single-concurrency account limits) would queue requests, requiring asynchronous worker queues (Celery/ARQ with Redis) to buffer spikes.

### Q14: What additional evidence would justify a paper or deployment with real workers?
**Answer:** A formal field deployment requires a counterbalanced usability trial with 30+ consenting ASHA workers across primary health centers, measuring real-world task completion time, environmental acoustic noise resilience (SNR 0–10 dB), worker qualitative trust surveys, and an expanded multi-speaker corpus across Gujarati, Marathi, and Tamil.
