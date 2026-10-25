# CS 4306 Algorithm Analysis, Fall 2026, Kennesaw State University
# Semester Project: When Does Greedy Fail? Comparing Dynamic Programming and
# Greedy Algorithms for the Knapsack Problem
#
# Author: Ramon Mandujano III (rmanduj1@students.kennesaw.edu)
# Team:   Jonathan Brockob, Alex Rivera Figueroa, Ocean Tshimbalanga
# File:   knapsack/__init__.py

"""Knapsack DP vs Greedy: a small, readable library for the CS 4306 project.

Public API:
    Item, KnapsackInstance, generate_instance   (instance.py)
    Solution, dp_01_knapsack, dp_01_knapsack_1d,
    greedy_by_ratio, greedy_by_value, brute_force (algorithms.py)
    time_and_memory, gap_percent, quality_percent (metrics.py)
"""

from .instance import Item, KnapsackInstance, generate_instance
from .algorithms import (
    Solution,
    dp_01_knapsack,
    dp_01_knapsack_1d,
    greedy_by_ratio,
    greedy_by_value,
    brute_force,
)
from .metrics import Measurement, time_and_memory, gap_percent, quality_percent

__all__ = [
    "Item",
    "KnapsackInstance",
    "generate_instance",
    "Solution",
    "dp_01_knapsack",
    "dp_01_knapsack_1d",
    "greedy_by_ratio",
    "greedy_by_value",
    "brute_force",
    "Measurement",
    "time_and_memory",
    "gap_percent",
    "quality_percent",
]
