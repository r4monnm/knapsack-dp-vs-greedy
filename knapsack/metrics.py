# CS 4306 Algorithm Analysis, Fall 2026, Kennesaw State University
# Semester Project: When Does Greedy Fail? Comparing Dynamic Programming and
# Greedy Algorithms for the Knapsack Problem
#
# Author: Ramon Mandujano III (rmanduj1@students.kennesaw.edu)
# Team:   Jonathan Brockob, Alex Rivera Figueroa, Ocean Tshimbalanga
# File:   knapsack/metrics.py

"""Measurement helpers: wall-clock time, peak memory, and solution quality."""

from __future__ import annotations

import statistics
import time
import tracemalloc
from dataclasses import dataclass
from typing import Callable, List

from .algorithms import Solution
from .instance import KnapsackInstance


@dataclass
class Measurement:
    """What time_and_memory returns for one solver on one instance."""

    seconds: float        # median wall time over `runs` timed executions
    peak_bytes: int       # peak memory allocated during one traced execution
    solution: Solution    # the answer, so the caller does not re-solve
    all_seconds: List[float]

    @property
    def peak_kib(self) -> float:
        return self.peak_bytes / 1024

    @property
    def peak_mib(self) -> float:
        return self.peak_bytes / (1024 * 1024)


def time_and_memory(fn: Callable[[KnapsackInstance], Solution], instance: KnapsackInstance, runs: int = 3) -> Measurement:
    """Run `fn(instance)` and report median wall time and peak memory.

    Timing uses time.perf_counter over `runs` executions (median of 3 by
    default) with tracemalloc OFF, because tracing slows code down. Memory
    is then measured in one extra traced run using tracemalloc, which reports
    the peak number of bytes allocated by Python objects during the call.
    """
    times: List[float] = []
    solution = None
    for _ in range(runs):
        start = time.perf_counter()
        solution = fn(instance)
        times.append(time.perf_counter() - start)

    tracemalloc.start()
    tracemalloc.reset_peak()
    fn(instance)
    _current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return Measurement(
        seconds=statistics.median(times),
        peak_bytes=peak,
        solution=solution,
        all_seconds=times,
    )


def gap_percent(greedy_value: int, optimal_value: int) -> float:
    """How far below optimal the greedy answer is, as a percent of optimal.

    0.0 means greedy found the optimum. 25.0 means greedy got 75% of it.
    """
    if optimal_value == 0:
        return 0.0
    return 100.0 * (optimal_value - greedy_value) / optimal_value


def quality_percent(greedy_value: int, optimal_value: int) -> float:
    """Greedy value as a percent of the optimum (100 means optimal)."""
    if optimal_value == 0:
        return 100.0
    return 100.0 * greedy_value / optimal_value
