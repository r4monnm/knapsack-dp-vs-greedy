# CS 4306 Algorithm Analysis, Fall 2026, Kennesaw State University
# Semester Project: When Does Greedy Fail? Comparing Dynamic Programming and
# Greedy Algorithms for the Knapsack Problem
#
# Author: Ramon Mandujano III (rmanduj1@students.kennesaw.edu)
# Team:   Jonathan Brockob, Alex Rivera Figueroa, Ocean Tshimbalanga
# File:   experiments/exp1_items.py

"""Experiment 1: fixed capacity, growing number of items n.

Measures runtime, peak memory and solution value for the DP and both greedy
heuristics as n grows. Writes results/exp1_items.csv and two charts:
    results/charts/exp1_runtime_vs_n.png   (log-log, with reference lines)
    results/charts/exp1_memory_vs_n.png
"""

from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import common  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

from knapsack import generate_instance, time_and_memory  # noqa: E402
from knapsack.algorithms import SOLVERS  # noqa: E402

N_VALUES = [10, 20, 50, 100, 200, 500, 1000, 2000]
CAPACITY = 1000
VALUE_RANGE = (1, 100)
WEIGHT_RANGE = (1, 100)
SEED = 4306
ALGOS = ["dp_2d", "dp_1d", "greedy_ratio", "greedy_value"]

CSV_PATH = common.results_path("exp1_items.csv")
RUNTIME_CHART = common.chart_path("exp1_runtime_vs_n.png")
MEMORY_CHART = common.chart_path("exp1_memory_vs_n.png")


def run() -> list:
    rows = []
    for n in N_VALUES:
        inst = generate_instance(n, CAPACITY, VALUE_RANGE, WEIGHT_RANGE, seed=SEED + n)
        optimal = None
        for name in ALGOS:
            m = time_and_memory(SOLVERS[name], inst)
            if name == "dp_2d":
                optimal = m.solution.value
            rows.append({
                "n": n,
                "capacity": CAPACITY,
                "algorithm": name,
                "seconds": f"{m.seconds:.6f}",
                "peak_bytes": m.peak_bytes,
                "value": m.solution.value,
                "optimal_value": optimal,
                "quality_percent": f"{100.0 * m.solution.value / optimal:.3f}",
            })
            print(f"n={n:5d}  {name:13s}  {m.seconds*1000:9.2f} ms  {m.peak_kib:10.1f} KiB  value={m.solution.value}")
    return rows


def plot(rows: list) -> None:
    by_algo = {a: [r for r in rows if r["algorithm"] == a] for a in ALGOS}

    # Runtime chart (log-log) with reference growth lines anchored at the
    # measured time for the largest n (small n is dominated by fixed overhead).
    fig, ax = plt.subplots(figsize=(7.5, 5))
    for a in ALGOS:
        xs = [int(r["n"]) for r in by_algo[a]]
        ys = [float(r["seconds"]) for r in by_algo[a]]
        ax.plot(xs, ys, marker="o", label=common.LABELS[a], color=common.COLORS[a])

    import math
    n0 = N_VALUES[-1]
    xs = N_VALUES
    dp0 = float(by_algo["dp_2d"][-1]["seconds"])
    gr0 = float(by_algo["greedy_ratio"][-1]["seconds"])
    # O(nW) with W fixed grows linearly in n.
    ax.plot(xs, [dp0 * (x / n0) for x in xs], linestyle="--", color=common.COLORS["reference"],
            label="reference O(nW), W fixed")
    ax.plot(xs, [gr0 * (x * math.log2(x)) / (n0 * math.log2(n0)) for x in xs], linestyle=":",
            color=common.COLORS["reference"], label="reference O(n log n)")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("number of items n (capacity W = %d)" % CAPACITY)
    ax.set_ylabel("median runtime (seconds)")
    ax.set_title("Experiment 1: runtime vs number of items")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(RUNTIME_CHART, dpi=150)
    plt.close(fig)

    # Memory chart
    fig, ax = plt.subplots(figsize=(7.5, 5))
    for a in ALGOS:
        xs = [int(r["n"]) for r in by_algo[a]]
        ys = [int(r["peak_bytes"]) / 1024 for r in by_algo[a]]
        ax.plot(xs, ys, marker="o", label=common.LABELS[a], color=common.COLORS[a])
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("number of items n (capacity W = %d)" % CAPACITY)
    ax.set_ylabel("peak memory (KiB, tracemalloc)")
    ax.set_title("Experiment 1: peak memory vs number of items")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(MEMORY_CHART, dpi=150)
    plt.close(fig)


def main() -> None:
    common.ensure_dirs()
    start = time.perf_counter()
    rows = run()
    fields = ["n", "capacity", "algorithm", "seconds", "peak_bytes", "value", "optimal_value", "quality_percent"]
    common.write_csv(CSV_PATH, rows, fields)
    plot(rows)
    print(f"[exp1] wrote {CSV_PATH}, {RUNTIME_CHART}, {MEMORY_CHART} in {time.perf_counter() - start:.1f}s")


if __name__ == "__main__":
    main()
