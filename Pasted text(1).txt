Research Dossier: High-Impact AI Research Directions for the Great Indian AI Internship Challenge
Executive conclusion and assumptions
The strongest opportunity is not another multilingual assistant. India already has large-scale voice-first systems for agricultural advice, grievance filing and scheme discovery, including Kisan Sarathi, Kisan e-Mitra and the 2026 CPGRAMS “Samadhan Didi” system. 
 A project that merely connects speech recognition to RAG or an agent would therefore be difficult to defend as research differentiation.

The best research direction is instead a reliability layer for critical structured information spoken in Indian languages and code-mixed speech: when a frontline worker dictates a form, the system should detect which task-critical fields—names, ages, dates, quantities, locations, identifiers or measurements—are likely to have been mistranscribed, and selectively ask the speaker to repeat only those fields before committing them. A health-worker home-visit form is the strongest initial demonstration because Indian frontline health workflows already involve structured records and digital entry, while the proposed system would perform documentation rather than diagnosis or medical advice. The Ministry of Health's NCD workflow explicitly describes ASHAs maintaining field records and ANMs entering records on tablets, and acknowledges concerns about frontline-worker workload. 

The strongest runner-up is entity-safe noisy-telephony transcription for small-business/customer-service workflows, where the same selective-verification research can be tested on amounts, dates, product names and addresses. It is somewhat easier to demonstrate but less socially distinctive and sits closer to commercial ASR correction work already represented by RAGEC, DeRAGEC, RECOVER and Gnani's own key-term functionality. 

My confidence in the ranking is moderate-high, about 0.78. The core problem is well supported, the demo is feasible in the remaining contest window, and prior art leaves room for a systems-research contribution around task-critical selective verification rather than generic transcript correction. The principal uncertainty is Gnani API behaviour on the participant account: the official challenge material names Prisma v2.5 and Timbre v2.5, while Gnani publicly released Prisma v3.0 on 28 October 2026, only two days before this analysis. Whether v3.0 is enabled for the challenge account is therefore UNKNOWN until tested in the dashboard. 

This report treats the detailed uploaded research brief as the contest-specific specification, including the requirement to start from Indian problems, test prior art adversarially and distinguish systems integration from original research. 
 The remaining unspecified assumptions are: Krish is building solo; today's date is 30 October 2026; the prototype must be demonstrable by 10 November 2026; no paid-budget ceiling was specified in the conversational request, but the contest plan should remain viable using the 5,000 programme credits and ordinary student/Kaggle compute; and no access to private Gnani dashboard information is assumed.

Verified contest, platform and builder capability
Competition facts
The official Gnani challenge page says the Great Indian AI Internship Challenge runs under the theme “Build Sovereign AI for India”, started on 1 October 2026, closes at 11:59 PM IST on 10 November 2026, is open to enrolled students in India aged 18 or older, and permits solo entries or teams of two. Each registrant receives 5,000 programme credits, and a valid submission must contain a working application using at least one Gnani model/API plus a public LinkedIn/X demonstration. 

The same official material distinguishes internship selection from awards. Verified engagement on nominated posts determines the project shortlist; shortlisted people are then interviewed individually, and employment offers depend on those interviews. Separately, ten ₹50,000 awards recognise regional-language work, code-mixed speech, real-world impact, noisy telephony, solo/duo projects, creativity, Tier-2/Tier-3 builds, the 60-second demo and public voting. Purchased engagement, bots, paid promotion, engagement exchanges, plagiarism and misleading demonstrations are prohibited. 

Primary source: Gnani challenge page, official, live 2026, VERIFIED.
Primary source: Registration terms, official, 2026, VERIFIED.

Gnani technical reality
The challenge announcement names Prisma v2.5 for speech-to-text and Timbre v2.5 beta for text-to-speech on the programme API platform. It states that Evon v3.3 is not on the API platform and must instead be requested as open weights from Hugging Face. 

Prisma v2.5's public material describes support for Indian English, Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada, Malayalam, Punjabi and Odia, including code-switched speech and native 8-kHz telephony input. It also documents WebSocket streaming. These are vendor claims, not independently reproduced benchmark results. 

Gnani released Prisma v3.0 on 28 October 2026. Its public product documentation lists ten languages—English plus nine Indian languages—and adds four transcript modes, automatic language identification, up to 200 key terms, previous-context support, REST, WebSocket streaming and batch processing. The v3.0 documentation explicitly accepts native 8-kHz telephony and 16-kHz app/VoIP audio. 
 This should not be assumed available under contest credits merely because it exists publicly; the challenge's official model table still names v2.5. 

Timbre v2.5's public language pages show REST synthesis, a timbre-2.5 model identifier and a 48-kHz example request; Gnani markets support for Indian names, numerals and code-mixed text. Voice identities exposed to a particular participant are dashboard-dependent and therefore UNVERIFIED until the account is inspected. 

Evon v3.3's official Hugging Face model card states Apache-2.0 licensing, 30B total parameters with roughly 3.5B active per token, BF16 weights, 128K context and support for English plus ten Indic languages. The card lists NVIDIA H100 80GB, H200 and A100 as supported hardware and recommends tensor parallelism for longer contexts or higher concurrency. Running the full BF16 checkpoint on typical free Kaggle hardware is therefore not something the project should depend upon. 

Primary source: Evon v3.3 model card, Gnani/Hugging Face, August 2026, VERIFIED.
Verification status: model architecture/licence are verified from the model card; actual access approval and workable free-GPU deployment remain UNKNOWN.

Krish Ujeniya capability audit
Public evidence shows a substantial software-engineering base but much thinner direct speech-research evidence. GitHub lists 41 public repositories and a profile centred on RAG, agent systems and MLOps. His portfolio similarly describes Python, agentic systems, ML pipelines, OCR and software deployment work. These are self-published claims and should not be treated as independent proof of production performance. 

The strongest inspectable repository I found is Anchor, which contains executable workflow/state-management scripts, CI verification, TDD-oriented gates, rollback, drift checking, security checks, evaluation fixtures and chaos testing. That provides credible evidence of familiarity with deterministic verification, stateful agent workflows and engineering guardrails, even though README-reported benchmark claims such as “100% planning precision” should not be accepted without reproducing the experiment. 

I could not reliably locate public krishujeniya/Hadron or krishujeniya/Aegis repositories through indexed GitHub search. Results for those names largely resolved to unrelated owners, so any claim that those repositories demonstrate particular skills would be UNVERIFIED. The practical skill gap relevant to this contest is consequently clear: there is public evidence for reliable software/agent engineering, but I found no comparable public evidence of ASR model training, speech-dataset annotation, phonetic modelling, confidence calibration or statistically rigorous speech evaluation. 

That makes a project where the innovation lies in evaluation, confidence estimation, selective recovery and robust software integration around a strong commercial ASR, rather than training a new foundation speech model in eleven days, unusually well matched to the demonstrated skill profile.

India problem landscape and research-topic options
The discovery phase produces several genuine problems, but many superficially attractive ideas are already occupied by government or commercial systems.

Indian problem	Affected user and present failure	Voice necessity and evidence	Research judgement
Agricultural extension reach	Farmers need timely local advice; the Economic Survey says extension still faces limited reach, staff shortages and fragmented delivery. Kisan Call Centres handled 30.65 lakh calls in 2024-25.	Voice is already a major delivery channel, including Kisan Call Centres in 22 languages. 
Important, but a generic farmer assistant is weak novelty.
Farm schemes/advisories	Farmers need scheme, weather, mandi and expert information.	Kisan Sarathi already offers multilingual advice, expert calls and scheme discovery across 768 districts; Kisan e-Mitra had handled more than 95 lakh queries by March 2026. 
Reject generic voice-RAG. Research only reliability/escalation failures.
MSME delayed payments	Micro and small suppliers struggle with delayed receivables and must lodge cases through formal portals.	Voice could lower evidence-entry friction, but existing SAMADHAAN and CHAMPIONS already handle complaints/support. 
Retain only as structured-document capture, not grievance chatbot.
Informal-business transaction capture	Small businesses increasingly use digital payments but may still need lightweight bookkeeping/order capture.	Voice is valuable when owner/operators are handling customers or goods; this usage claim is a research hypothesis rather than established fact. MSME policy strongly promotes digital-payment adoption. 
Strong commercial demo, moderate research depth.
Frontline health documentation	ASHAs maintain field records while ANMs enter data digitally; government FAQs explicitly discuss perceived workload.	Hands-free structured dictation could reduce switching between patient interaction and data entry; necessity should be validated with users rather than assumed. 
Strongest research target if limited to documentation.
Citizen grievance filing	Citizens may struggle with forms, department selection and language.	Already directly addressed by CPGRAMS Samadhan Didi with speech, 22 scheduled languages and AI routing. 
Reject as negative control.
Unorganised/platform-worker safety reporting	India has a database exceeding 300 million unorganised workers; Labour Ministry reporting notes road safety, working hours and worker well-being as concerns for platform workers.	A voice incident log is plausible for workers operating on the move, but field evidence of demand would still be needed. 
Good public-interest idea, weaker accessible benchmark.
Disability-related digital exclusion	Government accessibility policy requires accessible ICT and sector-specific standards.	Speech can be an accessibility channel for some motor/visual impairments, though not universally; voice-only design would itself exclude some users. 
Worth studying, but user testing is difficult in 11 days.
Multilingual classroom participation	Government education material highlights India's extreme linguistic diversity and multilingual-education goals.	Oral assessment can capture learners who are more comfortable speaking than typing, but pedagogical validity would need serious study. 
Long-term education research; risky contest prototype.
Noisy contact-centre transcription	Indian calls include code-switching, accents, compression and background noise; Gnani itself positions telephony as a core ASR challenge.	Voice is intrinsic, not decorative. 
Excellent engineering/research benchmark, less distinctive social story.
Accent/dialect disparity	Research on Hindi accents and broader Indic varieties finds substantial variation and named-entity/specialised-term difficulty.	The problem exists in speech itself. LAHAJA spans 132 speakers/83 districts; 2026 dialect research reports transfer problems on noisy, spontaneous Indic varieties. 
Strong technical research topic.
Critical entities lost despite acceptable WER	Names, organisations, dates and numbers can be wrong even when overall transcripts look reasonable.	This is intrinsically speech-specific and directly affects downstream actions. Recent Indic benchmarking and broader ASR research both document the gap. 
Highest-value cross-domain technical gap.

From that landscape, eight viable research programmes emerge. These also satisfy the broader requirement for options spanning health, business, technology, policy, environment and education.

Research option	Rationale	Three central research questions	Methods and primary sources	Timeframe, deliverables and resources
Critical-field selective verification for frontline health forms	Converts ASR reliability into a measurable public-service workflow rather than a chatbot.	Can entity-level risk predict wrong fields? Can selective re-prompts cut critical errors without excessive dialogue? Does it remain robust under code-mix/noise?	Literature review; consented/synthetic form recordings; Gnani + IndicConformer baselines; ablations. Primary sources: MoHFW, AI4Bharat, Gnani.	Short: working demo + 100–300 utterance evaluation. Medium: multi-language benchmark. Long: field study. Needs API credits, Python, annotation, optional Kaggle GPU.
Entity-safe MSME voice order/invoice capture	Amounts, dates, product names and addresses are directly measurable.	Which entity classes dominate failure? Does schema-aware verification outperform transcript correction? What latency/confirmation burden is acceptable?	Call simulations, noisy recordings, structured-field metrics, user interviews.	Short: order capture demo. Medium: business-domain corpus. Long: real deployment. Needs synthetic catalogue, speech API, frontend.
Noisy telephony selective repair	Gnani's strongest native domain and a contest award category.	When should the system accept, correct or re-ask? Does acoustic/noise context improve calibration? Can critical-field error fall without hurting latency?	Benchmark APIs/open ASR; real codec transformations; calibration and risk-coverage curves.	Short: benchmark/demo. Medium: learnt confidence model. Long: carrier/contact-centre trial. Needs audio tooling and API credits.
Accent/dialect fairness auditor for Indian ASR	Aggregate WER conceals demographic and regional failure modes.	Which accents/entities cause disproportionate errors? Can uncertainty identify under-served speech? Are vendor rankings stable across accents?	LAHAJA/Svarah/IndicVoices analysis; stratified statistics; robustness testing.	Short: dashboard + benchmark. Medium: expanded languages. Long: publishable audit. Needs datasets and moderate inference compute.
Worker-safety voice incident capture	Hands-busy workers need fast incident recording and structured extraction.	Does voice improve completion? Which safety entities are misrecognised? Can confirmation prevent unsafe records?	Worker interviews, simulated incidents, field-noise tests, case studies.	Short: controlled demo. Medium: pilot. Long: occupational-safety study. Needs domain expert and consented audio.
Voice-based vocational oral assessment	Tests practical spoken reasoning rather than typed literacy.	Can scoring be separated from ASR errors? Are accent/language effects fair? Does confidence-aware replay improve validity?	Education literature, rubric-based annotation, inter-rater analysis, ASR fairness analysis.	Short: assessment prototype. Medium: controlled study. Long: educational validation. Needs teachers/assessors and labelled responses.
Farmer-query uncertainty triage	Existing farmer services make “answer generation” unoriginal, but safe escalation remains useful.	Can the system detect ambiguous or poorly recognised queries? When should it route to an expert? Does uncertainty correlate with task resolution?	Kisan-service analysis, simulated calls, classification/abstention experiments.	Short: triage demo. Medium: farmer recordings. Long: KVK partnership. Needs agricultural expert and speech data.
Accessible voice navigation of public digital services	Accessibility standards create a concrete policy need.	Which navigation tasks are hardest? Does multimodal voice reduce task failure? How should low-confidence speech be recovered accessibly?	Accessibility review, usability tests, task-completion metrics.	Short: prototype. Medium: disability user study. Long: government-service pilot. Needs accessibility expertise and representative participants.

The two best choices are therefore frontline critical-field voice documentation and noisy telephony selective repair. The first has the stronger Indian public-interest story and clearer non-chatbot identity; the second offers easier benchmarking and closer alignment to Gnani's core product domain.

Prior art, datasets and novelty boundary
What is already established
Code-switching ASR is an active, mature research area rather than an open blank slate. A 2026 systematic review documents extensive end-to-end code-switch ASR work, while recent Indic studies investigate Hindi-English adaptation, spontaneous/disfluent speech and dialect transfer. 
 Consequently, “we support Hinglish” is not a research contribution.

Named-entity preservation is also already recognised as a distinct ASR problem. The 2026 Indic named-entity stress-test repository evaluates Hindi and Telugu specifically using entity precision, recall and F1 rather than WER alone. AI4Bharat's 2026 IndicContextEval reports a standalone IndicConformer baseline of 18.81% WER but 29.58% named-entity error rate on its benchmark, illustrating why aggregate WER can hide high-value semantic failures. 

Post-ASR entity correction is likewise established. RAGEC retrieves candidate entities for LLM correction; DeRAGEC denoises candidate retrieval; the October 2026 RECOVER paper uses multiple ASR hypotheses, retrieval, deterministic guardrails and an LLM critic. 
 A project that merely applies RAG to a product-name list would therefore have weak novelty.

Confidence estimation and abstention are established research areas too. Recent work studies word-level confidence estimation, noisy-speech overconfidence, confidence-guided error correction and explicit ASR abstention. 
 The defensible opportunity is not to claim invention of uncertainty, but to test a new task-level formulation in Indian code-mixed structured voice workflows.

Closest prior-art matrix
Candidate	Closest prior art	What prior art demonstrates	Gap that remains defensible
Frontline critical-field verification	Indic named-entity stress test; IndicContextEval; RAGEC/RECOVER; confidence-estimation literature	Entities fail disproportionately; contextual prompts can help; retrieval/correction and confidence models can repair errors. 
Little evidence found for field-level utility-weighted selective re-asking in Indian code-mixed structured forms, optimised jointly for critical-field accuracy and user re-prompt burden. This is a potential research gap, not an originality guarantee.
Noisy-telephony selective repair	Noisy calibration, Prisma, RECOVER	Noise increases overconfidence; entity recovery and contextual biasing are active areas. 
Domain-specific risk/coverage optimisation across Indian telephony codecs and critical entity classes remains a reasonable systems-research question.
Farmer-query uncertainty triage	Kisan Sarathi/e-Mitra, code-switch ASR, abstention work	Voice advisory infrastructure already exists; abstention is known. 
Research would have to centre on measurable escalation quality, not advisory generation. Real farmer data access is the blocker.

Selected research-paper bibliography
The most decision-relevant papers are:

Agro et al., “Code-Switching in End-to-End Automatic Speech Recognition: A Systematic Literature Review,” LREC 2026 — maps current code-switch ASR methods and gaps. ACL Anthology 
Dhasmana et al., “Dialect Matters: Cross-Lingual ASR Transfer for Low-Resource Indic Language Varieties,” VarDial 2026 — spontaneous/noisy/code-mixed Indic dialect evaluation. ACL Anthology 
Biswas et al., Hindi-English code-mix Whisper adaptation, Interspeech 2025. ISCA 
Mitra et al., Bengali-English/Hindi-English code-mixed disfluent speech, 2026. ACL 
Pusateri et al., “Retrieval Augmented Correction of Named Entity Speech Recognition Errors,” 2024. arXiv 
Im et al., “DeRAGEC,” ACL Findings 2025. ACL 
Kumar & Sachdeva, “RECOVER,” EMNLP Industry 2026. ACL 
Ravi et al., ASR Confidence Estimation using True Class Lexical Similarity Score, Interspeech 2025. ISCA 
Naowarat et al., Word-level Confidence Estimation for CTC Models, Interspeech 2023. ISCA 
Shu et al., Confidence- and acoustic-reference ASR error correction, Interspeech 2024. ISCA 
“Identifying and Calibrating Overconfidence in Noisy Speech Recognition,” ASRU 2025. IEEE DOI 
Huang et al., “RAS: a Reliability Oriented Metric for Automatic Speech Recognition,” 2026. arXiv 
Istaiteh et al., “What WER Hides,” ArabicNLP 2026 — especially useful as a methodological warning because fewer than half of named entities were preserved in its best code-switched setting. ACL 
Directly relevant repositories
A minimum viable prior-art sweep should include these genuine repositories:

AI4Bharat/IndicConformerASR — MIT-licensed 22-language ASR. 

AI4Bharat/IndicVoices — large-scale natural Indic speech collection. 

AI4Bharat/IndicContextEval — context/entity-aware AudioLLM benchmark, CC BY 4.0. 

AI4Bharat/IndicSUPERB — speech-understanding benchmark and Kathbath data. 

AI4Bharat/IndicWav2Vec — older multilingual Indic speech representation work. 

AI4Bharat/Lahaja — Hindi multi-accent benchmark. 

AI4Bharat/Svarah — Indian-accented English benchmark. 

AI4Bharat/Vimarsha — recent work on more faithful Indian-language ASR evaluation. 

Sankeertanaaa/Stress-testing-ASR-models-on-Named-Entities-in-Indic-Languages — direct negative control for any claim that entity-aware ASR evaluation is new. 

Nagarathna-R/2026_RanDiS_Interspeech — recent confidence-estimation implementation with a Hindi pipeline. 

Open-Speech-EkStep/vakyansh-models — older open Indic ASR/TTS baselines. 

c-viswanath/JanMitra — important negative control showing that voice-first multilingual government-service agents are already implemented prototypes. 

Garidepallisahithi/shudh-asr — retrieval-grounded post-ASR correction for code-switched Indian speech, another novelty warning. 

Dataset and access verification
Dataset/source	Relevant content	Licence/access status	Use in this project
IndicContextEval	56 h, 555 speakers, 8 Indic languages, 23 domains, transcripts with entity forms	CC BY 4.0, downloadable via Hugging Face according to repository. 
Best ready-made entity/context evaluation source.
IndicVoices	About 12,000 h, 22 languages, 22,563 speakers, natural/read/extempore/conversational speech	Public project; exact subset/use terms must be checked before sending audio to any third-party API. 
Sample carefully; do not bulk-upload without licence/privacy verification.
IndicSUPERB/Kathbath	About 1,684 h labelled speech across 12 languages, with clean/noisy test material	Repository states broad copyright waiver for IndicSUPERB; individual underlying-resource terms should still be checked. 
Robustness baseline.
LAHAJA	12.5 h Hindi, 132 speakers, 83 districts, read/extempore speech and demographic metadata	Public dataset link; licence was not explicit in the indexed README I inspected: LICENCE UNVERIFIED. 
Accent robustness if licence permits API processing.
Svarah	9.6 h Indian English, 117 speakers, 65 districts/19 states	Public benchmark; exact dataset licence not exposed in the indexed README snippet: LICENCE UNVERIFIED. 
Indian-accent comparison.
Small consented contest set	100–300 utterances recorded by builder/volunteers with synthetic identities and fictional form values	Builder-controlled consent and licence	Most defensible contest evaluation because labels and consent can be audited.
Prisma API outputs	Participant-generated inference results	Governed by challenge/API terms; dashboard conditions must be checked	Required Gnani experimental arm.

For the contest demo, the safest data design is a small, consented evaluation set with synthetic names/IDs. Splits should be speaker-disjoint, and template prompts should also be split so the test set does not consist of memorised form sentences. Real Aadhaar, PAN, account numbers, telephone records or patient identifiers should not appear. The Gnani challenge page itself warns participants against putting real phone numbers, account numbers, Aadhaar, PAN or recorded calls into demos. 

Decision matrix, scoring and adversarial audit
General research-option matrix
Scores use 1–5, where higher impact/feasibility/novelty is better and higher resource intensity is worse.

Topic	Impact	Feasibility	Novelty potential	Resource intensity
Critical-field frontline documentation	5	5	4	2
Noisy telephony selective repair	4	5	3	2
Accent/dialect ASR auditor	4	5	3	2
MSME order/invoice capture	4	5	3	2
Worker-safety voice incident capture	4	3	4	3
Farmer-query uncertainty triage	5	3	2	3
Accessible voice public-service navigation	5	3	3	4
Vocational oral assessment	4	3	4	4

The top two remain frontline documentation and telephony repair because both can be independently tested in eleven days, force Gnani speech models into the core causal path, support measurable speech research, and yield a visible before/after demonstration without pretending that RAG or an agent shell is novel.

Contest-specific weighted scoring
Using the requested 100-point rubric:

Criterion	Weight	Frontline critical-field verification	Noisy telephony entity repair	Farmer uncertainty triage
Indian problem severity/specificity	18	16	13	17
Gnani necessity	15	14	15	13
Technical differentiation/research	18	15	14	10
Probability functioning by deadline	15	14	15	10
60-sec demo clarity	12	11	11	9
Engineering/interview depth	10	9	9	8
Data/compute affordability	5	5	5	3
Public-interest/communication	7	7	5	7
Total	100	91	87	77

These scores are judgement estimates, not measured contest outcomes.

Hostile review of the winning idea
A skeptical speech scientist could reject the project if the “uncertainty detector” is merely an arbitrary confidence threshold. The response must be experimental: compare at least a fixed threshold, transcript-disagreement baseline and a learned/entity-aware risk model, and plot critical-field error versus re-prompt rate.

A skeptical PhD reviewer could reject a claim of novelty because confidence estimation, named-entity correction, contextual biasing and abstention are already published. 
 The thesis must therefore be narrow: utility-weighted selective verification for structured Indian code-mixed voice tasks, not “a new method for ASR uncertainty”.

A skeptical Gnani engineer could ask why Prisma's key-term prompting or new v3 contextual features do not already solve the problem. Prisma v3.0 publicly offers up to 200 key terms and context. 
 The project therefore needs adversarial conditions where contextual biasing still produces uncertain or wrong critical fields and must show that the verification layer adds value rather than duplicating the recogniser.

A skeptical contest judge could ask whether the app works without voice. A typed form obviously does. The correct answer is that the research target is hands-free, eyes-free field capture under speech-specific errors, and the demonstration must visibly compare speech acceptance versus selective recovery; otherwise voice becomes decoration.

A skeptical recruiter could reject an over-engineered research prototype with no working end-to-end flow. Anchor suggests Krish is already comfortable with software verification and stateful workflows, so the project should spend less time on agent orchestration and more on speech evaluation, annotation quality and reproducibility. 

The strongest rival submission would probably be a polished Hinglish/Tanglish real-time telephony agent using Prisma and Timbre with excellent UX. The recommended project beats that only if its 60-second video demonstrates an unmistakable failure that the baseline accepts and the research layer correctly catches.

Final research thesis, architecture and deadline feasibility
Final problem statement
Named user: an ASHA or comparable frontline field worker completing a structured household/home-visit record while interacting with a beneficiary.

Observed workflow: the worker currently gathers structured information and maintains records; in the NCD programme, the official workflow assigns ASHAs family-folder/register work and ANMs tablet entry. 

Problem: conventional speech-to-text can produce a transcript that appears broadly correct while corrupting the one field that drives the record—an age, person name, date, village, measurement or other critical entity. Named-entity research and recent Indic benchmarks show that these failures are not adequately represented by aggregate WER. 

System objective: accept spoken form entries through Gnani Prisma, map the transcript into a typed schema, estimate risk independently for each critical field, and use Timbre to request a focused confirmation only for fields whose expected error cost exceeds a threshold.

Proposed research thesis
Untested hypothesis: A task-aware selective-verification policy combining entity type, cross-hypothesis disagreement, schema constraints and recognition/context signals will reduce critical-field error at a fixed confirmation budget more than transcript-level confidence thresholds or generic LLM correction on noisy, code-mixed Indian speech.

That is falsifiable. If the proposed method does not lower critical-field error at matched re-prompt rate relative to the baselines, the hypothesis fails.

The classification of contribution should be kept explicit:

Established technical capability: Indian-language ASR, contextual biasing, confidence estimation, entity correction and TTS. 

New system integration: Prisma → schema extraction → entity-risk layer → selective Timbre confirmation.
Potentially new method: utility-weighted field-level risk scoring under Indian code-mixed/noisy speech.
Demonstrated original research contribution: only claimable after experiments show a reproducible improvement over appropriate baselines; it must not be claimed in advance.

Minimum architecture
A practical eleven-day stack is:

Microphone / uploaded sample → Prisma STT → structured field extractor → per-field risk scorer → accept OR targeted re-ask → Timbre TTS → corrected structured record → audit trace

The critical engineering feature is that no LLM is allowed to silently invent or overwrite a critical field. Corrections should either be supported by a constrained candidate set/schema or explicitly confirmed by the speaker.

Evon should be optional rather than a dependency. Its official card describes a 30B BF16 model and H100/H200/A100 deployment targets; the challenge page says Evon is not hosted under programme API credits. 
 A smaller open model or deterministic parser is sufficient for schema extraction during the contest.

Baselines and ablations
The simplest valid baseline is Prisma's first transcript followed by deterministic schema extraction with no verification.

The strong baseline is Prisma plus all available supported contextual/key-term mechanisms, followed by a global confidence or heuristic threshold. If v3.0 is unavailable, use the strongest documented v2.5 settings and record that limitation.

A third baseline should be generic post-ASR LLM correction with the same entity list, because RAGEC/RECOVER-like methods are the most obvious competitor. 

Ablations should remove, one at a time: entity type weighting; schema validation; hypothesis disagreement; noise features; and domain/entity context. If the full method beats baselines but collapses when a component is removed, the experiment begins to support a causal contribution.

Metrics
Do not optimise only WER. Report critical-field exact-match accuracy, entity recall/F1, numeric/date exact match, slot error rate, unsafe-accept rate, false-reprompt rate, task completion, mean re-prompts per form, latency, and a risk–coverage curve showing error as increasingly uncertain fields are rejected. The rationale for beyond-WER metrics is well supported by recent entity-focused and reliability-oriented ASR research. 

A useful primary metric is:

Critical Error Rate among Accepted Fields = wrong critical fields accepted without confirmation / all accepted critical fields.

The contest success criterion should be pre-registered, for example: at the same confirmation budget, the proposed policy must lower critical-field error versus the strongest heuristic baseline. The exact numerical threshold should be chosen before seeing test results; no benchmark result should be invented now.

Eleven-day execution
The research is feasible because it does not require speech-model training. Days 1–2 should test the actual Gnani account, freeze API/model availability and construct the synthetic form schema. Days 2–4 should record a small speaker-disjoint corpus in Hindi/Gujarati/English code-mix and multiple noise conditions. Days 4–6 should build the baselines and entity metrics. Days 6–8 should implement the risk policy and ablations. Days 8–9 should run frozen-test evaluation. Days 9–10 should harden latency/failure handling and prepare the 60-second demo. Day 11 should be reserved for reproduction, submission assets and a final no-fabrication audit.

The minimum 60-second demonstration is unusually clear: first show a noisy/code-mixed utterance with a fictional but critical field; show the raw recogniser output accepting an incorrect value; then run the same task through the proposed system; show the exact field highlighted as risky; play Timbre's short confirmation prompt; speak the corrected field; and display the final structured record plus a tiny “baseline vs selective verification” metric card. The demo should use only synthetic identifiers and consented voices, consistent with the contest's privacy instructions. 

Fallback if the hypothesis fails
If learned/selective scoring does not beat simple rules, the project remains valuable as a rigorous benchmark and reliability harness for Gnani on task-critical Indian entities. That is a systems-research contribution rather than a novel algorithm: release the test protocol, entity taxonomy, risk curves, noisy/code-mixed synthetic benchmark generator and reproducible evaluation runner. This is much more defensible than hiding a negative experiment behind a prettier agent UI.

The unresolved factual questions that must be settled by dashboard/API testing are: whether challenge keys currently expose Prisma v2.5, v3.0 or both; whether confidence/token-level metadata are returned; whether N-best hypotheses are available; exact streaming audio encodings and session limits; actual Timbre voices/languages exposed to the account; credit accounting for STT versus TTS; retry/rate-limit error shapes; whether v3 key-term prompting works under programme credits; whether v3 Auto-LID and output modes are exposed; and whether Evon weights have actually been approved for Krish's Hugging Face account. Public documentation does not establish these account-specific facts. 

Research programme, visualisations and machine-readable handoff
For a post-contest three-month research extension, the milestones should separate problem validation, dataset construction, baseline reproduction, method development and frozen evaluation rather than allowing the demo application to become the experiment.

22 Nov
29 Nov
06 Dec
13 Dec
20 Dec
27 Dec
03 Jan
10 Jan
17 Jan
24 Jan
31 Jan
07 Feb
14 Feb
User interviews and task analysis
Consent and recording protocol
Pre-register metrics and failure rules
Multi-speaker data collection
Independent annotation and QA
Reproduce baselines
Risk model and selective policy
Ablations and calibration
Frozen test evaluation
Error analysis and robustness tests
Paper-style report and release package
Problem and protocol
Data
Modelling
Evaluation
Three-Month Critical-Field Speech Reliability Study


Show code
The most useful visualisations would be a risk–coverage curve for accepted-field error versus percentage of fields auto-accepted; grouped bars for entity accuracy by type and language; a calibration/reliability diagram; a confusion matrix for numeric/date/name errors; a box plot of latency across pipeline stages; a Sankey or state diagram for accept → re-prompt → corrected/failed outcomes; and a heat map of errors across clean, street-noise and telephony conditions. For the contest video, however, a single side-by-side “baseline accepted wrong field / proposed system caught it” panel is more communicative than a research dashboard.

A reusable project-plan template is: define one falsifiable hypothesis and freeze primary/secondary metrics; establish data rights and consent; create train/dev/test splits with speaker and prompt isolation; reproduce the simplest and strongest baselines; implement one minimal new component; run ablations; freeze the test set before tuning; analyse failures by language/entity/noise; record latency and cost; reproduce the complete run from a clean environment; and explicitly document negative results. Principal risks are API instability, undocumented confidence signals, insufficient natural code-mixed data, overfitting to synthetic prompts, LLM “corrections” that hallucinate entities, and overclaiming novelty. Mitigation is respectively an adapter layer around the API, signal-agnostic disagreement features, a small consented real-speech set, prompt/speaker-disjoint splits, constrained confirmation rather than silent correction, and conservative research language anchored to the prior-art matrix.

ASTRA_RESEARCH_HANDOFF
yaml
Copy
chosen_problem:
  title: "Selective verification of task-critical fields in Indian code-mixed voice form entry"
  primary_user: "ASHA or comparable frontline field worker completing structured records"
  core_failure: >
    A broadly correct ASR transcript can contain an incorrect critical entity
    such as a name, age, date, quantity, location or identifier, and downstream
    software may commit that value without knowing it is wrong.

evidence_sources:
  - source: "MoHFW NCD programme FAQ"
    url: "https://ncd-prestaging.mohfw.gov.in/ncdlandingassets/faqs.html"
    status: "VERIFIED official source"
  - source: "Gnani Great Indian AI Internship Challenge"
    url: "https://www.gnani.ai/internship"
    status: "VERIFIED official source"
  - source: "Gnani Prisma v3.0"
    url: "https://www.gnani.ai/resources/prisma-v3"
    status: "VERIFIED public product documentation; challenge-account availability UNKNOWN"
  - source: "IndicContextEval"
    url: "https://github.com/AI4Bharat/IndicContextEval"
    status: "VERIFIED repository"
  - source: "Indic named-entity ASR stress test"
    url: "https://github.com/Sankeertanaaa/Stress-testing-ASR-models-on-Named-Entities-in-Indic-Languages"
    status: "VERIFIED repository"

nearest_prior_art:
  - "Retrieval Augmented Correction of Named Entity Speech Recognition Errors (2024)"
  - "DeRAGEC (ACL Findings 2025)"
  - "RECOVER (EMNLP Industry 2026)"
  - "IndicContextEval (Interspeech 2026)"
  - "ASR confidence-estimation and abstention literature"

differentiator_hypothesis: >
  A utility-weighted field-level selective verification policy combining
  entity type, schema constraints and recognition/disagreement signals will
  reduce critical-field error at a fixed re-prompt budget relative to
  transcript-level thresholds and generic post-ASR correction on noisy,
  code-mixed Indian speech.

baseline_methods:
  - "Prisma transcript + deterministic schema extraction, no verification"
  - "Prisma + strongest available contextual/key-term options + global threshold"
  - "Generic LLM post-ASR correction using the same entity/context list"

datasets:
  contest:
    - "100-300 consented, synthetic-identity utterances recorded by builder/volunteers"
  external_candidates:
    - "IndicContextEval, CC BY 4.0"
    - "IndicVoices, rights for third-party API processing must be rechecked"
    - "IndicSUPERB/Kathbath"
    - "LAHAJA, licence must be verified before API use"
    - "Svarah, licence must be verified before API use"

model_constraints:
  mandatory:
    - "Gnani Prisma STT"
    - "Gnani Timbre TTS for selective confirmations"
  optional:
    - "Small local/open LLM for schema extraction"
  avoid_dependency:
    - "Evon v3.3: 30B BF16; not on challenge API platform and free-GPU feasibility is poor"
  unknown_until_dashboard_test:
    - "Prisma v3.0 programme availability"
    - "token/word confidence availability"
    - "N-best hypotheses"
    - "Timbre voice inventory"
    - "rate limits and credit accounting"

critical_risks:
  - "Novelty collapses into ordinary confidence thresholding"
  - "Prisma v3 contextual features already solve easy examples"
  - "Synthetic data does not represent spontaneous field speech"
  - "LLM silently changes valid entities"
  - "Too many re-prompts destroy usability"
  - "Health framing drifts into unsafe clinical advice"
  - "Demo overstates research results"

experiment_plan:
  primary_metric: "critical-field error among automatically accepted fields"
  secondary_metrics:
    - "entity exact match / F1"
    - "slot error rate"
    - "unsafe accept rate"
    - "false re-prompt rate"
    - "mean confirmations per form"
    - "task completion"
    - "latency"
    - "risk-coverage curve"
  required_ablations:
    - "remove entity-type weighting"
    - "remove schema constraints"
    - "remove disagreement signal"
    - "remove contextual/entity list"
    - "clean vs noisy vs telephony-like audio"
  split_policy: "speaker-disjoint and prompt/template-disjoint test set"
  failure_rule: >
    If the proposed policy does not outperform the strongest baseline at a
    matched re-prompt budget on the frozen test set, do not claim a new method.

implementation_dependencies:
  - "Gnani challenge API key and credits"
  - "Python/FastAPI or equivalent backend"
  - "Browser microphone interface"
  - "audio conversion/resampling utilities"
  - "structured schema validator"
  - "evaluation harness with reproducible manifests"
  - "consent and annotation protocol"
  - "simple result visualisation"
  - "public 60-second demo with synthetic identifiers only"

confidence_level: 0.78
The recommendation is therefore deliberately narrower than a typical hackathon assistant: research whether an Indian voice system can know when a critical spoken field is unsafe to trust, and prove it with controlled experiments. That problem makes Gnani's speech stack causally necessary, aligns with real Indian field workflows, has a highly legible one-minute demonstration, and remains scientifically defensible even if the eventual contribution turns out to be a rigorous systems study rather than a novel speech algorithm. 