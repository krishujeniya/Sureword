# ADR 0007: Validate canonical PCM without transcoding

Date: 2026-11-06. Status: accepted.

The site verification repeatedly reproduced a 15-second ffmpeg startup timeout in the full audio lifecycle test, while later standalone conversion checks passed. The supplied WAV already met the format defined by ADR 0004.

Validate and return complete mono, 16-bit, target-rate PCM WAV directly. Enforce byte-size, minimum/maximum duration, and declared frame payload completeness before returning the original bytes and hash. All other formats retain the existing converter. This removes an unnecessary subprocess for already normalized input without weakening its format contract. Tradeoff: hashes preserve the original canonical container rather than a rewritten ffmpeg header. No change to audio privacy or provider selection.

Regression: `tests/unit/test_audio.py::test_canonical_wav_does_not_launch_converter` fails before the change and passes afterward. Full suite is reported separately in QA_REPORT.md. Browser microphone WebM still requires ffmpeg on the runtime.
