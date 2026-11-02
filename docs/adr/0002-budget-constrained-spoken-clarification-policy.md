# ADR-0002: Budget-Constrained Spoken Clarification Policy ($B \le 1.0$)

**Date**: 2026-10-31  
**Status**: accepted  
**Deciders**: Krish Ujeniya  

## Context

Frontline workers capturing clinical data under high noise and time pressure experience rapid dictation fatigue when forced to repeat entire sentences or confirm every individual field. Traditional voice agents either passively accept erroneous transcripts (causing silent data corruption) or engage in exhaustive confirmation dialogues (asking the user to confirm name, age, village, and date sequentially), causing users to abandon the voice interface entirely.

We need a clarification policy that minimizes critical-field errors while enforcing a strict cognitive dialogue budget.

## Decision

We decided to formulate the clarification interaction as a Budget-Constrained Risk Minimization Problem with an operational budget ceiling of $B \le 1.0$ prompt per visit record. The system evaluates entity uncertainty across missingness ($w_\text{miss}=0.5$), out-of-bounds physiological values ($w_\text{bound}=0.4$), and dictionary ambiguity ($w_\text{amb}=0.2$). If $\max R(k) \ge \tau$ ($\tau = 0.3$), Gnani Timbre synthesizes a targeted spoken prompt asking the worker to repeat *only* the single highest-risk field.

## Alternatives Considered

### Alternative 1: Passive Acceptance (Baseline $B_0$)
- **Pros**: Zero dialogue burden; fastest workflow.
- **Cons**: Silently commits mistranscribed names, ages, and dates (6.2% error in benchmark).
- **Why not**: Violates clinical safety and record integrity requirements.

### Alternative 2: Exhaustive Confirmation / Confirm-All (Baseline $B_3$)
- **Pros**: 100% record accuracy (0% error).
- **Cons**: Requires 4 prompts per form, creating unacceptable frontline friction and fatigue.
- **Why not**: Infeasible for community health workers visiting 20–30 households daily.

### Alternative 3: Random Field Clarification (Baseline $B_2$)
- **Pros**: Simple to implement.
- **Cons**: Wastes user effort on already correct fields without reducing error (6.2% error at 1 prompt/form).
- **Why not**: Empirical evaluation proved random selection yields 0% relative error reduction over raw ASR.

## Consequences

### Positive
- Achieves 50% relative reduction in accepted critical-field error (3.1% vs 6.2%).
- Elevates whole-record correctness from 75.0% to 87.5% at an exact dialogue cost of 1.0 prompt.
- Protects frontline workers from cognitive overload.

### Negative
- If multiple fields contain errors simultaneously, only the highest-risk field can be clarified within the 1-prompt budget.

### Risks
- An error could occur in a low-risk field while a harmless ambiguity exists in another field. Mitigation: Explicit human review gate (`READY_FOR_REVIEW`) allows the user to perform inline manual touchscreen corrections before final commit.
