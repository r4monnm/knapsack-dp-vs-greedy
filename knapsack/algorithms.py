# CS 4306 Algorithm Analysis, Fall 2026, Kennesaw State University
# Semester Project: When Does Greedy Fail? Comparing Dynamic Programming and
# Greedy Algorithms for the Knapsack Problem
#
# Author: Ramon Mandujano III (rmanduj1@students.kennesaw.edu)
# Team:   Jonathan Brockob, Alex Rivera Figueroa, Ocean Tshimbalanga
# File:   knapsack/algorithms.py

"""Solvers for the 0/1 knapsack problem.

Every solver has the same signature:

    solve(instance: KnapsackInstance) -> Solution

so the experiments can treat them interchangeably.

    dp_01_knapsack     exact, O(n*W) time, O(n*W) space, recovers items
    dp_01_knapsack_1d  exact, O(n*W) time, O(W) space, value only
    greedy_by_ratio    heuristic, O(n log n), sort by value/weight
    greedy_by_value    heuristic, O(n log n), sort by value
    brute_force        exact, O(2^n), only for n <= 20 (test oracle)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List

from .instance import KnapsackInstance


@dataclass
class Solution:
    """Result of a solver: total value, total weight, and which items."""

    value: int
    weight: int
    chosen_indices: List[int] = field(default_factory=list)

    def is_feasible(self, instance: KnapsackInstance) -> bool:
        """True if the chosen items really fit and the totals are consistent."""
        w = sum(instance.items[i].weight for i in self.chosen_indices)
        v = sum(instance.items[i].value for i in self.chosen_indices)
        return w <= instance.capacity and w == self.weight and v == self.value


# ---------------------------------------------------------------------------
# Dynamic programming
# ---------------------------------------------------------------------------

def dp_01_knapsack(instance: KnapsackInstance) -> Solution:
    """Classic bottom-up DP with a full (n+1) x (W+1) table.

    table[i][w] = best value using only the first i items with capacity w.

    Recurrence:
        table[i][w] = table[i-1][w]                              if weight_i > w
                    = max(table[i-1][w],
                          table[i-1][w - weight_i] + value_i)    otherwise

    After filling the table we walk backwards from table[n][W] to find out
    which items were actually taken (backtracking).
    """
    items = instance.items
    n = len(items)
    W = instance.capacity

    # Row 0 is all zeros: no items means no value.
    table = [[0] * (W + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        value = items[i - 1].value
        weight = items[i - 1].weight
        prev = table[i - 1]
        row = table[i]
        for w in range(W + 1):
            best = prev[w]  # skip item i
            if weight <= w:
                take = prev[w - weight] + value
                if take > best:
                    best = take
            row[w] = best

    # Backtrack: if the value changed between row i-1 and row i at this
    # capacity, item i must have been taken.
    chosen: List[int] = []
    w = W
    for i in range(n, 0, -1):
        if table[i][w] != table[i - 1][w]:
            chosen.append(i - 1)
            w -= items[i - 1].weight
    chosen.reverse()

    total_weight = sum(items[i].weight for i in chosen)
    return Solution(value=table[n][W], weight=total_weight, chosen_indices=chosen)


def dp_01_knapsack_1d(instance: KnapsackInstance) -> Solution:
    """Space-optimized DP using a single rolling array of size W+1.

    Iterating w from high to low means dp[w - weight] still holds the value
    from the previous item row, which keeps the 0/1 rule (each item once).
    This version only returns the optimal value, not the chosen items, so
    it is used for the memory comparison against the 2D table.
    """
    W = instance.capacity
    dp = [0] * (W + 1)
    for item in instance.items:
        weight, value = item.weight, item.value
        for w in range(W, weight - 1, -1):
            candidate = dp[w - weight] + value
            if candidate > dp[w]:
                dp[w] = candidate
    return Solution(value=dp[W], weight=-1, chosen_indices=[])


# ---------------------------------------------------------------------------
# Greedy heuristics
# ---------------------------------------------------------------------------

def _greedy(instance: KnapsackInstance, key: Callable) -> Solution:
    """Shared greedy loop: sort by key (descending), take whatever still fits.

    This is 0/1 greedy, so items are never split. The sort costs
    O(n log n) and the single pass costs O(n).
    """
    order = sorted(range(instance.n), key=lambda i: key(instance.items[i]), reverse=True)
    remaining = instance.capacity
    chosen: List[int] = []
    total_value = 0
    for i in order:
        item = instance.items[i]
        if item.weight <= remaining:
            chosen.append(i)
            remaining -= item.weight
            total_value += item.value
    chosen.sort()
    return Solution(value=total_value, weight=instance.capacity - remaining, chosen_indices=chosen)


def greedy_by_ratio(instance: KnapsackInstance) -> Solution:
    """Greedy on value/weight ratio (the fractional-knapsack ordering).

    Optimal for the fractional problem, but can fail for 0/1 because it
    cannot take part of an item to fill leftover capacity.
    """
    return _greedy(instance, key=lambda item: item.value / item.weight)


def greedy_by_value(instance: KnapsackInstance) -> Solution:
    """Greedy on raw value: grab the most valuable item that still fits."""
    return _greedy(instance, key=lambda item: item.value)


# ---------------------------------------------------------------------------
# Brute force (oracle for tests)
# ---------------------------------------------------------------------------

def brute_force(instance: KnapsackInstance) -> Solution:
    """Try every subset. Exponential, so only allowed for n <= 20."""
    n = instance.n
    if n > 20:
        raise ValueError("brute_force is limited to n <= 20")
    items = instance.items
    W = instance.capacity

    best_value = 0
    best_mask = 0
    for mask in range(1 << n):
        weight = 0
        value = 0
        for i in range(n):
            if mask >> i & 1:
                weight += items[i].weight
                value += items[i].value
        if weight <= W and value > best_value:
            best_value = value
            best_mask = mask

    chosen = [i for i in range(n) if best_mask >> i & 1]
    weight = sum(items[i].weight for i in chosen)
    return Solution(value=best_value, weight=weight, chosen_indices=chosen)


# Name -> solver, used by the experiment scripts for loops and CSV columns.
SOLVERS: Dict[str, Callable[[KnapsackInstance], Solution]] = {
    "dp_2d": dp_01_knapsack,
    "dp_1d": dp_01_knapsack_1d,
    "greedy_ratio": greedy_by_ratio,
    "greedy_value": greedy_by_value,
}
