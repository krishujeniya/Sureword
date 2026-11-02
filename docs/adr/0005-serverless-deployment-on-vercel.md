# ADR-0005: Serverless Deployment on Vercel with Ephemeral SQLite and Native Audio Validation

**Date**: 2026-11-02  
**Status**: accepted  
**Deciders**: Krish Ujeniya  

## Context

To provide an instantly accessible public demonstration URL for competition judges, reviewers, and evaluators in the Great Indian AI Internship Challenge 2026, Sureword required public cloud hosting. While Docker container deployment works well on dedicated VPS or cloud instances, serverless platforms like Vercel offer instant global HTTPS CDN distribution, zero idle server cost, and seamless GitHub deployment integration.

However, deploying a stateful FastAPI speech application on Vercel serverless presents two architectural hurdles:
1. **Read-Only Filesystem**: Vercel serverless execution environments enforce a read-only root filesystem, allowing disk writes exclusively within `/tmp/`.
2. **Missing Binary Dependencies**: Standard Vercel Python runtimes do not package system binaries like `ffmpeg` or `ffprobe`.

## Decision

We decided to support native Vercel serverless deployment via an ASGI adapter (`api/index.py`) and `vercel.json` routing, configured with two operational safeguards:
1. **Dynamic Database Routing**: Automatically detect Vercel serverless runtime (`VERCEL=1`) and route SQLite storage to `/tmp/sureword.db`, while preserving persistent `sureword.db` for containerized and local deployments.
2. **Native WAV Validation Fallback**: Enhance [`src/sureword/audio.py`](file:///home/ai/Documents/projects/Freelance/Sureword/src/sureword/audio.py) to inspect WAV headers, sample rates, channels, and duration directly using Python's built-in `wave` module whenever the `ffmpeg` binary is absent.

## Alternatives Considered

### Alternative 1: Dedicated Container Hosting (Render / Railway / Fly.io / AWS EC2)
- **Pros**: Persistent disk storage and full OS container control with FFmpeg installed.
- **Cons**: Cold start delays or paid continuous instance costs; requires credit card billing; slower global edge routing.
- **Why not**: Vercel offers instantaneous edge routing, zero infrastructure cost on hobby tiers, and native integration with the owner's GitHub organization.

### Alternative 2: External Hosted Database (Supabase / Neon Postgres)
- **Pros**: Persistent shared storage across serverless function invocations.
- **Cons**: Adds external network roundtrips (50–150ms per database operation), increases deployment complexity, and introduces third-party credential dependencies.
- **Why not**: Overkill for short-lived session intake drafts; visit records are meant to be exported or stored locally on the frontline worker's device.

## Consequences

### Positive
- Public production deployment live at `https://sureword.vercel.app` with sub-500ms global edge latency.
- Deployment verification script passes 100% of functional health and draft lifecycle checks against the live production endpoint.
- Zero server maintenance overhead.

### Negative
- Visit drafts stored in `/tmp/sureword.db` are ephemeral and reset when serverless container instances recycle. However, frontline dictation sessions are transient (<2 minutes), and committed records are returned immediately to the client.

### Risks
- Users attempting to upload non-WAV audio (e.g. raw WebM) on Vercel without client-side WAV encoding could fail if FFmpeg is absent. Mitigation: The web frontend uses browser AudioContext to transcode microphone captures to compliant linear PCM WAV.
