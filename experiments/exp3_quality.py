# CS 4306 Algorithm Analysis, Fall 2026, Kennesaw State University
# Semester Project: When Does Greedy Fail? Comparing Dynamic Programming and
# Greedy Algorithms for the Knapsack Problem
#
# Author: Ramon Mandujano III (rmanduj1@students.kennesaw.edu)
# Team:   Jonathan Brockob, Alex Rivera Figueroa, Ocean Tshimbalanga
# File:   experiments/exp3_quality.py

"""Experiment 3: solution quality of greedy versus the DP optimum.

Generates 300 random instances (100 each of uncorrelated, weakly correlated
and strongly correlated) and records each greedy value as a percent of the
DP optimum. Writes:
    results/exp3_quality.csv           one row per instance
    results/exp3_quality_summary.csv   mean / min / % optimal per variant and type
    results/charts/exp3_quality_hist.png
"""

from __future__ import annotations

import os
import random
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import common  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

from knapsack import dp_01_knapsack, generate_instance, greedy_by_ratio, greedy_by_value, quality_percent  # noqa: E402
from knapsack.instance import CORRELATION_TYPES  # noqa: E402

INSTANCES_PER_TYPE = 100
N_RANGE = (20, 100)       # random n per instance
VALUE_RANGE = (1, 100)
WEIGHT_RANGE = (1, 100)
SEED = 4306

CSV_PATH = common.results_path("exp3_quality.csv")
SUMMARY_PATH = common.results_path("exp3_quality_summary.csv")
CHART_PATH = common.chart_path("exp3_quality_hist.png")

GREEDIES = {"greedy_ratio": greedy_by_ratio, "greedy_value": greedy_by_value}


def run() -> list:
    rng = random.Random(SEED)
    rows = []
    k = 0
    for kind in CORRELATION_TYPES:
        for _ in range(INSTANCES_PER_TYPE):
            n = rng.randint(*N_RANGE)
            seed = rng.randint(0, 10**9)
            inst = generate_instance(n, 1, VALUE_RANGE, WEIGHT_RANGE, seed=seed, correlation=kind)
            # Capacity is a random fraction (20% to 60%) of the total weight,
            # so the knapsack is always a real constraint.
            inst.capacity = max(1, int(inst.total_weight * rng.uniform(0.2, 0.6)))
            opt = dp_01_knapsack(inst).value
            row = {"id": k, "correlation": kind, "n": n, "capacity": inst.capacity, "seed": seed, "optimal": opt}
            for name, fn in GREEDIES.items():
                val = fn(inst).value
                row[f"{name}_value"] = val
                row[f"{name}_quality"] = f"{quality_percent(val, opt):.4f}"
            rows.append(row)
            k += 1
        print(f"[exp3] {kind}: {INSTANCES_PER_TYPE} instances done")
    return rows


def summarize(rows: list) -> list:
    """Mean, min, and percent-optimal of greedy quality per variant and type."""
    summary = []
    groups = list(CORRELATION_TYPES) + ["all"]
    for name in GREEDIES:
        for kind in groups:
            subset = [r for r in rows if kind == "all" or r["correlation"] == kind]
            q = [float(r[f"{name}_quality"]) for r in subset]
            summary.append({
                "greedy": name,
                "correlation": kind,
                "instances": len(q),
                "mean_quality_percent": f"{statistics.mean(q):.3f}",
                "min_quality_percent": f"{min(q):.3f}",
                "median_quality_percent": f"{statistics.median(q):.3f}",
                "percent_optimal": f"{100.0 * sum(1 for x in q if x >= 100.0 - 1e-9) / len(q):.1f}",
            })
    return summary


def plot(rows: list) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
    colors = {"uncorrelated": "#1f4e79", "weak": "#5b9bd5", "strong": "#c55a11"}
    for ax, name in zip(axes, GREEDIES):
        data = [[float(r[f"{name}_quality"]) for r in rows if r["correlation"] == kind] for kind in CORRELATION_TYPES]
        lo = min(min(d) for d in data)
        bins = 30
        ax.hist(data, bins=bins, range=(min(lo, 99.0), 100.0), stacked=True,
                label=list(CORRELATION_TYPES), color=[colors[k] for k in CORRELATION_TYPES])
        ax.set_title(common.LABELS[name])
        ax.set_xlabel("greedy value as % of DP optimum")
        ax.grid(True, alpha=0.3)
    axes[0].set_ylabel("number of instances")
    axes[0].legend(title="instance type", fontsize=8)
    fig.suptitle("Experiment 3: greedy solution quality on %d random instances" % len(rows))
    fig.tight_layout()
    fig.savefig(CHART_PATH, dpi=150)
    plt.close(fig)


def print_summary(summary: list) -> None:
    print(f"{'greedy':13s} {'type':13s} {'mean %':>8s} {'min %':>8s} {'optimal %':>10s}")
    for s in summary:
        print(f"{s['greedy']:13s} {s['correlation']:13s} {s['mean_quality_percent']:>8s} "
              f"{s['min_quality_percent']:>8s} {s['percent_optimal']:>10s}")


def main() -> None:
    common.ensure_dirs()
    start = time.perf_counter()
    rows = run()
    fields = ["id", "correlation", "n", "capacity", "seed", "optimal",
              "greedy_ratio_value", "greedy_ratio_quality", "greedy_value_value", "greedy_value_quality"]
    common.write_csv(CSV_PATH, rows, fields)
    summary = summarize(rows)
    common.write_csv(SUMMARY_PATH, summary, list(summary[0].keys()))
    plot(rows)
    print_summary(summary)
    print(f"[exp3] wrote {CSV_PATH}, {SUMMARY_PATH}, {CHART_PATH} in {time.perf_counter() - start:.1f}s")


if __name__ == "__main__":
    main()
