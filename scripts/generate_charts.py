#!/usr/bin/env python3
"""Generate publication-ready evaluation charts for FieldCheck.

Reads artifacts/evaluation/results.json and produces:
- artifacts/evaluation/error_vs_burden.png
- artifacts/evaluation/policy_comparison.png

Usage:
    python scripts/generate_charts.py [--results artifacts/evaluation/results.json] [--output artifacts/evaluation]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def generate_charts(results_path: Path, output_dir: Path) -> None:
    if not results_path.exists():
        print(f"Error: Results file not found: {results_path}")
        sys.exit(1)

    with open(results_path, encoding="utf-8") as f:
        data = json.load(f)

    output_dir.mkdir(parents=True, exist_ok=True)

    policies = ["B0", "B1", "B2", "P", "B3"]
    labels = {
        "B0": "B0: Raw ASR",
        "B1": "B1: Alphabetical",
        "B2": "B2: Random",
        "P": "P: Risk-Ranked",
        "B3": "B3: Confirm All",
    }
    colors = {
        "B0": "#64748b",  # slate
        "B1": "#0284c7",  # sky blue
        "B2": "#eab308",  # yellow
        "P": "#16a34a",   # emerald green
        "B3": "#8b5cf6",  # purple
    }

    [data[p]["realized_clarification_burden"] for p in policies]
    errors = [data[p]["primary_accepted_field_error"] * 100 for p in policies]
    coverages = [data[p]["automatic_coverage"] * 100 for p in policies]
    correctness = [data[p]["whole_record_correctness"] * 100 for p in policies]

    # --- Chart 1: Error vs. Clarification Burden ---
    plt.figure(figsize=(8, 5.5), dpi=300)
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    for p in policies:
        x = data[p]["realized_clarification_burden"]
        y = data[p]["primary_accepted_field_error"] * 100
        size = 180 if p == "P" else 130
        plt.scatter(
            x, y,
            color=colors[p],
            s=size,
            label=labels[p],
            edgecolor="black",
            linewidth=1.2,
            zorder=4,
        )
        offset_y = 0.3 if p != "B1" else -0.5
        offset_x = 0.05 if p != "P" else -0.15
        plt.annotate(
            f"{p} ({y:.1f}%)",
            (x + offset_x, y + offset_y),
            fontweight="bold" if p == "P" else "normal",
            fontsize=9,
        )

    plt.title("FieldCheck: Critical-Field Error vs. Clarification Burden", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Realized Clarification Burden (prompts / form)", fontsize=10, labelpad=8)
    plt.ylabel("Primary Accepted-Field Error (%)", fontsize=10, labelpad=8)
    plt.ylim(-0.5, max(errors) + 2.0)
    plt.xlim(-0.2, 4.5)
    plt.axvline(1.0, color="#94a3b8", linestyle="--", alpha=0.7, label="Budget Limit (1.0 prompt/form)")
    plt.legend(frameon=True, loc="upper right", fontsize=9)
    plt.tight_layout()

    chart1_path = output_dir / "error_vs_burden.png"
    plt.savefig(chart1_path)
    plt.close()
    print(f"Generated chart: {chart1_path}")

    # --- Chart 2: Grouped Policy Comparison Bar Chart ---
    plt.figure(figsize=(10, 5.5), dpi=300)
    x = np.arange(len(policies))
    width = 0.25

    plt.bar(x - width, errors, width, label="Primary Error (%)", color="#ef4444", alpha=0.9, edgecolor="black", linewidth=0.8)
    plt.bar(x, coverages, width, label="Coverage (%)", color="#0284c7", alpha=0.9, edgecolor="black", linewidth=0.8)
    plt.bar(x + width, correctness, width, label="Whole-Record Correctness (%)", color="#16a34a", alpha=0.9, edgecolor="black", linewidth=0.8)

    plt.title("FieldCheck: Comparative Metric Profiles Across Policies", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Verification Policy", fontsize=10, labelpad=8)
    plt.ylabel("Percentage (%)", fontsize=10, labelpad=8)
    plt.xticks(x, [labels[p] for p in policies], fontsize=9)
    plt.ylim(0, 115)
    plt.legend(frameon=True, loc="upper left", fontsize=9)
    plt.tight_layout()

    chart2_path = output_dir / "policy_comparison.png"
    plt.savefig(chart2_path)
    plt.close()
    print(f"Generated chart: {chart2_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate FieldCheck evaluation charts")
    parser.add_argument("--results", type=Path, default=Path("artifacts/evaluation/results.json"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/evaluation"))
    args = parser.parse_args()

    generate_charts(args.results, args.output)


if __name__ == "__main__":
    main()
