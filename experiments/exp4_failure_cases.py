# CS 4306 Algorithm Analysis, Fall 2026, Kennesaw State University
# Semester Project: When Does Greedy Fail? Comparing Dynamic Programming and
# Greedy Algorithms for the Knapsack Problem
#
# Author: Ramon Mandujano III (rmanduj1@students.kennesaw.edu)
# Team:   Jonathan Brockob, Alex Rivera Figueroa, Ocean Tshimbalanga
# File:   experiments/exp4_failure_cases.py

"""Experiment 4: hand-constructed instances where greedy fails.

Each case is small enough to explain on a slide. For every case we print
what each algorithm picks, its value, and its gap to the DP optimum, then
write results/exp4_failure_cases.csv and a bar chart
results/charts/exp4_failure_cases.png.

The cases are also exposed as FAILURE_CASES so the tests can check that the
expected values really come out.
"""

from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import common  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

from knapsack import Item, KnapsackInstance, dp_01_knapsack, gap_percent, greedy_by_ratio, greedy_by_value  # noqa: E402

CSV_PATH = common.results_path("exp4_failure_cases.csv")
CHART_PATH = common.chart_path("exp4_failure_cases.png")


def _case(name: str, capacity: int, pairs, note: str) -> KnapsackInstance:
    inst = KnapsackInstance(items=[Item(v, w) for v, w in pairs], capacity=capacity, name=name)
    inst.metadata["note"] = note
    return inst


# (value, weight) pairs. Expected values are checked by tests/test_failure_cases.py.
FAILURE_CASES = [
    {
        "instance": _case(
            "classic_ratio_fails", 50,
            [(60, 10), (100, 20), (120, 30)],
            "Textbook example. Ratios 6, 5, 4: greedy-by-ratio takes the first two "
            "(value 160, weight 30) and then the 120-item no longer fits. Optimal is 220."),
        "expected": {"optimal": 220, "greedy_ratio": 160, "greedy_value": 220},
    },
    {
        "instance": _case(
            "one_big_item_beats_small_high_ratio", 100,
            [(95, 100), (10, 6), (10, 6), (10, 6), (10, 6)],
            "Four small items have ratio 1.67 and the big one only 0.95, so greedy-by-ratio "
            "fills 24 units with the small items (value 40) and the big item no longer fits. "
            "Optimal is the big item alone (95)."),
        "expected": {"optimal": 95, "greedy_ratio": 40, "greedy_value": 95},
    },
    {
        "instance": _case(
            "greedy_value_fails", 10,
            [(10, 10), (6, 5), (6, 5)],
            "Greedy-by-value grabs the single heavy 10-item and fills the bag (value 10). "
            "Two lighter items give 12."),
        "expected": {"optimal": 12, "greedy_ratio": 12, "greedy_value": 10},
    },
    {
        "instance": _case(
            "both_fail_badly", 100,
            [(60, 50), (60, 50), (31, 20), (65, 100)],
            "Greedy-by-ratio is lured by the (31,20) item (ratio 1.55) and then only one "
            "(60,50) fits: value 91. Greedy-by-value grabs the (65,100) item and the bag is "
            "full: value 65. Optimal is the two (60,50) items: 120."),
        "expected": {"optimal": 120, "greedy_ratio": 91, "greedy_value": 65},
    },
    {
        "instance": _case(
            "greedy_works_fine", 12,
            [(10, 5), (7, 4), (4, 3), (3, 2), (1, 1)],
            "Control case: not everything fits (total weight 15), yet both greedy orders "
            "find the optimum (21) because the items they drop are the right ones."),
        "expected": {"optimal": 21, "greedy_ratio": 21, "greedy_value": 21},
    },
]


def describe(instance: KnapsackInstance, indices) -> str:
    return "[" + ", ".join(f"({instance.items[i].value},{instance.items[i].weight})" for i in indices) + "]"


def run() -> list:
    rows = []
    for case in FAILURE_CASES:
        inst = case["instance"]
        opt = dp_01_knapsack(inst)
        print("=" * 78)
        print(f"Case: {inst.name}   capacity = {inst.capacity}")
        print(f"Items (value,weight): {describe(inst, range(inst.n))}")
        print(f"Note: {inst.metadata['note']}")
        print(f"{'algorithm':16s} {'picks':34s} {'value':>6s} {'weight':>7s} {'gap %':>7s}")
        for name, fn in (("dp_2d", dp_01_knapsack), ("greedy_ratio", greedy_by_ratio), ("greedy_value", greedy_by_value)):
            sol = fn(inst)
            gap = gap_percent(sol.value, opt.value)
            print(f"{name:16s} {describe(inst, sol.chosen_indices):34s} {sol.value:6d} {sol.weight:7d} {gap:7.1f}")
            rows.append({
                "case": inst.name,
                "capacity": inst.capacity,
                "algorithm": name,
                "picks": describe(inst, sol.chosen_indices),
                "value": sol.value,
                "weight": sol.weight,
                "optimal": opt.value,
                "gap_percent": f"{gap:.2f}",
            })
    print("=" * 78)
    return rows


def plot(rows: list) -> None:
    cases = [c["instance"].name for c in FAILURE_CASES]
    algos = ["dp_2d", "greedy_ratio", "greedy_value"]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    width = 0.26
    for j, a in enumerate(algos):
        vals = [100.0 - float(r["gap_percent"]) for r in rows if r["algorithm"] == a]
        xs = [i + (j - 1) * width for i in range(len(cases))]
        ax.bar(xs, vals, width=width, label=common.LABELS[a], color=common.COLORS[a])
    ax.set_xticks(range(len(cases)))
    ax.set_xticklabels([c.replace("_", "\n") for c in cases], fontsize=8)
    ax.set_ylabel("value as % of optimum")
    ax.set_ylim(0, 110)
    ax.axhline(100, color="black", linewidth=0.8, linestyle="--")
    ax.set_title("Experiment 4: hand-built failure cases")
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(CHART_PATH, dpi=150)
    plt.close(fig)


def main() -> None:
    common.ensure_dirs()
    start = time.perf_counter()
    rows = run()
    fields = ["case", "capacity", "algorithm", "picks", "value", "weight", "optimal", "gap_percent"]
    common.write_csv(CSV_PATH, rows, fields)
    plot(rows)
    print(f"[exp4] wrote {CSV_PATH}, {CHART_PATH} in {time.perf_counter() - start:.1f}s")


if __name__ == "__main__":
    main()
