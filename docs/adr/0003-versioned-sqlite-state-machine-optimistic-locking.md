# ADR-0003: Versioned SQLite State Machine with Optimistic Concurrency Control

**Date**: 2026-10-31  
**Status**: accepted  
**Deciders**: Krish Ujeniya  

## Context

Frontline mobile applications operate under intermittent cellular connectivity and concurrent user interactions. If a healthcare worker is editing a visit draft on a tablet while an asynchronous background speech transcription or clarification response returns, race conditions can silently overwrite manual corrections with stale ASR output. Furthermore, saving incomplete or unverified clinical records violates medical record governance.

## Decision

We decided to implement a transactional state machine in SQLite with optimistic concurrency control using monotonically increasing version counters ($V_t$). Every state transition requires matching the draft's expected version (`WHERE id = ? AND version = ?`). If a stale client or delayed response attempts an update, the database rejects the write and the API raises an explicit HTTP 409 Conflict. Additionally, drafts cannot transition to `COMMITTED` unless all four required fields are present, valid, and explicitly reviewed.

## Alternatives Considered

### Alternative 1: Distributed Key-Value Store / Redis with Pessimistic Locking
- **Pros**: Handles high distributed scale across multiple worker servers.
- **Cons**: Requires additional infrastructure daemons, increases operational overhead, and complicates local offline/edge tablet deployment.
- **Why not**: Over-engineering for single-worker frontline tablet sessions; SQLite provides zero-dependency, ACID-compliant local storage.

### Alternative 2: In-Memory Python Dictionary / Process State
- **Pros**: Fastest implementation.
- **Cons**: Process crashes lose in-flight drafts; no audit trail; unable to survive app restarts.
- **Why not**: Unacceptable for clinical records where data loss must be prevented.

## Consequences

### Positive
- Strict auditability: Every field update, speech turn, and status transition is recorded with millisecond timestamps.
- Zero lost updates: Conflicting or out-of-order writes fail safely with HTTP 409.
- Idempotent commits: Once committed, subsequent commit calls return the existing record without duplicating IDs.
- Zero external daemon dependencies; fully embedded and portable.

### Negative
- SQLite write locking is single-writer; however, for local and frontline microservices, write throughput far exceeds clinical visit frequencies.

### Risks
- Stale conflict (HTTP 409) requires the frontend client to reload latest state. Mitigation: Web UI automatically catches 409 and resynchronizes client state without discarding uncommitted input.
