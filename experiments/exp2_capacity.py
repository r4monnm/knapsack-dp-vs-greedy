# CS 4306 Algorithm Analysis, Fall 2026, Kennesaw State University
# Semester Project: When Does Greedy Fail? Comparing Dynamic Programming and
# Greedy Algorithms for the Knapsack Problem
#
# Author: Ramon Mandujano III (rmanduj1@students.kennesaw.edu)
# Team:   Jonathan Brockob, Alex Rivera Figueroa, Ocean Tshimbalanga
# File:   experiments/exp2_capacity.py

"""Experiment 2: fixed number of items n, growing capacity W.

Shows that DP runtime and memory grow with W (pseudo-polynomial O(nW))
while greedy does not depend on W at all. Writes results/exp2_capacity.csv
and two charts:
    results/charts/exp2_runtime_vs_capacity.png
    results/charts/exp2_memory_vs_capacity.png
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

N_ITEMS = 200
CAPACITIES = [100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000]
VALUE_RANGE = (1, 100)
WEIGHT_RANGE = (1, 500)   # wider weights so large capacities are still meaningful
SEED = 4306
ALGOS = ["dp_2d", "dp_1d", "greedy_ratio", "greedy_value"]

CSV_PATH = common.results_path("exp2_capacity.csv")
RUNTIME_CHART = common.chart_path("exp2_runtime_vs_capacity.png")
MEMORY_CHART = common.chart_path("exp2_memory_vs_capacity.png")


def run() -> list:
    rows = []
    # Same item set for every capacity so only W changes.
    base = generate_instance(N_ITEMS, CAPACITIES[0], VALUE_RANGE, WEIGHT_RANGE, seed=SEED)
    for W in CAPACITIES:
        inst = generate_instance(N_ITEMS, W, VALUE_RANGE, WEIGHT_RANGE, seed=SEED)
        inst.items = base.items
        optimal = None
        for name in ALGOS:
            m = time_and_memory(SOLVERS[name], inst)
            if name == "dp_2d":
                optimal = m.solution.value
            rows.append({
                "n": N_ITEMS,
                "capacity": W,
                "algorithm": name,
                "seconds": f"{m.seconds:.6f}",
                "peak_bytes": m.peak_bytes,
                "value": m.solution.value,
                "optimal_value": optimal,
                "quality_percent": f"{100.0 * m.solution.value / optimal:.3f}",
            })
            print(f"W={W:6d}  {name:13s}  {m.seconds*1000:9.2f} ms  {m.peak_mib:8.2f} MiB  value={m.solution.value}")
    return rows


def plot(rows: list) -> None:
    by_algo = {a: [r for r in rows if r["algorithm"] == a] for a in ALGOS}

    fig, ax = plt.subplots(figsize=(7.5, 5))
    for a in ALGOS:
        xs = [int(r["capacity"]) for r in by_algo[a]]
        ys = [float(r["seconds"]) for r in by_algo[a]]
        ax.plot(xs, ys, marker="o", label=common.LABELS[a], color=common.COLORS[a])
    # Reference line anchored at the largest W, where overhead is negligible.
    W0 = CAPACITIES[-1]
    dp0 = float(by_algo["dp_2d"][-1]["seconds"])
    ax.plot(CAPACITIES, [dp0 * (W / W0) for W in CAPACITIES], linestyle="--",
            color=common.COLORS["reference"], label="reference O(nW), n fixed")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("capacity W (n = %d items)" % N_ITEMS)
    ax.set_ylabel("median runtime (seconds)")
    ax.set_title("Experiment 2: runtime vs capacity")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(RUNTIME_CHART, dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.5, 5))
    for a in ALGOS:
        xs = [int(r["capacity"]) for r in by_algo[a]]
        ys = [int(r["peak_bytes"]) / 1024 for r in by_algo[a]]
        ax.plot(xs, ys, marker="o", label=common.LABELS[a], color=common.COLORS[a])
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("capacity W (n = %d items)" % N_ITEMS)
    ax.set_ylabel("peak memory (KiB, tracemalloc)")
    ax.set_title("Experiment 2: peak memory vs capacity")
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
    print(f"[exp2] wrote {CSV_PATH}, {RUNTIME_CHART}, {MEMORY_CHART} in {time.perf_counter() - start:.1f}s")


if __name__ == "__main__":
    main()
