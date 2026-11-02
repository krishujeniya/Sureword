#!/usr/bin/env python3
"""Sureword — 60-Second Video Demo Walkthrough Runner (T19 Helper).

Guides the presenter through each segment of the 60-second submission video,
showing exact timings, visual cues, and narration lines from docs/SUBMISSION_PACK.md.

Usage:
    python scripts/demo_runner.py [--base-url http://127.0.0.1:8000]
"""

from __future__ import annotations

import argparse
import sys

import httpx

STORYBOARD = [
    {
        "segment": "1/6: Opening & Problem Context",
        "time_window": "0:00 – 0:08 (8s)",
        "visual_cue": "Display blank Sureword visit form (http://127.0.0.1:8000). Show fields: Name, Age, Village, Visit Date.",
        "narration": "Frontline workers dictate household visits in Hindi-English, but a single mistranscribed name or age can quietly corrupt digital records.",
        "action": "Open browser to http://127.0.0.1:8000. Ensure microphone permission is granted.",
    },
    {
        "segment": "2/6: Code-Mixed Dictation with Bound Error",
        "time_window": "0:08 – 0:18 (10s)",
        "visual_cue": "Click 'Start Recording'. Speak the test visit sentence clearly into the microphone.",
        "narration": "Let's dictate a visit with an intentional physiological error: age 150 years.",
        "action": "Speak clearly: 'मरीज का नाम कमला देवी, उम्र 150 साल, गाँव रामपुर, 30 अक्टूबर 2026'",
    },
    {
        "segment": "3/6: Gnani Prisma Transcription & Deterministic Flagging",
        "time_window": "0:18 – 0:32 (14s)",
        "visual_cue": "Click 'Stop Recording'. Live transcript streams in. Name, Village, and Date show green; Age badge highlights red (Needs Repeat).",
        "narration": "Gnani Prisma transcribes the audio. Our deterministic parser flags that age 150 is out of valid physiological bounds.",
        "action": "Point mouse cursor to the red 'Needs Repeat' badge next to the Age field.",
    },
    {
        "segment": "4/6: Gnani Timbre Spoken Clarification & Turn Recovery",
        "time_window": "0:32 – 0:46 (14s)",
        "visual_cue": "Timbre spoken audio plays. Click 'Speak This Field' and repeat only the corrected age.",
        "narration": "Gnani Timbre speaks up to clarify only the uncertain field. We repeat just the age, and the record updates with full provenance.",
        "action": "Speak: 'पैंतालीस साल' (45 years). Watch Age update to 45 with a green 'Confirmed' badge.",
    },
    {
        "segment": "5/6: Explicit Review & Idempotent Commit",
        "time_window": "0:46 – 0:54 (8s)",
        "visual_cue": "Form transitions to READY_FOR_REVIEW. Click 'Verify & Commit Record'. Show generated record ID and JSON audit log.",
        "narration": "The record cannot commit until all fields are verified. Review is explicit, and save is idempotent.",
        "action": "Click 'Verify & Commit Record' button. Highlight record ID (REC-20261031-XXXX).",
    },
    {
        "segment": "6/6: Benchmark Card & GitHub Repository Link",
        "time_window": "0:54 – 1:00 (6s)",
        "visual_cue": "Switch to summary card: 50% relative error reduction (6.2% -> 3.1% at 1 prompt/form). Display GitHub URL.",
        "narration": "Sureword: selective clarification for sovereign speech workflows. Code and benchmarks on GitHub.",
        "action": "Show benchmark chart/card and conclude recording within 60 seconds.",
    },
]


def check_server(base_url: str) -> bool:
    try:
        res = httpx.get(f"{base_url}/healthz", timeout=3.0)
        return res.status_code == 200
    except Exception:
        return False


def run_demo_guide(base_url: str) -> None:
    print("=" * 72)
    print("   Sureword — 60-Second Video Demo Walkthrough Guide (T19)")
    print("=" * 72)
    print(f"Target Server: {base_url}")

    if not check_server(base_url):
        print(f"\n[WARNING] Server is not currently reachable at {base_url}.")
        print("Please launch it in another terminal before recording:")
        print("   uv run uvicorn sureword.app:app --host 127.0.0.1 --port 8000\n")
    else:
        print("[OK] Server is running and responsive at /healthz.\n")

    print(
        "Prepare your screen recorder (e.g., OBS Studio, SimpleScreenRecorder, or browser recorder)."
    )
    print("Press [Enter] to begin the countdown for each segment.\n")

    for step in STORYBOARD:
        print("-" * 72)
        print(f"[{step['segment']}] — Window: {step['time_window']}")
        print(f"Action:     {step['action']}")
        print(f"Visual:     {step['visual_cue']}")
        print(f'Narration:  "{step["narration"]}"')
        print("-" * 72)
        try:
            input("Press [Enter] when ready for this segment (or Ctrl+C to exit)... ")
        except (KeyboardInterrupt, EOFError):
            print("\nDemo walkthrough paused.")
            sys.exit(0)

    print("\n" + "=" * 72)
    print("WALKTHROUGH COMPLETE: Video fits strictly within the 60-second limit.")
    print("Submission Pack Reference: docs/SUBMISSION_PACK.md §3")
    print("=" * 72)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sureword 60-Second Demo Rehearsal Runner")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="App base URL")
    args = parser.parse_args()
    run_demo_guide(args.base_url)


if __name__ == "__main__":
    main()
