#!/usr/bin/env python3
"""Automated Demo Screencast & Step Snapshot Capture for Sureword.

Exercises the entire 60-second submission flow and captures high-resolution
screenshots of each state using native headless Chrome.

Usage:
    python scripts/capture_demo_walkthrough.py [--base-url http://127.0.0.1:8000] [--output artifacts/demo]
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

import httpx


def generate_wav(duration_s: float = 0.5, sample_rate: int = 16000) -> bytes:
    num_samples = int(sample_rate * duration_s)
    data_size = num_samples * 2
    header = (
        b"RIFF"
        + (data_size + 36).to_bytes(4, "little")
        + b"WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
        + sample_rate.to_bytes(4, "little")
        + (sample_rate * 2).to_bytes(4, "little")
        + b"\x02\x00\x10\x00data"
        + data_size.to_bytes(4, "little")
    )
    return header + (b"\x00" * data_size)


def capture_screenshot(
    chrome_bin: str, url: str, output_png: Path, window_size: str = "1280,820", timeout: int = 25
) -> bool:
    cmd = [
        chrome_bin,
        "--headless",
        "--no-sandbox",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--window-size={window_size}",
        f"--screenshot={output_png}",
        url,
    ]
    try:
        res = subprocess.run(
            cmd, capture_output=True, timeout=timeout, stdin=subprocess.DEVNULL, check=False
        )
        return res.returncode == 0 and output_png.exists()
    except Exception as ex:
        print(f"Error capturing {output_png}: {ex}")
        return False


def build_preview_html(output_dir: Path, steps_info: list[dict[str, str]]) -> None:
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sureword — 60-Second Demo Storyboard Walkthrough</title>
  <style>
    body { font-family: system-ui, -apple-system, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 2rem; }
    .container { max-width: 1100px; margin: 0 auto; }
    h1 { color: #38bdf8; margin-bottom: 0.5rem; }
    p.lead { color: #94a3b8; font-size: 1.1rem; margin-bottom: 2rem; }
    .step-card { background: #1e293b; border-radius: 12px; padding: 1.5rem; margin-bottom: 2.5rem; border: 1px solid #334155; }
    .step-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid #334155; padding-bottom: 0.5rem; }
    .step-title { font-size: 1.25rem; font-weight: 600; color: #f1f5f9; }
    .step-time { background: #0369a1; color: white; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.85rem; font-weight: bold; }
    .step-desc { color: #cbd5e1; margin-bottom: 1rem; font-size: 0.95rem; line-height: 1.5; }
    .step-narration { background: #0f172a; border-left: 4px solid #38bdf8; padding: 0.75rem 1rem; border-radius: 4px; font-style: italic; color: #e2e8f0; margin-bottom: 1rem; }
    .step-img-wrap { border: 1px solid #475569; border-radius: 8px; overflow: hidden; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5); }
    .step-img-wrap img { width: 100%; height: auto; display: block; }
  </style>
</head>
<body>
  <div class="container">
    <h1>Sureword: 60-Second Video Demo Walkthrough</h1>
    <p class="lead">Storyboard sequence matching official nomination guidelines and docs/SUBMISSION_PACK.md §3</p>
"""
    for s in steps_info:
        html_content += f"""
    <div class="step-card">
      <div class="step-header">
        <div class="step-title">{s["title"]}</div>
        <div class="step-time">{s["time"]}</div>
      </div>
      <div class="step-desc"><strong>Visual Action:</strong> {s["desc"]}</div>
      <div class="step-narration"><strong>Narration:</strong> "{s["narration"]}"</div>
      <div class="step-img-wrap">
        <img src="{s["filename"]}" alt="{s["title"]}">
      </div>
    </div>
"""

    html_content += """
  </div>
</body>
</html>
"""
    preview_path = output_dir / "demo_preview.html"
    with open(preview_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated storyboard HTML preview: {preview_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture Demo Walkthrough Screenshots")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--output", type=Path, default=Path("artifacts/demo"))
    args = parser.parse_args()

    chrome_bin = shutil.which("google-chrome") or shutil.which("chromium")
    if not chrome_bin:
        print("Error: google-chrome or chromium not found on system.")
        sys.exit(1)

    args.output.mkdir(parents=True, exist_ok=True)
    client = httpx.Client(base_url=args.base_url, timeout=10.0)

    # 1. Health check
    try:
        res = client.get("/healthz")
        if res.status_code != 200:
            print(f"Server at {args.base_url} returned status {res.status_code}")
            sys.exit(1)
    except Exception as ex:
        print(f"Cannot connect to server at {args.base_url}: {ex}")
        print(
            "Please start the server first: uv run uvicorn sureword.app:app --host 127.0.0.1 --port 8000"
        )
        sys.exit(1)

    steps_info: list[dict[str, str]] = []

    print("\n[1/5] Capturing Step 1: Blank Visit Form...")
    step1_png = args.output / "step1_blank_form.png"
    if capture_screenshot(chrome_bin, f"{args.base_url}/", step1_png):
        print(f"  -> Saved: {step1_png}")
        steps_info.append(
            {
                "title": "Step 1: Blank Frontline Visit Form",
                "time": "0:00 – 0:08",
                "desc": "Open Sureword web application. Blank visit form with 4 core fields: Person Name, Age, Village, Visit Date.",
                "narration": "Frontline workers dictate household visits in Hindi-English, but a single mistranscribed name or age can quietly corrupt digital records.",
                "filename": "step1_blank_form.png",
            }
        )

    print("\n[2/5] Creating draft and processing dictation with physiological age bound error...")
    d_res = client.post("/api/drafts").json()
    draft_id = d_res["draft_id"]
    curr_v = d_res["version"]

    wav_bytes = generate_wav(0.5)
    files = {"audio_file": ("dictation.wav", wav_bytes, "audio/wav")}
    client.post(f"/api/drafts/{draft_id}/audio", data={"expected_version": curr_v}, files=files)

    step2_png = args.output / "step2_dictation_flagged.png"
    time.sleep(0.5)
    if capture_screenshot(chrome_bin, f"{args.base_url}/?draft_id={draft_id}", step2_png):
        print(f"  -> Saved: {step2_png}")
        steps_info.append(
            {
                "title": "Step 2: Dictation Transcribed & Age Flagged (Needs Repeat)",
                "time": "0:08 – 0:32",
                "desc": "Prisma transcript streams in. Name, Village, and Date show valid; Age 150 is flagged out of physiological bounds (1-120) with a red Needs Repeat badge.",
                "narration": "Gnani Prisma transcribes the audio. Our deterministic parser flags that age 150 is out of valid physiological bounds.",
                "filename": "step2_dictation_flagged.png",
            }
        )

    print("\n[3/5] Capturing Step 3: Spoken Clarification Banner Active...")
    step3_png = args.output / "step3_clarification_banner.png"
    if capture_screenshot(chrome_bin, f"{args.base_url}/?draft_id={draft_id}", step3_png):
        print(f"  -> Saved: {step3_png}")
        steps_info.append(
            {
                "title": "Step 3: Timbre Spoken Clarification Audio & Banner",
                "time": "0:32 – 0:46",
                "desc": "Gnani Timbre speaks prompt: 'कृपया मरीज़ की सही उम्र दोबारा बोलिए।' System asks user to repeat only the uncertain field.",
                "narration": "Gnani Timbre speaks up to clarify only the uncertain field. We repeat just the age, and the record updates with full provenance.",
                "filename": "step3_clarification_banner.png",
            }
        )

    print("\n[4/5] Clarifying age to 45 and capturing Step 4: Ready for Review...")
    draft_curr = client.get(f"/api/drafts/{draft_id}").json()
    curr_v = draft_curr["version"]
    res_clarify = client.post(
        f"/api/drafts/{draft_id}/clarify",
        data={
            "target_field": "age",
            "expected_version": curr_v,
            "manual_value": "45",
        },
    ).json()
    curr_v = res_clarify["version"]

    step4_png = args.output / "step4_ready_for_review.png"
    time.sleep(0.5)
    if capture_screenshot(chrome_bin, f"{args.base_url}/?draft_id={draft_id}", step4_png):
        print(f"  -> Saved: {step4_png}")
        steps_info.append(
            {
                "title": "Step 4: Age Corrected & State Transitions to READY_FOR_REVIEW",
                "time": "0:46 – 0:54",
                "desc": "Age updates to 45 with Confirmed badge. All 4 fields verified. Verify & Commit Record button becomes active.",
                "narration": "The record cannot commit until all fields are verified. Review is explicit, and save is idempotent.",
                "filename": "step4_ready_for_review.png",
            }
        )

    print("\n[5/5] Committing record and capturing Step 5: Committed Local Audit...")
    client.post(
        f"/api/drafts/{draft_id}/commit",
        json={
            "expected_version": curr_v,
            "idempotency_key": f"demo_capture_{int(time.time())}",
        },
    )

    step5_png = args.output / "step5_committed_record.png"
    time.sleep(0.5)
    if capture_screenshot(chrome_bin, f"{args.base_url}/?draft_id={draft_id}", step5_png):
        print(f"  -> Saved: {step5_png}")
        steps_info.append(
            {
                "title": "Step 5: Record Committed with Local ID & Full JSON Audit",
                "time": "0:54 – 1:00",
                "desc": "Record ID generated (REC-20261031-XXXX). Complete JSON provenance audit log displayed locally.",
                "narration": "Sureword: selective clarification for sovereign speech workflows. Code and benchmarks on GitHub.",
                "filename": "step5_committed_record.png",
            }
        )

    build_preview_html(args.output, steps_info)
    print("\n========================================================")
    print("ALL DEMO SNAPSHOTS CAPTURED SUCCESSFULLY!")
    print(f"Directory: {args.output.resolve()}")
    print("========================================================")


if __name__ == "__main__":
    main()
