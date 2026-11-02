# ADR-0004: Server-Side Audio Processing and Normalization Pipeline

**Date**: 2026-10-31  
**Status**: accepted  
**Deciders**: Krish Ujeniya  

## Context

Frontline speech is captured across heterogeneous mobile hardware (Android smartphones, low-cost tablets, laptops) via browser `MediaRecorder` APIs. Browsers produce varied container formats (WebM/Opus, OGG, MP4/AAC) with disparate sample rates (44.1kHz, 48kHz), variable bitrates, and stereo channels. Sending unnormalized or malformed audio directly to Gnani Prisma STT causes format rejection, unnecessary bandwidth consumption, or acoustic degradation.

Moreover, unvalidated audio uploads expose the server to denial-of-service (DoS) via massive files or infinite streams.

## Decision

We decided to establish a strict server-side audio validation and normalization boundary using an asynchronous FFmpeg pipeline ([`src/sureword/audio.py`](file:///home/ai/Documents/projects/Freelance/Sureword/src/sureword/audio.py)):
1. **Size Boundary**: Reject any upload exceeding 10 MB with HTTP 413.
2. **Duration Boundary**: Enforce audio length bounds ($0.2\text{s} \le \text{duration} \le 20.0\text{s}$).
3. **Format Standardization**: Transcode incoming audio into standardized single-channel, 16 kHz, 16-bit linear PCM WAV.
4. **Audit Fingerprinting**: Generate a cryptographic SHA-256 digest of every audio payload for data provenance.
5. **Subprocess Hardening**: Execute FFmpeg with `-nostdin` and `stdin=subprocess.DEVNULL` to prevent terminal hanging or blocking.

## Alternatives Considered

### Alternative 1: Client-Side Audio Resampling via WebAssembly / AudioWorklet
- **Pros**: Reduces server CPU workload; sends pre-converted WAV from the browser.
- **Cons**: High memory and CPU overhead on low-end Android mobile devices; inconsistent WebAudio browser implementations.
- **Why not**: Battery life and browser stability on frontline rural tablets are critical constraints; server-side conversion is vastly faster and more reliable.

### Alternative 2: Direct Passthrough of WebM to Gnani REST Endpoint
- **Pros**: Zero local server transcoding.
- **Cons**: Gnani REST API specifications strictly recommend 16kHz mono WAV for optimal acoustic feature extraction and lowest latency; uncompressed/malformed audio risks provider timeouts.
- **Why not**: Sub-second latency and acoustic accuracy require compliant 16kHz WAV format.

## Consequences

### Positive
- Consistent acoustic input guaranteed for Gnani Prisma STT across all client browsers and operating systems.
- Robust DoS protection through upload size and duration gating.
- Full cryptographic traceability of every spoken dictation.

### Negative
- Requires `ffmpeg` binary installed in deployment environment (containerized via `Dockerfile`).

### Risks
- FFmpeg process hang on corrupted audio streams. Mitigation: Explicit `timeout=10` parameter in `subprocess.run` terminates runaway processes immediately.
