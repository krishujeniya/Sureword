#!/usr/bin/env python3
"""Evaluation runner for Sureword: compares B0, B1, B2, B3, and Policy P.

Computes primary accepted-field error, automatic coverage, uncaught error rate,
whole-record correctness, and realized clarification burden.

Usage:
    python scripts/evaluate.py [--config configs/experiment.json] [--manifest data/manifests/test.jsonl] [--output artifacts/evaluation]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sureword.contracts import FieldKey, FieldStatus, FieldValue
from sureword.parser import parse_visit_form
from sureword.policy import (
    select_clarification_field_b1,
    select_clarification_field_b2,
    select_clarification_field_p,
)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def canonicalize(val: str | None) -> str:
    """Normalize string for scoring comparison."""
    if val is None:
        return ""
    return val.strip().lower()


def evaluate_policy(
    policy_name: str,
    samples: list[dict[str, Any]],
    budget_max_prompts: int = 1,
    seed: int = 42,
) -> dict[str, Any]:
    critical_keys = [
        FieldKey.PERSON_NAME.value,
        FieldKey.AGE.value,
        FieldKey.VILLAGE.value,
        FieldKey.VISIT_DATE.value,
    ]

    total_expected_critical_fields = len(samples) * len(critical_keys)
    total_auto_accepted = 0
    wrong_auto_accepted = 0
    total_prompts = 0
    records_all_correct = 0

    error_rows = []

    for sample in samples:
        transcript = sample["transcript"]
        gold = sample["gold_fields"]
        parsed = parse_visit_form(transcript)

        attempts_by_field: dict[str, int] = {}
        prompts_this_sample = 0

        # Run clarification turn if policy allows prompts
        if policy_name == "B0":
            # No prompts allowed
            pass
        elif policy_name == "B1":
            prompt = select_clarification_field_b1(parsed, attempts_by_field, max_attempts=1)
            if prompt:
                prompts_this_sample += 1
                # Simulated clarification: user repeats gold label for that field
                k = prompt.target_field
                parsed[k] = FieldValue(
                    key=k,
                    raw_span=gold[k],
                    canonical_value=gold[k],
                    status=FieldStatus.USER_CONFIRMED,
                )
        elif policy_name == "B2":
            prompt = select_clarification_field_b2(
                parsed, attempts_by_field, seed=seed, max_attempts=1
            )
            if prompt:
                prompts_this_sample += 1
                k = prompt.target_field
                parsed[k] = FieldValue(
                    key=k,
                    raw_span=gold[k],
                    canonical_value=gold[k],
                    status=FieldStatus.USER_CONFIRMED,
                )
        elif policy_name == "B3":
            # Confirm every field (upper bound reference)
            for k in critical_keys:
                prompts_this_sample += 1
                parsed[k] = FieldValue(
                    key=k,
                    raw_span=gold[k],
                    canonical_value=gold[k],
                    status=FieldStatus.USER_CONFIRMED,
                )
        elif policy_name == "P":
            prompt = select_clarification_field_p(
                parsed, attempts_by_field, max_attempts=budget_max_prompts, risk_threshold=0.3
            )
            if prompt:
                prompts_this_sample += 1
                k = prompt.target_field
                parsed[k] = FieldValue(
                    key=k,
                    raw_span=gold[k],
                    canonical_value=gold[k],
                    status=FieldStatus.USER_CONFIRMED,
                )

        total_prompts += prompts_this_sample

        # Score fields
        sample_correct = True
        for k in critical_keys:
            f = parsed[k]
            gold_val = canonicalize(gold[k])
            cand_val = canonicalize(f.canonical_value)

            is_accepted = (
                f.status
                in {FieldStatus.PROPOSED, FieldStatus.USER_CONFIRMED, FieldStatus.MANUALLY_EDITED}
                and f.canonical_value is not None
            )

            if is_accepted:
                total_auto_accepted += 1
                if cand_val != gold_val:
                    wrong_auto_accepted += 1
                    sample_correct = False
                    error_rows.append(
                        {
                            "sample_id": sample["sample_id"],
                            "field": k,
                            "expected": gold_val,
                            "predicted": cand_val,
                            "status": f.status.value,
                        }
                    )
            else:
                sample_correct = False

        if sample_correct:
            records_all_correct += 1

    # Compute metrics with explicit denominators
    primary_err = (wrong_auto_accepted / total_auto_accepted) if total_auto_accepted > 0 else 0.0
    coverage = (
        (total_auto_accepted / total_expected_critical_fields)
        if total_expected_critical_fields > 0
        else 0.0
    )
    uncaught_err = (
        (wrong_auto_accepted / total_expected_critical_fields)
        if total_expected_critical_fields > 0
        else 0.0
    )
    burden = total_prompts / len(samples) if samples else 0.0
    record_accuracy = records_all_correct / len(samples) if samples else 0.0

    return {
        "policy": policy_name,
        "samples_evaluated": len(samples),
        "primary_accepted_field_error": round(primary_err, 4),
        "primary_error_fraction": f"{wrong_auto_accepted}/{total_auto_accepted}",
        "automatic_coverage": round(coverage, 4),
        "automatic_coverage_fraction": f"{total_auto_accepted}/{total_expected_critical_fields}",
        "uncaught_error_rate": round(uncaught_err, 4),
        "whole_record_correctness": round(record_accuracy, 4),
        "whole_record_fraction": f"{records_all_correct}/{len(samples)}",
        "realized_clarification_burden": round(burden, 2),
        "total_prompts": total_prompts,
        "error_rows": error_rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Sureword policies")
    parser.add_argument("--config", type=Path, default=Path("configs/experiment.json"))
    parser.add_argument("--manifest", type=Path, default=Path("data/manifests/test.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/evaluation"))
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    samples = load_jsonl(args.manifest)

    policies = ["B0", "B1", "B2", "P", "B3"]
    results = {}

    print(
        "========================================================================================="
    )
    print(f"Sureword Benchmark Evaluation — {len(samples)} Held-Out Test Samples")
    print(
        "=========================================================================================\n"
    )

    for pol in policies:
        res = evaluate_policy(pol, samples, budget_max_prompts=1, seed=42)
        results[pol] = res

    # Print Markdown Summary Table
    headers = [
        "Policy",
        "Description",
        "Primary Error",
        "Auto Coverage",
        "Uncaught Error",
        "Record Correctness",
        "Burden (prompts/form)",
    ]
    descriptions = {
        "B0": "Raw ASR (No clarification)",
        "B1": "Alphabetical (Budget 1)",
        "B2": "Random Selection (Budget 1)",
        "P": "Selective Risk Ranking (Budget 1)",
        "B3": "Confirm All Fields (Upper Bound)",
    }

    print(f"| {' | '.join(headers)} |")
    print(f"|{'---|' * len(headers)}")
    for pol in policies:
        r = results[pol]
        print(
            f"| **{pol}** | {descriptions[pol]} "
            f"| {r['primary_accepted_field_error']:.1%} ({r['primary_error_fraction']}) "
            f"| {r['automatic_coverage']:.1%} ({r['automatic_coverage_fraction']}) "
            f"| {r['uncaught_error_rate']:.1%} "
            f"| {r['whole_record_correctness']:.1%} ({r['whole_record_fraction']}) "
            f"| {r['realized_clarification_burden']} |"
        )

    # Save artifacts
    results_path = args.output / "results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nArtifact saved: {results_path}")
    print(
        "========================================================================================="
    )


if __name__ == "__main__":
    main()
