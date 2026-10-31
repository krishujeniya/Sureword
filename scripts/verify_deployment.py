#!/usr/bin/env python3
"""Automated deployment verification and smoke test runner for FieldCheck.

Exercises health check, static asset serving, draft lifecycle, audio conversion,
field parsing, clarification, idempotent commit, and session cleanup.

Usage:
    python scripts/verify_deployment.py [--base-url http://127.0.0.1:8000]
"""

from __future__ import annotations

import argparse
import sys
import time

import httpx


def generate_test_wav(duration_s: float = 0.5, sample_rate: int = 16000) -> bytes:
    """Generate a clean PCM mono 16-bit WAV header and silence."""
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


def run_deployment_check(base_url: str) -> None:
    print("=================================================================")
    print(f"FieldCheck — Deployment Smoke Verification: {base_url}")
    print("=================================================================\n")

    client = httpx.Client(base_url=base_url, timeout=15.0)
    checks: list[tuple[str, bool, float, str]] = []

    # 1. Health check
    t0 = time.perf_counter()
    try:
        res = client.get("/healthz")
        elapsed = (time.perf_counter() - t0) * 1000.0
        if res.status_code == 200 and res.json().get("status") == "healthy":
            checks.append(("GET /healthz", True, elapsed, f"OK (db: {res.json().get('database')})"))
        else:
            checks.append(("GET /healthz", False, elapsed, f"Status {res.status_code}: {res.text}"))
    except Exception as ex:
        checks.append(("GET /healthz", False, 0.0, f"Connection error: {ex}"))

    # 2. Static UI check
    t0 = time.perf_counter()
    try:
        res = client.get("/")
        elapsed = (time.perf_counter() - t0) * 1000.0
        if res.status_code == 200 and "FieldCheck" in res.text:
            checks.append(("GET / (UI)", True, elapsed, "OK (HTML served)"))
        else:
            checks.append(("GET / (UI)", False, elapsed, f"Failed (HTTP {res.status_code})"))
    except Exception as ex:
        checks.append(("GET / (UI)", False, 0.0, f"Failed: {ex}"))

    # 3. Create Draft Session
    draft_id = ""
    curr_v = 1
    t0 = time.perf_counter()
    try:
        res = client.post("/api/drafts")
        elapsed = (time.perf_counter() - t0) * 1000.0
        if res.status_code == 200:
            data = res.json()
            draft_id = data["draft_id"]
            curr_v = data["version"]
            checks.append(("POST /api/drafts", True, elapsed, f"OK (draft: {draft_id}, v{curr_v})"))
        else:
            checks.append(("POST /api/drafts", False, elapsed, f"HTTP {res.status_code}"))
    except Exception as ex:
        checks.append(("POST /api/drafts", False, 0.0, f"Error: {ex}"))

    if not draft_id:
        print_summary_and_exit(checks)

    # 4. Upload Audio
    t0 = time.perf_counter()
    try:
        wav_data = generate_test_wav(0.5)
        files = {"audio_file": ("test.wav", wav_data, "audio/wav")}
        data_payload = {"expected_version": curr_v}
        res = client.post(f"/api/drafts/{draft_id}/audio", data=data_payload, files=files)
        elapsed = (time.perf_counter() - t0) * 1000.0
        if res.status_code == 200:
            d_res = res.json()
            curr_v = d_res["draft"]["version"]
            checks.append(("POST /api/drafts/{id}/audio", True, elapsed, f"OK (v{curr_v}, state: {d_res['draft']['state']})"))
        else:
            checks.append(("POST /api/drafts/{id}/audio", False, elapsed, f"HTTP {res.status_code}: {res.text[:100]}"))
    except Exception as ex:
        checks.append(("POST /api/drafts/{id}/audio", False, 0.0, f"Error: {ex}"))

    # 5. Clarify field
    t0 = time.perf_counter()
    try:
        res = client.post(
            f"/api/drafts/{draft_id}/clarify",
            data={
                "target_field": "person_name",
                "expected_version": curr_v,
                "manual_value": "Kamla Devi",
            },
        )
        elapsed = (time.perf_counter() - t0) * 1000.0
        if res.status_code == 200:
            d_res = res.json()
            curr_v = d_res["version"]
            checks.append(("POST /api/drafts/{id}/clarify", True, elapsed, f"OK (v{curr_v}, person_name verified)"))
        else:
            checks.append(("POST /api/drafts/{id}/clarify", False, elapsed, f"HTTP {res.status_code}"))
    except Exception as ex:
        checks.append(("POST /api/drafts/{id}/clarify", False, 0.0, f"Error: {ex}"))

    # 6. Ensure all remaining fields confirmed for commit test
    try:
        draft_fetch = client.get(f"/api/drafts/{draft_id}").json()
        for k in ["age", "village", "visit_date"]:
            if draft_fetch["fields"][k]["status"] not in {"user_confirmed", "manually_edited"}:
                val = draft_fetch["fields"][k]["canonical_value"] or "TestVal"
                res_c = client.post(
                    f"/api/drafts/{draft_id}/clarify",
                    data={
                        "target_field": k,
                        "expected_version": curr_v,
                        "manual_value": str(val),
                    },
                )
                if res_c.status_code == 200:
                    curr_v = res_c.json()["version"]
    except Exception as ex:
        print(f"Field setup warning: {ex}")

    # 7. Commit Record
    t0 = time.perf_counter()
    try:
        res = client.post(
            f"/api/drafts/{draft_id}/commit",
            json={
                "expected_version": curr_v,
                "idempotency_key": f"deploy_test_{int(time.time())}",
            },
        )
        elapsed = (time.perf_counter() - t0) * 1000.0
        if res.status_code == 200:
            rec_id = res.json().get("record_id")
            checks.append(("POST /api/drafts/{id}/commit", True, elapsed, f"OK ({rec_id})"))
        else:
            checks.append(("POST /api/drafts/{id}/commit", False, elapsed, f"HTTP {res.status_code}: {res.text[:100]}"))
    except Exception as ex:
        checks.append(("POST /api/drafts/{id}/commit", False, 0.0, f"Error: {ex}"))

    # 8. Cleanup / Delete draft
    t0 = time.perf_counter()
    try:
        res = client.delete(f"/api/drafts/{draft_id}")
        elapsed = (time.perf_counter() - t0) * 1000.0
        if res.status_code == 204:
            checks.append(("DELETE /api/drafts/{id}", True, elapsed, "OK (deleted)"))
        else:
            checks.append(("DELETE /api/drafts/{id}", False, elapsed, f"HTTP {res.status_code}"))
    except Exception as ex:
        checks.append(("DELETE /api/drafts/{id}", False, 0.0, f"Error: {ex}"))

    print_summary_and_exit(checks)


def print_summary_and_exit(checks: list[tuple[str, bool, float, str]]) -> None:
    all_passed = True
    print("| Step | Result | Latency | Details |")
    print("|---|---|---|---|")
    for step, passed, lat, details in checks:
        status_str = "**PASS**" if passed else "**FAIL**"
        if not passed:
            all_passed = False
        print(f"| {step} | {status_str} | {lat:.1f}ms | {details} |")

    print("\n=================================================================")
    if all_passed:
        print("DEPLOYMENT VERIFICATION PASSED: All endpoints operational.")
        print("=================================================================")
        sys.exit(0)
    else:
        print("DEPLOYMENT VERIFICATION FAILED: One or more checks failed.")
        print("=================================================================")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="FieldCheck Deployment Verification")
    parser.add_argument("--base-url", type=str, default="http://127.0.0.1:8000", help="Base URL of deployment")
    args = parser.parse_args()

    run_deployment_check(args.base_url)


if __name__ == "__main__":
    main()
