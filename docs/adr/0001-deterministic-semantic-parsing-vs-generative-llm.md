# ADR-0001: Deterministic Semantic Parsing vs. Generative LLM Extraction

**Date**: 2026-10-31  
**Status**: accepted  
**Deciders**: Krish Ujeniya  

## Context

Frontline healthcare documentation requires extracting four core entities (`person_name`, `age`, `village`, `visit_date`) from conversational Hindi-English speech transcribed by Gnani Prisma STT. In clinical contexts, mistranscribing a number or date (e.g., flipping an age from 45 to 15 or generating an impossible calendar date) has severe consequences. Many modern voice assistants default to passing transcripts to an unconstrained generative Large Language Model (LLM) or conversational agent for entity extraction.

However, in rural Indian healthcare settings, unconstrained LLMs introduce significant failure modes: stochastic token hallucinations (e.g., inventing medication names or altering patient demographics when uncertain), inference latencies exceeding 2–4 seconds on mobile edge connections, and unsustainable token costs for public health deployments.

## Decision

We decided to implement a zero-hallucination, deterministic semantic parser and normalizer ([`src/sureword/parser.py`](file:///home/ai/Documents/projects/Freelance/Sureword/src/sureword/parser.py)) using finite state regular automata, Devanagari digit converters, a comprehensive 1–100 Hindi numeral dictionary, physiological age bounds (1–120), and strict calendar date verification. Generative LLM extraction is explicitly rejected.

## Alternatives Considered

### Alternative 1: Cloud-Hosted Large Language Model (OpenAI GPT-4o / Gemini Flash)
- **Pros**: Handles arbitrary unstructured phrasing and grammatical variations effortlessly.
- **Cons**: High latency (1.5s–3.0s), recurring per-token API costs, external non-sovereign network dependencies, and stochastic hallucination risks on ambiguous speech.
- **Why not**: Generative models cannot guarantee 0% hallucination on patient entities; a deterministic parser provides 100% predictable, auditable behavior.

### Alternative 2: Local Open-Weight SLM (Evon v3.3 / Llama-3-8B / Phi-3)
- **Pros**: On-device sovereign processing without external cloud dependencies.
- **Cons**: Substantial memory footprint (>4GB VRAM), slow inference on frontline mobile hardware, and difficult edge deployment for ASHAs/ANMs.
- **Why not**: Over-engineering for a fixed 4-field extraction schema; official contest FAQ confirmed Evon is not hosted on the challenge API platform.

## Consequences

### Positive
- Sub-millisecond parsing execution latency (<2ms).
- Zero probability of hallucinated names, ages, or dates.
- Predictable handling of Devanagari numerals (`०-९`) and Hindi number words (*पैंतालीस* $\to 45$).
- Fully auditable and unit-testable extraction logic with 100% test coverage.

### Negative
- Grammar patterns and marker expressions must be explicitly maintained in code.
- Unanticipated regional slang or novel phrasing outside configured regexes requires gazetteer / pattern updates.

### Risks
- New dialectal phrasings could be tagged as `MISSING` rather than extracted. Mitigation: The risk-ranking clarification policy ($P$) catches missing fields and asks the user to repeat only that field.
