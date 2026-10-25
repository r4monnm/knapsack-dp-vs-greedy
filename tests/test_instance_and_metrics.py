# CS 4306 Algorithm Analysis, Fall 2026, Kennesaw State University
# Semester Project: When Does Greedy Fail? Comparing Dynamic Programming and
# Greedy Algorithms for the Knapsack Problem
#
# Author: Ramon Mandujano III (rmanduj1@students.kennesaw.edu)
# Team:   Jonathan Brockob, Alex Rivera Figueroa, Ocean Tshimbalanga
# File:   tests/test_instance_and_metrics.py

"""Tests for instance generation, JSON round trip, and the metric helpers."""

from knapsack import KnapsackInstance, dp_01_knapsack, gap_percent, generate_instance, quality_percent, time_and_memory
from knapsack.instance import CORRELATION_TYPES


def test_generate_is_reproducible():
    a = generate_instance(30, 100, seed=42, correlation="weak")
    b = generate_instance(30, 100, seed=42, correlation="weak")
    assert a.items == b.items


def test_generate_respects_ranges_and_types():
    for kind in CORRELATION_TYPES:
        inst = generate_instance(50, 100, (1, 100), (5, 20), seed=3, correlation=kind)
        assert inst.n == 50
        assert all(5 <= it.weight <= 20 for it in inst.items)
        assert all(it.value >= 1 for it in inst.items)
    strong = generate_instance(50, 100, (1, 100), (5, 20), seed=3, correlation="strong")
    assert all(it.value == it.weight + 10 for it in strong.items)


def test_json_round_trip():
    inst = generate_instance(10, 50, seed=9, correlation="uncorrelated")
    again = KnapsackInstance.from_json(inst.to_json())
    assert again.items == inst.items
    assert again.capacity == inst.capacity
    assert again.name == inst.name


def test_gap_and_quality():
    assert gap_percent(160, 220) == 100.0 * 60 / 220
    assert quality_percent(220, 220) == 100.0
    assert gap_percent(0, 0) == 0.0


def test_time_and_memory_returns_solution():
    inst = generate_instance(40, 200, seed=1)
    m = time_and_memory(dp_01_knapsack, inst)
    assert m.seconds > 0
    assert m.peak_bytes > 0
    assert len(m.all_seconds) == 3
    assert m.solution.value == dp_01_knapsack(inst).value
