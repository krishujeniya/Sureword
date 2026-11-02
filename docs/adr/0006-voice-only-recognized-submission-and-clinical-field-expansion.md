# 0006. Voice-Only Recognized Submission and Clinical Field Expansion

Date: 2026-11-02  
Status: Accepted  

## Context

Sureword is designed for frontline healthcare workers (such as ASHA and ANM workers in India) who record patient visit narratives in rural and semi-urban settings. In actual field conditions:
1. Frontline workers frequently wear clinical gloves, navigate outdoor ambient sunlight, or possess limited keyboard typing literacy on low-cost Android smartphones.
2. Providing editable text fields and manual typing inputs invites typing latency, defeats the purpose of hands-free voice-to-form automation, and introduces data entry errors.
3. Frontline household encounters routinely capture clinical indicators beyond demographics—specifically patient **Gender** (महिला / पुरुष / अन्य) and **Chief Complaints / Symptoms** (Fever, Cough, Diarrhea, etc.).
4. The core benchmark evaluation for the Gnani.ai challenge requires the 4 primary fields (`person_name`, `age`, `village`, `visit_date`) to maintain strict invariant checking, deterministic accuracy, and budget-constrained clarification.

## Decision

1. **Pure Voice-Only Recognized Submission:**
   - Remove manual typing inputs from the Structured Visit Form. All fields are marked `readonly` and visually styled as voice-captured fields.
   - Remove the manual text input box and manual save button from the Clarification Banner. Clarification is executed strictly through spoken repeat (`🎙️ Speak Answer`), preserving a 100% voice-driven workflow.
   - Frontline workers dictate or select presets, review the recognized extraction cards, and explicitly commit verified records via the Save action.

2. **Clinical Field Expansion:**
   - Expand extraction to support **Gender** (`gender`: Female, Male, Other) and **Chief Complaints / Symptoms** (`symptoms`: Fever, Cough, Cold, Headache, Body Pain, Diarrhea, Weakness) across Indic languages.
   - Keep Gender and Symptoms as **optional fields**: they are extracted deterministically if dictated, but do not consume clarification budget ($Risk = 0.0$) and do not block commitment if unmentioned.

3. **Deterministic Parser Accuracy Upgrades:**
   - Suffix Village Extraction: Detect village markers following the name (e.g., `रामपुर गाँव`, `बिलासपुर गाव`, `Rampur village`).
   - Village Suffix Phonetics: Detect canonical geographic endings (`-pur`, `-nagar`, `-garh`, `-bad`, `-kheda`, `-gaon`).
   - Honorific and Title Normalization: Robustly strip titles (`श्रीमती`, `श्री`, `सुश्री`, `डॉ.`, `Mr`, `Mrs`) while parsing compound multi-word person names.

## Consequences

- **Positive:**
  - Frontline workers experience a genuine hands-free voice interface with zero keyboard friction.
  - Clinical documentation depth increases with structured capture of gender and chief complaints.
  - Extraction accuracy improves for natural conversational Indian speech patterns (e.g. suffix markers).
  - 100% backwards-compatibility is maintained for the Gnani.ai benchmark test suite.
- **Negative / Trade-offs:**
  - Users with severe speech impediments cannot type manual overrides directly on the frontend UI without invoking the backend API.
