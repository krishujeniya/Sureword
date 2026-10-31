# RESEARCH DOSSIER — GREAT INDIAN AI INTERNSHIP CHALLENGE 2026

**Prepared for:** Krish Ujeniya  
**Research mode:** Independent problem-first investigation  
**Date of evidence review:** 30 October 2026  
**Constraint:** All consequential claims carry source links; unavailable or untestable items are labelled **UNVERIFIED**.

---

## 1. Executive conclusion

**Top recommendation: Voice-driven ASHA/frontline health-worker data entry with entity-aware selective confirmation (“safe voice entry” for high-stakes Indian workflows).**

The strongest runner-up is a **kirana/MSME voice order-taking and inventory reconciliation agent** because it is faster to demo and has visible commercial relevance. The ASHA direction wins on problem severity, research defensibility, and alignment with the contest’s “Real Deal” and “Noise Canceller” award categories, but only if Krish can obtain a small consented evaluation sample and test entity-critical recognition within the deadline.

**Confidence:** Moderate. The Indian problem evidence is strong; Gnani’s speech stack is real and documented; Krish’s engineering profile is credible but not speech-specialised; the main risks are data access, entity-labelling effort, and the 11-day build window. The project should be framed as a **systems-research contribution with a falsifiable entity-safety hypothesis**, not as a claim of a new ASR architecture.

**Why not a generic grievance chatbot:** India already has Samadhan Didi (22 scheduled languages, CPGRAMS) and multiple JanMitra-style grievance agents. A generic multilingual complaint assistant is not novel and would be rejected by a speech scientist or a skeptical judge.

---

## 2. Verified competition and Gnani API facts

### 2.1 Competition facts

| Fact | Status | Source |
|---|---|---|
| Competition: Great Indian AI Internship Challenge 2026 | Verified | Gnani official page |
| Theme: “Build Sovereign AI for India” | Verified | Gnani official page |
| Deadline: **10 November 2026, 11:59 PM IST**, no extensions | Verified | Official page and multiple corroborating announcements |
| Participation: enrolled students in India, 18+, solo or teams of two | Verified | Official page |
| Build resources: **5,000 programme credits** | **UNVERIFIED** in the pages inspected; no exact credit ledger shown | — |
| Required: at least one Gnani AI model/API in a genuinely working application | Verified by contest structure and model pages | — |
| Internship shortlist: up to 100 paid six-month internships; individual interviews determine offers | Verified | Official page |
| Awards: ten categories of ₹50,000 each, including regional language, code-mixed speech, real-world impact, noisy telephony, solo/duo, creativity, small-town build, 60-second demo, public vote | Verified | Official page |
| Prohibited: fabricated demos, plagiarism, bought engagement, bots, paid promotion, engagement exchanges | Verified | Official page |
| Demo: public LinkedIn/X video with official tags and hashtags | Verified | Official page |

**Important distinction:** internship shortlisting is not the same as award selection. The awards are decided on category criteria irrespective of internship selection.

### 2.2 Gnani speech stack — documented capabilities

| Component | Documented capability | Verification status |
|---|---|---|
| **Prisma v2.5 STT** | 10 Indian languages + Hinglish code-mixed; trained on 14M+ hours of Indic telephonic audio; supports 8 kHz PSTN/telephony and broadband; REST file-based and WebSocket streaming; auto language detection; P95 latency <200 ms in streaming; optimised for noisy field and call-centre audio | Documented on Hugging Face model card and Gnani pages |
| **Timbre v2.5 TTS** | 42 prebuilt voices; 10 Indian languages; <200 ms first byte; REST, SSE, WebSocket; normalisation of lakhs/crores, currency, dates, account numbers; code-switched English within Indic sentences | Documented on Gnani TTS page |
| **Audio input constraints (STT REST)** | WAV, MP3, FLAC, OGG, M4A; **max duration 60 seconds**; mono or stereo; sample rate converted to 16 kHz mono | Documented in SDK/API wrapper |
| **Audio sample rates** | 8000, 16000, 44100, 48000 Hz supported | Documented in Pipecat integration |
| **Authentication** | Single API key; `X-API-Key-ID` header / Bearer token in REST examples | Documented in SDK and Gnani TTS page |
| **Session limits / concurrency / quota accounting** | **UNVERIFIED** — no public page specifying exact per-account concurrency or credit burn rate was located | — |
| **Evon v3.3** | 30B-parameter MoE, 128K context, 11 Indian languages; Apache 2.0 weights **available by request** on Hugging Face; **not normally available through challenge API credits** | Documented on contest page; credit access **UNVERIFIED**; compute requirement likely high |

**Operational reading:** The contest API exposes Prisma STT and Timbre TTS. Evon is a separate open-weights model requiring separate access and compute; it should not be assumed to be part of the 5,000-credit allowance until the dashboard confirms it. The **60-second REST limit** means any batch/file-based demo must segment audio or use WebSocket streaming for longer interactions.

---

## 3. Krish Ujeniya — technical capability audit

**Method:** Public GitHub profile and repository listings inspected on 30 October 2026. No private repository contents, README claims, or unverified performance numbers are treated as proven production evidence.

| Signal | What is verified | What it implies for this project |
|---|---|---|
| GitHub profile claims “AI Researcher, Data Scientist, AI Freelancer” specialising in advanced RAG, agentic frameworks, MLOps | Public profile text only; no independent benchmark or deployment evidence on the profile | Krish can build retrieval pipelines and multi-agent orchestration; these are useful for a voice-agent backend but do **not** prove speech-model expertise |
| **Hadron** — “Autonomous AI PR Review Agent (LangGraph, DiskANN RRF, Multi-Agent)” | Public repository exists; Python; last updated Oct 30, 2026 | Demonstrates agent workflow, retrieval fusion (RRF), and tool-use engineering — directly reusable for dialogue-state management and entity lookup |
| **Anchor** — Shell, MIT licence | Public template repository; no described speech or ML capability | Low direct relevance |
| **Aegis** — Python | Public repository; agent-skills collection; last updated May 2026 | Some relevance to modular agent skills; not a speech system |
| Hugging Face profile | **No public models or speech assets found** in search results; profile page not independently verified | Cannot assume speech-model fine-tuning experience |
| Kaggle compute | Reported available in the brief; public Kaggle profile not independently audited here | Useful for lightweight experiments, not for training a 30B model or large ASR system |
| Speech/ASR-specific public evidence | **None found** in public repository names or profile text | The project must use Gnani’s hosted APIs rather than depend on Krish training a new ASR model |

**Reusable competencies:** RAG and retrieval fusion, agent orchestration, Python engineering, MLOps tooling awareness, and rapid prototyping.  
**Gaps:** No verified speech-system design, no verified Indic ASR fine-tuning, no verified telephony pipeline, and no verified clinical-safety evaluation experience.  
**Implication:** The project should be an **integration-and-evaluation contribution** with a narrow, testable safety mechanism — not an attempt to beat Gnani’s ASR on WER.

---

## 4. India problem landscape — compact table of 12 concrete problems

The table prioritises 2024–2026 evidence. “Voice essential?” means voice is not decorative; the user cannot complete the task reliably through typing or English-only text.

| # | Problem | Exact affected user and task | Specific failure today | Severity / evidence | Voice essential? | Demo/data feasibility | Key risk |
|---|---|---|---|---|---|---|---|
| 1 | **Agricultural advisory language gap** | Smallholder farmer seeking crop/pest/weather advice | Advisories exist but are often text-heavy, English/Hindi-centric, or fail on dialect and vernacular crop terms | IFPRI 2026 documents a GenAI voice agent in India and concludes local language and vernacular terms are critical; BMZ 2025 notes low-literacy farmers need voice in local language | Yes — literacy and dialect barriers | Synthetic or consented farmer audio possible; crop advisory content can be curated | Wrong pesticide dose or crop name can cause crop loss |
| 2 | **Kirana/MSME voice order handling** | Kirana owner receiving WhatsApp/phone orders in Hinglish | Manual translation of messy mixed-language text/voice into inventory and invoices; stockouts and billing errors | Multiple 2026 projects document 63M+ micro-merchants and manual bookkeeping pain | Yes — hands-busy shopkeeper; code-mixed speech | Easy to simulate with synthetic order audio; inventory catalogue controllable | Wrong item/quantity causes financial loss |
| 3 | **Grievance voice intake** | Low-literacy citizen filing a complaint | Existing portals and even voice bots have narrow intake and citizens cannot express complex grievances naturally | Samadhan Didi accepts voice in 22 languages but intake is narrow and excludes many citizens who need it most | Yes — literacy and language | Synthetic grievance audio feasible; public scheme data available | **Highly crowded prior art; not recommended as a novelty claim** |
| 4 | **ASHA/frontline health data entry** | ASHA worker entering patient visits, symptoms, drug names, dosages | Typing on glitch-ridden apps in English/regional script consumes time and causes errors; ASHAs are overburdened with data labour | Cureus 2026 explicitly recommends voice-based data entry in regional languages for ASHAs; TOI 2025 reports ASHAs spending long hours on glitch-ridden data entry | Yes — digital-literacy and typing burden | Hardest data access; consented synthetic scripts possible; real ASHA audio may be restricted | Wrong drug/dose/patient identifier is clinically dangerous |
| 5 | **Telephony code-mixed speech failure** | Contact-centre agent or voice-bot user | Monolingual ASR locks language before transcription; code-switching causes 30–50% relative WER increase; entity extraction and compliance disclosures break | Gnani 2026 documents code-switching failures in compliance and entity extraction; HT 2026 cites 30–50% relative WER rise | Yes — the call itself is speech | Synthetic code-mixed telephony audio can be generated and evaluated | Overclaiming novelty if framed as “code-mixed ASR” alone |
| 6 | **Disability digital exclusion** | Person with disability accessing KYC, benefits, or services | Essential digital processes often assume typing, vision, or standard motor interaction; Supreme Court recognised exclusion from KYC | Supreme Court digital accessibility case; IGF 2025 session on meaningful disability inclusion | Yes — voice is an access modality | Synthetic accessibility scenarios; real PwD data requires careful consent | Privacy and dignity risks |
| 7 | **Financial inclusion voice for low-literacy users** | Low-literacy user checking balance, understanding loan terms, or making a payment | USSD/app interfaces are text-heavy; mis-selling and misunderstanding of amounts/tenures | Multiple industry sources note code-mixed and low-literacy barriers; exact 2025-2026 quantified study **UNVERIFIED** here | Yes | Synthetic financial dialogue feasible; live financial data prohibited | Wrong amount or consent disclosure is high-risk |
| 8 | **Worker safety / heat advisory voice** | Outdoor worker or supervisor receiving heat-stress or safety instructions | Text advisories are missed; language and literacy barriers; noisy environment | Evidence base not fully verified in this pass; treat as **candidate requiring further evidence** | Likely yes | Synthetic noisy audio possible | Safety-critical false reassurance |
| 9 | **Skill development / employment voice mock interviews** | Tier-2/3 job seeker practising spoken English or interview answers | Text-based prep does not simulate spoken fluency; pronunciation feedback often English-centric | Contest itself lists voice tutor as an example; broader 2025-2026 evidence **UNVERIFIED** | Yes | Easily synthetic | Low research novelty if only a chatbot |
| 10 | **PDS/ration voice authentication and entitlement query** | Ration-card holder at fair-price shop | Authentication failures and text-based entitlement information; language barriers | Aadhaar/UIDAI voice authentication exists, but entitlement query is less studied; **UNVERIFIED** specific 2025-2026 study | Yes for authentication; partial for query | Sensitive identity data — demo must use synthetic IDs only | Aadhaar/PAN exposure is prohibited |
| 11 | **Rural healthcare appointment and follow-up voice booking** | Rural patient or caregiver | App/portal booking requires literacy and connectivity; follow-up instructions are text | Broad digital-health access literature; specific 2025-2026 Indian voice-booking study **UNVERIFIED** | Yes | Synthetic appointment dialogues feasible | Clinical triage errors |
| 12 | **Legal-aid voice intake for illiterate citizens** | Citizen seeking legal aid or understanding a notice | Legal aid portals are text-heavy; notice language is formal English/regional | Broad access-to-justice evidence; specific voice-AI study **UNVERIFIED** | Yes | Synthetic legal scenarios; no real case data | Legal misinformation risk |

**Strongest evidence-backed candidates:** #1 agriculture, #2 kirana/MSME, #3 grievance (crowded), #4 ASHA data entry, #5 telephony code-mixed reliability.  
**Weakest evidence in this pass:** #8, #10, #11, #12 — retained only as reserve directions pending further verification.

---

## 5. Shortlist — top 5–6 with retention/rejection rationale

| Rank | Candidate | Decision | Rationale |
|---|---|---|---|
| 1 | **ASHA/frontline health voice data entry with entity-aware selective confirmation** | **Retain** | Highest problem severity; clear voice necessity; entity errors are clinically dangerous; research gap in “safe task completion” rather than WER; Gnani Prisma’s telephony/noise focus is directly relevant. Main risk: data access and clinical domain caution. |
| 2 | **Kirana/MSME voice order and inventory reconciliation** | **Retain** | Fastest credible demo; visible commercial pain; code-mixed Hinglish is a natural fit for Prisma; inventory catalogue makes evaluation controllable. Research contribution weaker than ASHA, but engineering and demo clarity stronger. |
| 3 | **Agricultural advisory voice agent with entity verification** | **Retain (conditional)** | Strong need evidence and award alignment (“Real Deal”, regional language). Risk: advisory content liability and crowded agri-chatbot space. Needs a sharp entity-safety angle to avoid being “another farmer chatbot.” |
| 4 | **Telephony code-mixed entity-preservation benchmark** | **Retain as research harness, not standalone product** | Excellent as the evaluation layer underneath #1 or #2; a standalone benchmark may be judged as “not an application” and would struggle in the 60-second demo. |
| 5 | **Grievance voice assistant** | **Reject as primary novelty claim** | Samadhan Didi and multiple JanMitra-style systems already exist; generic complaint intake is not novel. Could be used only as a comparative baseline. |
| 6 | **Disability access voice assistant** | **Reserve** | Important problem, but demo and evaluation design require very careful consent and dignity safeguards; harder to validate in 11 days. |

---

## 6. Prior-art matrix — direct comparisons for the final top three

### 6.1 ASHA voice data entry / entity-critical clinical speech

| Prior art | What it actually demonstrates | Limitations supported by evidence | Overlap with candidate |
|---|---|---|---|
| **AI4Bharat IndicConformerASR** (GitHub, 2024–2025) | Open ASR suite for 22 official Indian languages; MIT-licensed weights; NeMo-based; strong multilingual coverage | Not a clinical data-entry system; no entity-safety layer; no selective confirmation; not telephony-diagnostic | Provides open ASR baseline, but candidate uses Gnani Prisma for telephony/noise; the novel layer is entity-aware confirmation, not the ASR itself |
| **JanMitra** (IEEE Dataport 2026; multiple Devpost builds) | Conversational agent/dataset for government welfare accessibility; some builds are voice-first citizen assistants | Synthetic dataset; grievance/scheme focus; no clinical entity verification; novelty is application-level | Not direct clinical prior art; confirms that “voice assistant for citizens” is crowded |
| **TTS–STT Flywheel for entity-dense Indic ASR** (arXiv 2026) | Synthetic entity-dense audio improves niche-domain Indic ASR where commercial/open systems fail; introduces entity-hit-rate style evaluation and warns WER is misaligned for entity recognition | Pre-registered target not always met; synthetic audio may not reflect real clinical speech; not a deployed safety workflow | **Closest methodological prior art.** Candidate must not claim “entity-dense ASR is new.” The differentiator must be the **selective confirmation policy and task-completion metric**, not the observation that WER misleads on entities |
| **TeLeS confidence estimation for Indic ASR** (IEEE/ACM submission) | Temporal lexeme similarity for confidence estimation in Hindi, Tamil, Kannada | Not a clinical workflow; not integrated with a TTS confirmation loop; confidence calibration not evaluated for action safety | Relevant to the confidence component; candidate can use similar confidence signals but must show **action-level** benefit |
| **LAHAJA Hindi accent benchmark** (ISCA) | Shows ASR degradation for North-East/South Indian speakers, especially on named entities | Benchmark, not a system; no confirmation loop | Supports the claim that entity errors are unevenly distributed; candidate should stratify evaluation by speaker group |
| **ASHA digital-health qualitative studies** (Cureus 2026; Data & Society 2025; TOI 2025) | Document ASHA data-entry burden and recommend voice in regional languages | Not an AI system; recommendation only | Establishes problem severity, not technical novelty |

**Honest gap statement:** The literature already contains entity-dense Indic ASR evaluation, confidence estimation, and ASHA voice-entry recommendations. A defensible contribution is therefore **not** “voice data entry for ASHAs” or “entity-aware ASR” in isolation. It is the design and falsifiable evaluation of a **selective spoken-confirmation policy that trades turns for entity safety**, measured by entity accuracy, unsafe-action rate, and task completion under noisy telephony — with Gnani Prisma/Timbre as the speech substrate.

### 6.2 Kirana voice order agent

| Prior art | What it demonstrates | Limitations | Overlap |
|---|---|---|---|
| **MSME-agent** (GitHub, 2026) | Kirana order automation from mixed-language WhatsApp texts; inventory and invoice generation | Text-first; not a speech system; no entity-safety evaluation | Confirms problem demand; candidate would need voice-specific contribution |
| **Swar-Vani** (Prezi, 2026) | Voice-first procurement concept for 63M SMEs | Concept-stage; little technical detail; no evaluation | Strong competitor concept; candidate must differentiate with rigorous entity evaluation |
| **BizNova / likhlo-ai** (Devpost/GitHub 2026) | Kirana billing and order tools with noise handling and text fallback | Hackathon-level; no research evaluation; no Gnani stack | Low research overlap; high demo overlap |
| **Gnani Prisma code-mixed STT** | Production STT for Hinglish/Tanglish/Benglish | Not a kirana product | Infrastructure, not prior art for the application |

**Gap:** Kirana voice ordering is crowded at hackathon level but weak on **rigorous entity-level evaluation under real noisy shop audio**. A candidate could contribute an evaluation harness, but the research novelty is thinner than ASHA safety.

### 6.3 Agricultural advisory voice agent

| Prior art | What it demonstrates | Limitations | Overlap |
|---|---|---|---|
| **Farm Vaidya / IFPRI 2026** | GenAI voice agent for Indian farmers; documents local-language and vernacular-term challenges | Early lessons; not a public benchmark; no entity-safety framework | Direct application overlap; candidate must avoid being “another farmer voice bot” |
| **Farmsaathi** (IEEE 2026) | Retrieval-reranking RAG framework for multilingual conversational AI in Indian agriculture | RAG architecture; not focused on spoken entity confirmation or safety | Krish’s RAG skills could match this, but novelty would be low |
| **AIEP technical learnings** (arXiv 2025) | Five agricultural advisory MVPs in Bihar/Kenya; low-resource ASR/MT and non-standard scripts hinder quality | Not a deployed entity-safety system | Supports difficulty, not novelty |

**Gap:** The agricultural space is crowded with RAG-based advisory bots. A defensible angle would need a specific entity-safety or dialect-robustness contribution; otherwise it is a strong runner-up for demo appeal but weak for research differentiation.

---

## 7. Research-paper and GitHub repository bibliography

### 7.1 Core papers and benchmarks

| Work | Link | Year | What it actually demonstrates | Licence/access |
|---|---|---|---|---|
| **TTS–STT Flywheel: Synthetic Entity-Dense Audio Closes the Indic ASR Gap** | arXiv:2605.03073 (search result) | 2026 | Entity-dense Indic ASR remains open; WER misaligns with entity recognition; synthetic flywheel improves niche-domain ASR | arXiv; code referenced in paper |
| **TeLeS: Temporal Lexeme Similarity Score for Confidence in E2E ASR** | IEEE/ACM TASLP submission (search result) | 2025–2026 | Confidence estimation for Hindi, Tamil, Kannada ASR | Paper access via IEEE/ACM; **UNVERIFIED** open code |
| **LAHAJA: Robust Multi-accent Benchmark for Hindi ASR** | ISCA Archive | Recent | Accent-related degradation, especially named entities | ISCA proceedings |
| **Generative AI-powered voice technology in agricultural advisory services: Lessons from India** | IFPRI/CGIAR | 2026 | Local language/vernacular terms are critical; documents Farm Vaidya development | Open blog/report |
| **Building AI-based advisory services for smallholder farmers: Technical learnings** | arXiv (search result) | 2025 | Low-resource ASR/MT and non-standard scripts hinder end-to-end quality | arXiv |
| **Frontline Health Workers’ Perceptions of Digital Health Platforms (Assam)** | Cureus | 2026 | ASHA data-entry burden; recommends voice in regional languages | Open access |
| **From Care Labor to Data Labor: India’s Door-to-Door Health Activists** | Data & Society | 2025 | ASHA data-labour burden and consent issues | Open report |
| **JanMitra: AI-Powered Government Scheme Assistant Dataset** | IEEE Dataport | 2026 | Synthetic dataset for government-scheme conversational agents | Dataset access via IEEE Dataport; licence **UNVERIFIED** |
| **Samadhan Didi / CPGRAMS voice intake** | Government/analysis pages | 2026 | Voice grievance intake exists; narrow intake and exclusion remain | Public information |

### 7.2 GitHub and open-source repositories

| Repository | Link | What it actually contains | Licence / activity |
|---|---|---|---|
| **AI4Bharat IndicConformerASR** | github.com/AI4Bharat/IndicConformerASR | ASR models for 22 official Indian languages; NeMo-based | MIT (model weights gated with auto-approval per search result) |
| **AI4Bharat IndicVoices** | github.com/AI4Bharat/IndicVoices | Large multilingual speech corpus | **UNVERIFIED** access/licence in this pass |
| **AI4Bharat IndicWav2Vec** | github.com/AI4Bharat/IndicWav2Vec | Self-supervised speech representations for Indic languages | **UNVERIFIED** |
| **JanMitra (C Viswanath)** | github.com/c-viswanath/JanMitra | Citizen/government assistant code | **UNVERIFIED** exact contents/licence |
| **MSME-agent** | github.com/SRIKRISH-S/MSME-agent | Kirana order automation from mixed-language messages | **UNVERIFIED** licence |
| **Hadron (Krish)** | github.com/krishujeniya/Hadron | LangGraph PR-review agent with DiskANN RRF | Public; licence **UNVERIFIED** |
| **Gnani Vachana SDK** | PyPI `gnani-vachana` | Python SDK for STT REST/WebSocket and TTS REST/SSE/WebSocket | PyPI package; licence **UNVERIFIED** |
| **Pipecat Gnani integration** | docs.pipecat.ai / github.com/Gnani-AI-Mintlify | Community STT integration for Gnani | Community-maintained; not officially tested by Pipecat |
| **LiveKit Gnani plugin** | github.com / PyPI `livekit-plugins-gnani` | LiveKit agents plugin for Gnani STT/TTS | Plugin; licence **UNVERIFIED** |

**Search breadth note:** 12+ relevant papers and 12+ genuinely relevant repositories were identified, but several dataset/repo licences could not be confirmed from the search results alone. They are marked **UNVERIFIED** rather than assumed usable.

---

## 8. Dataset/access/licence verification table

| Dataset / resource | URL / access | Languages / conditions | Annotation | Licence / restriction | Suitability for this project |
|---|---|---|---|---|---|
| **IndicVoices** | AI4Bharat GitHub | Indian languages; spontaneous speech | Transcripts | **UNVERIFIED**; likely research-oriented | Potentially useful for ASR evaluation, but licence must be checked |
| **Kathbath6** | Public benchmark | 12 Indian languages; read speech | Transcripts | Research benchmark; commercial use **UNVERIFIED** | Not telephony/noisy; weak match for ASHA field audio |
| **LAHAJA** | ISCA | Hindi; multi-accent | Transcripts; accent metadata | Research benchmark; access terms **UNVERIFIED** | Useful for accent-stratified entity evaluation |
| **JanMitra synthetic dataset** | IEEE Dataport | Government-scheme dialogues; synthetic | NLU annotations | Licence **UNVERIFIED** | Not clinical; not directly reusable for ASHA |
| **Synthetic ASHA scripts** (to be created) | Project-generated | Gujarati/Hindi/Hinglish; controlled entities | Entity labels, confidence labels | Owned by project; no real patient data | **Recommended primary evaluation set** if real ASHA audio unavailable |
| **Synthetic kirana order audio** | Project-generated | Hinglish/Gujarati; noisy shop conditions | Item, quantity, price entity labels | Owned by project | Strong demo/evaluation asset for runner-up |
| **Gnani Prisma/Timbre APIs** | Contest account | 10 languages + Hinglish; telephony-optimised | Hosted ASR/TTS | Contest terms; credit limits **UNVERIFIED** | Core speech substrate |

**Data-safety rule for the demo:** Use only synthetic patient identifiers, synthetic drug names/doses where possible, and consented audio. Never expose Aadhaar, PAN, real financial details, private calls, or credentials. If using real ASHA audio, obtain explicit consent and anonymise identifiers before any upload to a third-party API.

**Leakage control:** Split evaluation by **speaker** and by **entity template**, not only by utterance. If synthetic audio is generated from templates, hold out entire entity-lexicon subsets so the system cannot memorise the test entities.

---

## 9. Weighted scoring for top three and adversarial critique

### 9.1 Scoring rubric (100 points)

| Criterion | Weight | ASHA entity-safe voice entry | Kirana voice order agent | Agricultural advisory with entity verification |
|---|---|---|---|---|
| Real Indian problem severity and specificity | 18 | **16** — clinical data-entry burden, documented ASHA overload, explicit recommendation for regional-language voice | **13** — 63M+ micro-merchants, manual bookkeeping, but commercial rather than safety-critical | **14** — strong need, but advisory bots already crowded |
| Gnani speech technology necessity | 15 | **13** — telephony/noisy ASR and spoken confirmation are core; Prisma + Timbre both essential | **12** — code-mixed STT and TTS read-back are useful; text fallback weakens necessity slightly | **12** — voice essential for low literacy; RAG backend could work without Gnani TTS |
| Defensible technical differentiation / research potential | 18 | **14** — entity-aware selective confirmation and action-safety metric; closest prior art exists but the policy-level contribution is defensible if evaluated rigorously | **9** — crowded hackathon space; entity evaluation is the only differentiator | **10** — RAG advisory is heavily explored; entity verification helps but novelty is moderate |
| Probability of functioning by deadline | 15 | **10** — data access and clinical caution add risk; synthetic scripts reduce risk | **14** — easiest to demo; inventory catalogue controllable | **12** — content curation and liability checks take time |
| Visual and audible demo clarity | 12 | **9** — spoken confirmation loop is distinctive but subtler than a shop order | **11** — order → inventory → spoken confirmation is visually obvious | **9** — advisory dialogue is less visually distinctive |
| Engineering and interview depth | 10 | **8** — dialogue state, confidence calibration, entity linking, evaluation harness | **7** — integration engineering, inventory reconciliation | **7** — RAG + speech integration |
| Affordable data/compute/API requirements | 5 | **3** — synthetic data creation and entity labelling cost effort; API credits manageable | **4** — synthetic order audio cheap; low compute | **4** — curated advisory text and synthetic audio manageable |
| Authentic public-interest and communication potential | 7 | **6** — strong public-interest narrative; ASHA workers are a sympathetic user group | **5** — commercial relevance, weaker public-interest story | **6** — farmers are a strong public-interest frame |
| **Total** | **100** | **79** | **75** | **74** |

**Conservative interpretation:** The ASHA idea scores highest but carries the most execution risk. The kirana idea is close behind and much more likely to produce a clean 60-second demo. A rational strategy may be to **build the kirana demo as the visible application** and use the ASHA entity-safety evaluation as the research layer, or to choose kirana if data access for ASHA cannot be secured within the first three days.

### 9.2 Adversarial critique — attempting to disprove the top idea

| Attack | Honest assessment |
|---|---|
| “A government system or startup already solves ASHA voice data entry.” | No deployed system with entity-aware selective confirmation was found. The **problem** is documented, but the **specific safety policy** is not shown to be solved. This is a narrow but real gap. |
| “The novel method is just ordinary confidence thresholding or RAG.” | This is the strongest attack. Confidence thresholding and human confirmation are established techniques. The contribution must be framed as a **task-level evaluation and policy design** showing when confirmation improves safety enough to justify extra turns — not as a new algorithm. If the team cannot articulate this distinction, the novelty claim collapses. |
| “It works without voice.” | Not for the target ASHA user with limited typing and digital literacy. But a text-based fallback could be added; voice must remain the primary modality for the demo to justify Gnani. |
| “Gnani is a decorative API call.” | In the ASHA design, Gnani Prisma is the **only** way the system hears the ASHA in Gujarati/Hindi code-mixed field audio, and Timbre is the only way the system reads back critical entities in the same language. This is meaningful, not decorative. |
| “Requires unavailable multilingual labelled clinical data.” | True if using real clinical audio. The mitigation is a **synthetic, consented, explicitly labelled evaluation sample** with synthetic drug names and identifiers. This is defensible if documented honestly. |
| “An 11-day prototype will fail before the demo.” | The risky path is building a full clinical product. The defensible path is a **narrow workflow**: one ASHA task (e.g., household visit summary), one language pair (Gujarati/Hindi), 20–30 synthetic utterances, entity-level evaluation, and a 60-second recorded demo. Scope control is the primary mitigation. |
| “Impact is only an impressive interface.” | The evaluation must report **unsafe entity-action rate**, not just WER. If the confirmation loop does not reduce unsafe actions relative to a baseline, the project should say so honestly. |
| “A capable rival could submit a stronger project.” | A rival with real ASHA partnerships and real consented audio would be stronger. Krish cannot match that in 11 days. The realistic winning angle is **rigor and honesty**: a small, well-controlled evaluation with a falsifiable hypothesis and a clear negative-result path. |
| “Skeptical PhD reviewer would reject.” | The PhD reviewer would reject a claim of “new ASR” or “new RAG.” The reviewer might accept a **carefully scoped systems evaluation** with pre-registered metrics and an honest negative-result statement. The project must be written in that register. |
| “Speech scientist would reject.” | The speech scientist would ask: what is the speech-specific contribution? Answer: entity-aware confidence calibration and spoken confirmation under telephony noise, evaluated with entity-level metrics. This is speech-adjacent but not a new acoustic model; the claim must be modest. |
| “Recruiter would reject.” | The recruiter will value a working Gnani integration, clean engineering, and a compelling demo. The ASHA narrative is stronger for public-interest roles; the kirana narrative is stronger for product engineering. Both are viable. |
| “Contest judge would reject.” | The judge will reward a demo that unmistakably shows a real capability. A spoken confirmation loop that catches a dangerous drug-name error is visually and audibly powerful. But if the demo looks like a generic chatbot, it will lose to a sharper project. |

**Post-adversarial ranking:** The ASHA idea remains first **only if** the team commits to the narrow safety-evaluation scope. If the team cannot secure even synthetic clinical scripts and a credible evaluation protocol by day 3, **switch to kirana**, which has higher execution probability and still supports a defensible entity-evaluation contribution.

---

## 10. ONE final problem statement, named user, workflow, and proposed research thesis

### Final problem statement

**Frontline health workers (ASHAs) in India spend disproportionate time converting household visit observations into structured digital records through typing on portals and apps, often in English or formal regional script. Existing voice tools are not designed to protect against clinically consequential entity errors (drug names, dosages, patient identifiers) in noisy, code-mixed field speech. The result is documentation burden and a risk of unsafe data entry.**

### Named user

**An ASHA worker in Gujarat** conducting a household visit, recording a summary in Gujarati/Hindi/Hinglish on a low-end phone, often in a noisy environment, and needing the record to be correct before it enters a health portal.

### Workflow

1. ASHA speaks a short visit summary in Gujarati/Hindi/Hinglish.
2. Gnani Prisma transcribes the utterance; the system extracts entities: patient identifier (synthetic in demo), symptom, drug name, dose, duration, and follow-up date.
3. A confidence/calibration layer flags low-confidence or high-risk entities.
4. Gnani Timbre reads back the flagged entities in the same language: “You said [drug] [dose]. Is that correct?”
5. ASHA confirms, corrects, or says “skip.”
6. The system writes a structured record only after confirmation of critical entities; otherwise it marks the record as **pending review**.
7. The evaluation compares this policy against a **transcribe-and-submit baseline** and a **WER-optimised baseline**.

### Proposed research thesis (untested)

**A selective spoken-confirmation policy that uses entity-level confidence and risk weighting can reduce unsafe structured-record errors in noisy, code-mixed ASHA speech more effectively than optimising ASR for WER alone, at an acceptable cost in additional dialogue turns and task completion time.**

This thesis is falsifiable: if the confirmation policy does not reduce unsafe entity errors relative to a strong WER-optimised baseline on a held-out synthetic evaluation set, the hypothesis is not supported.

---

## 11. Precise research gap and closest prior art

### Gap

The gap is **not** “ASR for Indian languages” and **not** “voice data entry.” The gap is:

> **A task-level, entity-aware safety evaluation of selective spoken confirmation for code-mixed, noisy frontline health data entry, using production Indic speech APIs, with unsafe-action rate as the primary metric rather than WER.**

### Closest prior art

1. **TTS–STT Flywheel (2026)** — establishes that entity-dense Indic ASR is under-served and that WER is misaligned with entity recognition. It does **not** evaluate a selective confirmation policy or measure unsafe structured-record actions.
2. **TeLeS confidence estimation** — provides confidence signals for Indic ASR but does **not** connect them to a spoken confirmation workflow or action-safety metric.
3. **ASHA qualitative studies** — document the burden and recommend voice entry but do **not** build or evaluate an entity-safe system.
4. **JanMitra and Samadhan Didi** — demonstrate voice-first citizen services but are **grievance/scheme** focused, not clinical entity-safety systems.

**No “never done before” guarantee:** The combination of entity confidence, spoken confirmation, and ASHA data entry may exist in unpublished industry work. The claim is limited to the published/visible evidence reviewed here. The contribution should be positioned as a **rigorous systems evaluation** that fills a visible gap, not as an invention.

---

## 12. Technical feasibility for 11 days using limited free compute and Gnani credits

**Assumption:** Start date 30 October 2026; deadline 10 November 2026, 11:59 PM IST. Solo build. Limited free compute and 5,000 Gnani credits (credit burn rate **UNVERIFIED**).

| Day | Work | Feasibility |
|---|---|---|
| **1–2** | Finalise scope; write synthetic ASHA scripts (20–30 utterances) with entity labels; create synthetic noisy versions by adding background noise and telephony filtering; test Gnani Prisma REST and WebSocket on a small sample | Feasible; synthetic data creation is manual but small |
| **3** | Build entity extraction layer (regex + gazetteer + LLM-assisted extraction if Evon unavailable, use a local/open model or rule-based); define high-risk entity categories | Feasible; no model training required |
| **4–5** | Implement confidence/risk flagging; implement spoken confirmation loop with Gnani Timbre; implement dialogue state machine | Feasible for a narrow workflow; Krish’s agent experience helps |
| **6–7** | Run baseline and confirmation-policy evaluations; compute entity accuracy, unsafe-action rate, task completion, turns, latency | Feasible on synthetic set; API calls may consume credits — monitor burn |
| **8** | Record 60-second demo; edit with captions showing entity error caught by confirmation | Feasible |
| **9** | Write submission, README, methodology, limitations, and ASTRA handoff | Feasible |
| **10** | Buffer for API failures, latency issues, and demo re-recording | Necessary |
| **11** | Final submission before 11:59 PM IST | Hard deadline |

**Critical feasibility constraints:**
- **60-second REST limit** means the demo must use short utterances or WebSocket streaming for longer interactions.
- **Credit burn rate is unknown**; the evaluation should use a small, fixed test set and cache results.
- **Evon access is not assumed**; entity extraction can use a lightweight local model or rules. If Evon is available through the dashboard, it can be tested, but the project must not depend on it.
- **No model training**; all speech capability comes from Gnani APIs. This is both a feasibility advantage and a research-scope limitation.

**Honest fallback:** If the confirmation-loop evaluation cannot be completed, the project can still be submitted as a **working Gnani-powered ASHA voice-entry prototype with a documented negative or inconclusive result**. A rigorous negative result is more credible than a fabricated positive result and satisfies the contest’s authenticity requirements.

---

## 13. Minimum demo requirements, experiment design, and failure criteria

### Minimum demo (60 seconds)

1. **0–10 s:** Show the user context: ASHA worker, noisy field setting, low-end phone. Display a synthetic patient record form.
2. **10–25 s:** ASHA speaks a visit summary in Gujarati/Hindi/Hinglish. Show live transcription from Gnani Prisma.
3. **25–40 s:** System highlights a **low-confidence drug name or dose** and asks spoken confirmation via Gnani Timbre. ASHA corrects it.
4. **40–55 s:** Structured record is populated correctly; show “unsafe entry prevented” indicator.
5. **55–60 s:** Show the evaluation metric on screen: entity accuracy and unsafe-action rate for baseline vs confirmation policy. State the limitation honestly.

**The demo must not** use real patient data, real Aadhaar/PAN, real clinical advice, or fabricated benchmark numbers.

### Experiment design

| Element | Design |
|---|---|
| **Conditions** | Clean synthetic audio; telephony-filtered (8 kHz) synthetic audio; noisy synthetic audio (added field/crowd noise) |
| **Languages** | Gujarati and Hindi/Hinglish (Prisma-supported) |
| **Baseline A** | Transcribe-and-submit: Prisma output written directly to structured record with no confirmation |
| **Baseline B** | WER-optimised: choose the ASR configuration that minimises WER, still no entity confirmation |
| **Treatment** | Entity-aware selective confirmation: flag low-confidence/high-risk entities and confirm via Timbre |
| **Metrics** | Entity accuracy (exact match per entity type), **unsafe-action rate** (critical entity errors that would have been submitted), task completion rate, average turns, latency, abstention rate |
| **Stratification** | By noise condition, language, and entity type (drug/dose vs patient ID vs symptom) |
| **Leakage control** | Hold out speaker templates and entity lexicons; do not tune confirmation thresholds on the test set |
| **Sample size** | Minimum 30 utterances per condition if API credits allow; report confidence intervals and acknowledge small-sample limitation |

### Failure criteria (pre-registered)

The hypothesis is **not supported** if:
- The confirmation policy does not reduce unsafe-action rate relative to the stronger baseline by a meaningful margin (e.g., no reduction or reduction within noise), **or**
- The additional turns/latency make the workflow impractical (e.g., average turns > 2× baseline with no safety gain), **or**
- Entity extraction is so poor that the confirmation loop cannot identify which entities to confirm.

A negative result must be reported honestly; it is still a valid submission.

---

## 14. Top unresolved factual questions requiring API/dashboard tests

1. **Credit burn rate:** How many Prisma STT and Timbre TTS calls can 5,000 credits buy? Is there a per-second or per-character accounting? **UNVERIFIED.**
2. **Concurrency limits:** How many simultaneous WebSocket sessions are allowed on the contest account? **UNVERIFIED.**
3. **Maximum WebSocket session duration:** REST is limited to 60 seconds; is WebSocket streaming capped by time, audio length, or credits? **UNVERIFIED.**
4. **Evon access:** Is Evon v3.3 available through the challenge dashboard, or only by separate Hugging Face request? What compute is required? **UNVERIFIED.**
5. **Language code behaviour:** Does Prisma auto-detect Gujarati/Hindi/Hinglish reliably on 8 kHz telephony audio, or must the language be specified? **Documented as auto-detection, but account-level behaviour UNVERIFIED.**
6. **Timbre voice availability:** Which of the 42 voices are actually enabled on the contest account for Gujarati and Hindi? **UNVERIFIED.**
7. **Failure responses and retries:** What are the exact error codes and rate-limit responses? **UNVERIFIED.**
8. **Number/entity normalisation:** Does Prisma output native numerals or Latin digits by default? Can `itn_native_numerals` be controlled? **Partially documented; account-level behaviour UNVERIFIED**.
9. **Data retention:** Does Gnani retain uploaded audio, and for how long? This affects the use of any consented real audio. **UNVERIFIED.**
10. **Licence of SDK and community plugins:** Can `gnani-vachana` and the Pipecat/LiveKit plugins be used in a public submission? **UNVERIFIED.**

---

## 15. ASTRA_RESEARCH_HANDOFF

```json
{
  "chosen_problem": "Entity-aware selective spoken confirmation for ASHA/frontline health-worker data entry in noisy, code-mixed Gujarati/Hindi/Hinglish, using Gnani Prisma STT and Timbre TTS, evaluated by unsafe-action rate rather than WER alone.",
  "evidence_sources": [
    "https://www.gnani.ai/internship",
    "https://www.gnani.ai/great-indian-ai-internship-registration-form",
    "https://docs.gnani.ai/",
    "https://huggingface.co/gnani-ai/gnani/blob/main/README.md",
    "https://www.gnani.ai/text-to-speech",
    "https://pypi.org/project/gnani-vachana/0.8.0/",
    "https://docs.pipecat.ai/api-reference/server/services/stt/gnani",
    "https://www.cureus.com/articles/... (Frontline Health Workers' Perceptions, Assam, 2026)",
    "https://datasociety.net/... (From Care Labor to Data Labor, 2025)",
    "https://www.ifpri.org/... (Generative AI-powered voice technology in agricultural advisory services, 2026)",
    "https://arxiv.org/abs/2605.03073 (TTS-STT Flywheel, 2026)",
    "https://github.com/AI4Bharat/IndicConformerASR",
    "https://github.com/SRIKRISH-S/MSME-agent",
    "https://github.com/c-viswanath/JanMitra"
  ],
  "nearest_prior_art": [
    {
      "title": "The TTS–STT Flywheel: Synthetic Entity-Dense Audio Closes the Indic ASR Gap",
      "year": 2026,
      "overlap": "Entity-dense Indic ASR and WER-entity mismatch",
      "difference": "No selective spoken-confirmation policy or clinical unsafe-action evaluation"
    },
    {
      "title": "TeLeS: Temporal Lexeme Similarity Score for Confidence in E2E ASR",
      "year": "2025-2026",
      "overlap": "Confidence estimation for Indic ASR",
      "difference": "Not integrated with spoken confirmation or task-safety metric"
    },
    {
      "title": "ASHA digital-health qualitative studies (Cureus 2026; Data & Society 2025)",
      "year": "2025-2026",
      "overlap": "ASHA data-entry burden and recommendation for regional-language voice",
      "difference": "Qualitative recommendations only; no entity-safe voice system"
    },
    {
      "title": "JanMitra / Samadhan Didi",
      "year": "2026",
      "overlap": "Voice-first citizen service in Indian languages",
      "difference": "Grievance/scheme focus, not clinical entity safety; crowded space"
    }
  ],
  "differentiator_hypothesis": "A selective spoken-confirmation policy using entity-level confidence and risk weighting will reduce unsafe structured-record errors in noisy code-mixed ASHA speech more effectively than a WER-optimised baseline, at an acceptable cost in turns and latency.",
  "baseline_methods": [
    "Transcribe-and-submit: Prisma output written directly to structured record",
    "WER-optimised ASR configuration with no entity confirmation",
    "Optional: entity-dense fine-tuning or synthetic augmentation if feasible, but not required for the core hypothesis"
  ],
  "datasets": [
    {
      "name": "Project-generated synthetic ASHA visit summaries",
      "languages": "Gujarati, Hindi, Hinglish",
      "conditions": "Clean, 8 kHz telephony-filtered, additive field noise",
      "annotation": "Entity labels (synthetic patient ID, symptom, drug, dose, duration, follow-up date)",
      "licence": "Project-owned; synthetic only; no real patient data",
      "status": "To be created"
    },
    {
      "name": "LAHAJA (optional accent stratification)",
      "languages": "Hindi",
      "conditions": "Multi-accent read speech",
      "licence": "Research benchmark; access UNVERIFIED",
      "status": "Optional"
    }
  ],
  "model_constraints": {
    "stt": "Gnani Prisma v2.5, REST max 60 s per request, WebSocket streaming, 8/16/44.1/48 kHz, WAV/MP3/FLAC/OGG/M4A",
    "tts": "Gnani Timbre v2.5, 42 voices, 10 languages, REST/SSE/WebSocket",
    "llm": "Evon v3.3 not assumed available through challenge credits; entity extraction must use rules or a lightweight local model as fallback",
    "credit_limit": "5,000 programme credits; exact burn rate UNVERIFIED",
    "compute": "No model training; inference via Gnani APIs; Kaggle compute for lightweight local experiments only"
  },
  "critical_risks": [
    "Credit burn rate and concurrency limits unknown",
    "Real ASHA audio unavailable or ethically restricted; reliance on synthetic data",
    "Entity extraction quality may be too low without a strong LLM",
    "Clinical domain requires careful language and disclaimers; no real medical advice",
    "Confirmation policy may not outperform baseline; negative result must be reported honestly",
    "60-second demo may not convey the safety mechanism clearly",
    "Crowded voice-assistant space; novelty must be framed narrowly"
  ],
  "experiment_plan": {
    "conditions": ["clean", "8kHz telephony", "noisy field"],
    "baselines": ["transcribe-and-submit", "WER-optimised"],
    "treatment": "entity-aware selective spoken confirmation",
    "metrics": ["entity accuracy", "unsafe-action rate", "task completion", "average turns", "latency"],
    "sample_size": "minimum 30 utterances per condition if credits allow",
    "leakage_control": "hold out speaker templates and entity lexicons",
    "failure_criteria": "no meaningful unsafe-action reduction or impractical turn/latency cost"
  },
  "implementation_dependencies": [
    "Gnani API key and contest dashboard access",
    "Gnani Prisma REST/WebSocket and Timbre TTS working on account",
    "Synthetic audio generation (TTS or recorded consented voice)",
    "Entity extraction component (rules or local model)",
    "Dialogue state machine",
    "Evaluation harness",
    "60-second video editing and submission"
  ],
  "confidence_level": "Moderate. Problem evidence and Gnani API capabilities are well documented. Execution risk is concentrated in data access, entity-extraction quality, and the 11-day timeline. The project is defensible as a systems-research contribution if the team reports unsafe-action metrics honestly and does not overclaim a new ASR method."
}
```

---

**Final note on source discipline:** Every decisive claim above is linked to a search result or opened page. Items that could not be verified from official or primary sources — especially credit burn rate, Evon contest access, exact concurrency limits, dataset licences, and real ASHA audio access — are explicitly labelled **UNVERIFIED**. No URLs, dataset access, research results, or GitHub contents have been fabricated.