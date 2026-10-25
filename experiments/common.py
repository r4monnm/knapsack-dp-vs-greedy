# CS 4306 Algorithm Analysis, Fall 2026, Kennesaw State University
# Semester Project: When Does Greedy Fail? Comparing Dynamic Programming and
# Greedy Algorithms for the Knapsack Problem
#
# Author: Ramon Mandujano III (rmanduj1@students.kennesaw.edu)
# Team:   Jonathan Brockob, Alex Rivera Figueroa, Ocean Tshimbalanga
# File:   experiments/common.py

"""Shared paths and small helpers for the experiment scripts.

Each experiment script does `import common` after adding the repo root to
sys.path, so the scripts work with `python experiments/expN.py` from the
repo root without installing the package.
"""

from __future__ import annotations

import csv
import os
import sys
from typing import Dict, Iterable, List

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(REPO_ROOT, "results")
CHARTS_DIR = os.path.join(RESULTS_DIR, "charts")

if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Headless matplotlib: no display needed, PNG files only.
import matplotlib  # noqa: E402

matplotlib.use("Agg")


def ensure_dirs() -> None:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(CHARTS_DIR, exist_ok=True)


def write_csv(path: str, rows: Iterable[Dict], fieldnames: List[str]) -> None:
    rows = list(rows)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: str) -> List[Dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def results_path(filename: str) -> str:
    return os.path.join(RESULTS_DIR, filename)


def chart_path(filename: str) -> str:
    return os.path.join(CHARTS_DIR, filename)


# A small, consistent color set for the charts (works on white backgrounds).
COLORS = {
    "dp_2d": "#1f4e79",
    "dp_1d": "#5b9bd5",
    "greedy_ratio": "#c55a11",
    "greedy_value": "#7f7f7f",
    "reference": "#9e9e9e",
}

LABELS = {
    "dp_2d": "DP (2D table)",
    "dp_1d": "DP (1D rolling array)",
    "greedy_ratio": "Greedy by ratio",
    "greedy_value": "Greedy by value",
}
