#!/usr/bin/env python3
"""Smoke test script for live Gnani Prisma STT and Timbre TTS verification.

Usage:
    python scripts/smoke_gnani.py [--audio path/to/sample.wav] [--output artifacts/smoke]
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fieldcheck.providers.gnani import GnaniClient, GnaniProviderError


async def run_smoke(audio_path: str | None, output_dir: str) -> None:
    client = GnaniClient()
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    print("==================================================")
    print("FieldCheck — Gnani Provider Verification Probe")
    print("==================================================")
    print(f"STT Endpoint: {client.stt_url}")
    print(f"TTS Endpoint: {client.tts_url}")
    print(f"Target Models: STT={client.stt_model}, TTS={client.tts_model}")
    print(f"Credentials Configured: {'YES' if client.has_credentials() else 'NO (Fixture Fallback Active)'}")

    # 1. Test STT
    print("\n--- [1/2] Testing Speech-to-Text (Prisma) ---")
    if audio_path and os.path.exists(audio_path):
        with open(audio_path, "rb") as f:
            wav_bytes = f.read()
    else:
        # 1-second 16kHz mono silent WAV
        wav_bytes = (
            b"RIFF$\x7d\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
            b"\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00data\x00\x7d\x00\x00"
            + b"\x00" * 32000
        )

    t0 = time.perf_counter()
    try:
        stt_res = await client.transcribe_audio(wav_bytes)
        stt_elapsed = (time.perf_counter() - t0) * 1000.0
        print(f"STT Result: SUCCESS ({stt_elapsed:.1f}ms)")
        print(f"Transcript: \"{stt_res.text}\"")
        print(f"Model: {stt_res.effective_model}")
        print(f"Source: {stt_res.source}")
        print(f"Request ID: {stt_res.request_id}")
    except GnaniProviderError as err:
        print(f"STT Result: FAILED — {err}")

    # 2. Test TTS
    print("\n--- [2/2] Testing Text-to-Speech (Timbre) ---")
    test_phrase = "कृपया मरीज़ का पूरा नाम दोबारा बोलिए।"
    t0 = time.perf_counter()
    try:
        tts_audio = await client.synthesize_speech(test_phrase)
        tts_elapsed = (time.perf_counter() - t0) * 1000.0
        print(f"TTS Result: SUCCESS ({tts_elapsed:.1f}ms, {len(tts_audio)} bytes)")
        out_wav = out / "tts_probe_output.wav"
        with open(out_wav, "wb") as f:
            f.write(tts_audio)
        print(f"Saved probe audio to: {out_wav}")
    except GnaniProviderError as err:
        print(f"TTS Result: FAILED — {err}")

    print("\nProbe check completed.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Gnani Provider Smoke Test")
    parser.add_argument("--audio", type=str, default=None, help="Path to input audio file")
    parser.add_argument("--output", type=str, default="artifacts/smoke", help="Output directory")
    args = parser.parse_args()

    asyncio.run(run_smoke(args.audio, args.output))


if __name__ == "__main__":
    main()
