#!/usr/bin/env python3
"""Dataset manifest validation and leakage verification script.

Ensures zero speaker and sample overlap between development and test splits.

Usage:
    python scripts/validate_manifest.py --dev data/manifests/dev.jsonl --test data/manifests/test.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_manifest(path: Path) -> list[dict]:
    if not path.exists():
        print(f"Error: Manifest file not found: {path}")
        sys.exit(1)

    records = []
    with open(path, encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                records.append(rec)
            except json.JSONDecodeError as err:
                print(f"Error: Invalid JSON on line {idx} of {path}: {err}")
                sys.exit(1)
    return records


def validate_splits(dev_path: Path, test_path: Path) -> None:
    print(f"Loading dev manifest from: {dev_path}")
    dev_records = load_manifest(dev_path)
    print(f"Loaded {len(dev_records)} dev samples.")

    print(f"Loading test manifest from: {test_path}")
    test_records = load_manifest(test_path)
    print(f"Loaded {len(test_records)} test samples.")

    dev_sample_ids = {r["sample_id"] for r in dev_records}
    test_sample_ids = {r["sample_id"] for r in test_records}

    dev_speakers = {r["speaker_id"] for r in dev_records}
    test_speakers = {r["speaker_id"] for r in test_records}

    # 1. Sample ID Collision Check
    sample_collisions = dev_sample_ids.intersection(test_sample_ids)
    if sample_collisions:
        print(f"\n[FAIL] Found {len(sample_collisions)} overlapping sample IDs between dev and test: {sample_collisions}")
        sys.exit(1)
    print("\n[PASS] Zero sample ID overlap between dev and test splits.")

    # 2. Speaker Leakage Check
    speaker_leakage = dev_speakers.intersection(test_speakers)
    if speaker_leakage:
        print(f"\n[FAIL] Speaker leakage detected! Overlapping speakers: {speaker_leakage}")
        sys.exit(1)
    print(f"[PASS] Zero speaker leakage. Dev speakers: {sorted(list(dev_speakers))}; Test speakers: {sorted(list(test_speakers))}")

    # 3. Required Fields Check
    required_keys = {"sample_id", "speaker_id", "language", "gold_fields"}
    for split_name, recs in [("dev", dev_records), ("test", test_records)]:
        for r in recs:
            missing = required_keys - set(r.keys())
            if missing:
                print(f"\n[FAIL] Record {r.get('sample_id')} in {split_name} missing required fields: {missing}")
                sys.exit(1)
            # Check 4 critical fields in gold_fields
            gf = r["gold_fields"]
            for cf in ["person_name", "age", "village", "visit_date"]:
                if cf not in gf:
                    print(f"\n[FAIL] Record {r.get('sample_id')} missing critical gold field: {cf}")
                    sys.exit(1)

    print("[PASS] All records contain valid required fields and 4 critical gold fields.")
    print("\n==================================================")
    print("MANIFEST VALIDATION SUCCESSFUL: Protocol is frozen.")
    print("==================================================")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Dataset Manifests")
    parser.add_argument("--dev", type=Path, default=Path("data/manifests/dev.jsonl"), help="Dev manifest")
    parser.add_argument("--test", type=Path, default=Path("data/manifests/test.jsonl"), help="Test manifest")
    args = parser.parse_args()

    validate_splits(args.dev, args.test)


if __name__ == "__main__":
    main()
