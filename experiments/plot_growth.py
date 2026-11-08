# CS 4306 Algorithm Analysis, Fall 2026, Kennesaw State University
# Semester Project: When Does Greedy Fail? Comparing Dynamic Programming and
# Greedy Algorithms for the Knapsack Problem
#
# Author: Ramon Mandujano III (rmanduj1@students.kennesaw.edu)
# Team:   Jonathan Brockob, Alex Rivera Figueroa, Ocean Tshimbalanga
# File:   experiments/plot_growth.py

"""Log-log growth plots with theoretical overlays and fitted slopes.

Reads results/exp1_items.csv and results/exp2_capacity.csv (it does not rerun
any experiment) and writes:

    results/charts/growth_runtime_vs_n.png
    results/charts/growth_runtime_vs_W.png
    results/charts/growth_memory_vs_W.png
    results/growth_slopes.md

Each series gets a log-log slope fitted with numpy.polyfit over its 4 largest
inputs. A slope of 1 means the cost doubles when the input doubles; 0 means it
does not depend on the input at all.

Usage (from the repo root):
    python experiments/plot_growth.py
"""

from __future__ import annotations

import os
import sys
from statistics import median
from typing import Callable, Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import common  # noqa: E402  (also selects the Agg backend)
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

EXP1_CSV = common.results_path("exp1_items.csv")
EXP2_CSV = common.results_path("exp2_capacity.csv")
SLOPES_MD = common.results_path("growth_slopes.md")

CHART_RUNTIME_N = "growth_runtime_vs_n.png"
CHART_RUNTIME_W = "growth_runtime_vs_W.png"
CHART_MEMORY_W = "growth_memory_vs_W.png"

ALGORITHMS = ["dp_2d", "dp_1d", "greedy_ratio", "greedy_value"]
COLORS = {
    "dp_2d": "#3069BE",
    "dp_1d": "#13968F",
    "greedy_ratio": "#B8811A",
    "greedy_value": "#B44141",
}
MARKERS = {"dp_2d": "o", "dp_1d": "s", "greedy_ratio": "^", "greedy_value": "D"}

FIT_POINTS = 4
SUBTITLE = "Solid: measured. Dashed: theoretical growth rate, anchored at the largest input."

Series = Dict[str, Tuple[np.ndarray, np.ndarray]]


# ---------------------------------------------------------------- data

def load_series(path: str, x_key: str, y_of: Callable[[Dict[str, str]], float]) -> Series:
    """Group rows by algorithm and x, take the median y per x, sort by x."""
    grouped: Dict[str, Dict[int, List[float]]] = {}
    for row in common.read_csv(path):
        grouped.setdefault(row["algorithm"], {}).setdefault(int(row[x_key]), []).append(y_of(row))
    out: Series = {}
    for alg, by_x in grouped.items():
        xs = sorted(by_x)
        out[alg] = (np.array(xs, dtype=float), np.array([median(by_x[x]) for x in xs], dtype=float))
    return out


def runtime_ms(row: Dict[str, str]) -> float:
    return float(row["seconds"]) * 1000.0


def memory_mib(row: Dict[str, str]) -> float:
    return float(row["peak_bytes"]) / (1024 * 1024)


def fit_slope(xs: np.ndarray, ys: np.ndarray, k: int = FIT_POINTS) -> float:
    """Slope of log10(y) vs log10(x) over the k largest inputs."""
    slope, _ = np.polyfit(np.log10(xs[-k:]), np.log10(ys[-k:]), 1)
    slope = float(slope)
    return 0.0 if round(slope, 2) == 0 else slope  # print "0.00", never "-0.00"


def anchored(xs: np.ndarray, growth: Callable[[np.ndarray], np.ndarray],
             anchor_x: float, anchor_y: float) -> np.ndarray:
    """Scale growth(x) so the curve passes through (anchor_x, anchor_y)."""
    return growth(xs) * (anchor_y / float(growth(np.array([anchor_x]))[0]))


# ---------------------------------------------------------------- drawing

def _stagger(targets: List[float], gap: float, lo: float, hi: float) -> List[float]:
    """Spread label positions (log10 units) so neighbors are at least `gap` apart."""
    order = sorted(range(len(targets)), key=lambda i: targets[i])
    pos = [targets[i] for i in order]
    for j in range(1, len(pos)):
        pos[j] = max(pos[j], pos[j - 1] + gap)
    if pos and pos[-1] > hi:
        pos[-1] = hi
        for j in range(len(pos) - 2, -1, -1):
            pos[j] = min(pos[j], pos[j + 1] - gap)
    if pos and pos[0] < lo:
        shift = lo - pos[0]
        pos = [p + shift for p in pos]
    out = [0.0] * len(targets)
    for j, i in enumerate(order):
        out[i] = pos[j]
    return out


def growth_chart(series: Series, algorithms: List[str], overlays: List[Tuple[str, str, np.ndarray, np.ndarray]],
                 title: str, xlabel: str, ylabel: str, filename: str) -> Dict[str, float]:
    """Draw one log-log chart; return the fitted slope per algorithm."""
    fig, ax = plt.subplots(figsize=(10, 5.2), dpi=200, facecolor="white")
    ax.set_facecolor("white")
    fig.subplots_adjust(left=0.085, right=0.73, top=0.83, bottom=0.12)

    slopes: Dict[str, float] = {}
    for alg in algorithms:
        xs, ys = series[alg]
        slopes[alg] = fit_slope(xs, ys)
        ax.plot(xs, ys, color=COLORS[alg], marker=MARKERS[alg], markerfacecolor="white",
                markeredgecolor=COLORS[alg], markeredgewidth=1.6, markersize=6,
                linewidth=2, label=common.LABELS[alg], zorder=3)

    for color, label, xs, ys in overlays:
        ax.plot(xs, ys, color=color, linestyle="--", linewidth=1.4, alpha=0.75, label=label, zorder=2)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, which="major", color="#E3E3E3", linewidth=0.8)
    ax.grid(True, which="minor", color="#F2F2F2", linewidth=0.5)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color("#9A9A9A")

    # Freeze the y range (with headroom) so label positions are stable.
    all_y = np.concatenate([series[a][1] for a in algorithms] + [o[3] for o in overlays])
    lo, hi = np.log10(all_y.min()), np.log10(all_y.max())
    pad = 0.08 * (hi - lo)
    ax.set_ylim(10 ** (lo - pad), 10 ** (hi + pad))

    # End-of-line labels just outside the plot area, staggered so they never overlap.
    ylo, yhi = (np.log10(v) for v in ax.get_ylim())
    targets = [float(np.log10(series[a][1][-1])) for a in algorithms]
    placed = _stagger(targets, gap=0.075 * (yhi - ylo), lo=ylo, hi=yhi)
    for alg, y_pos in zip(algorithms, placed):
        xs, ys = series[alg]
        ax.annotate(f"{common.LABELS[alg]}: slope {slopes[alg]:.2f}",
                    xy=(xs[-1], ys[-1]), xycoords="data",
                    xytext=(1.03, 10 ** y_pos), textcoords=ax.get_yaxis_transform(),
                    va="center", ha="left", fontsize=9.5, color=COLORS[alg], fontweight="bold",
                    annotation_clip=False,
                    arrowprops=dict(arrowstyle="-", color=COLORS[alg], alpha=0.45,
                                    linewidth=0.8, shrinkA=0, shrinkB=5))

    ax.legend(loc="upper left", fontsize=9, frameon=True, framealpha=0.92, edgecolor="#DDDDDD")

    fig.text(0.085, 0.945, title, ha="left", va="baseline", fontsize=14, fontweight="bold", color="#1F1F1F")
    fig.text(0.085, 0.895, SUBTITLE, ha="left", va="baseline", fontsize=10, color="#5A5A5A")

    path = common.chart_path(filename)
    fig.savefig(path, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"[plot_growth] wrote {path}")
    return slopes


# ---------------------------------------------------------------- the three charts

def _n_log_n(x: np.ndarray) -> np.ndarray:
    return x * np.log2(x)


def runtime_vs_n() -> Dict[str, float]:
    s = load_series(EXP1_CSV, "n", runtime_ms)
    dense = np.geomspace(min(s[a][0][0] for a in ALGORITHMS), max(s[a][0][-1] for a in ALGORITHMS), 200)
    dp_x, dp_y = s["dp_2d"]
    gr_x, gr_y = s["greedy_ratio"]
    overlays = [
        # W is fixed in this experiment, so O(nW) grows linearly in n.
        (COLORS["dp_2d"], "O(nW) theory, anchored to DP (2D)", dense,
         anchored(dense, lambda x: x, dp_x[-1], dp_y[-1])),
        (COLORS["greedy_ratio"], "O(n log n) theory, anchored to greedy by ratio", dense,
         anchored(dense, _n_log_n, gr_x[-1], gr_y[-1])),
    ]
    return growth_chart(s, ALGORITHMS, overlays,
                        "Runtime vs number of items (W = 1000)",
                        "number of items n (log scale)", "median runtime, ms (log scale)",
                        CHART_RUNTIME_N)


def runtime_vs_w() -> Dict[str, float]:
    s = load_series(EXP2_CSV, "capacity", runtime_ms)
    dense = np.geomspace(min(s[a][0][0] for a in ALGORITHMS), max(s[a][0][-1] for a in ALGORITHMS), 200)
    dp_x, dp_y = s["dp_2d"]
    gr_x, gr_y = s["greedy_ratio"]
    overlays = [
        # n is fixed in this experiment, so O(nW) grows linearly in W ...
        (COLORS["dp_2d"], "O(nW) theory, anchored to DP (2D)", dense,
         anchored(dense, lambda w: w, dp_x[-1], dp_y[-1])),
        # ... and O(n log n) does not depend on W at all: a flat line.
        (COLORS["greedy_ratio"], "O(n log n) theory (flat in W), anchored to greedy by ratio", dense,
         anchored(dense, np.ones_like, gr_x[-1], gr_y[-1])),
    ]
    return growth_chart(s, ALGORITHMS, overlays,
                        "Runtime vs knapsack capacity (n = 200)",
                        "capacity W (log scale)", "median runtime, ms (log scale)",
                        CHART_RUNTIME_W)


def memory_vs_w() -> Dict[str, float]:
    s = load_series(EXP2_CSV, "capacity", memory_mib)
    return growth_chart(s, ["dp_2d", "dp_1d", "greedy_ratio"], [],
                        "Peak memory vs knapsack capacity (n = 200)",
                        "capacity W (log scale)", "peak memory, MiB (log scale)",
                        CHART_MEMORY_W)


# ---------------------------------------------------------------- slope table

def slope_table(vs_n: Dict[str, float], vs_w: Dict[str, float]) -> str:
    lines = [
        "| algorithm | slope vs n | slope vs W |",
        "|---|---|---|",
    ]
    for alg in ALGORITHMS:
        lines.append(f"| {common.LABELS[alg]} | {vs_n[alg]:.2f} | {vs_w[alg]:.2f} |")
    return "\n".join(lines)


def write_slopes(table: str) -> None:
    text = (
        "# Log-log runtime slopes\n\n"
        "Generated by `experiments/plot_growth.py` from `exp1_items.csv` (slope vs n, W = 1000) "
        f"and `exp2_capacity.csv` (slope vs W, n = 200). Each slope is a `numpy.polyfit` line through "
        f"log10(runtime) vs log10(input) over the {FIT_POINTS} largest inputs. "
        "Theory predicts about 1 for DP in both columns, slightly above 1 vs n and 0 vs W for greedy.\n\n"
        f"{table}\n"
    )
    with open(SLOPES_MD, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(f"[plot_growth] wrote {SLOPES_MD}")


def main() -> Dict[str, Dict[str, float]]:
    common.ensure_dirs()
    vs_n = runtime_vs_n()
    vs_w = runtime_vs_w()
    mem_w = memory_vs_w()
    table = slope_table(vs_n, vs_w)
    print("\nLog-log runtime slopes (4 largest inputs):\n")
    print(table)
    print("\nLog-log memory slopes vs W: " +
          ", ".join(f"{common.LABELS[a]} {v:.2f}" for a, v in mem_w.items()))
    write_slopes(table)
    return {"vs_n": vs_n, "vs_w": vs_w, "memory_vs_w": mem_w}


if __name__ == "__main__":
    main()
