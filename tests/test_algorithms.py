# CS 4306 Algorithm Analysis, Fall 2026, Kennesaw State University
# Semester Project: When Does Greedy Fail? Comparing Dynamic Programming and
# Greedy Algorithms for the Knapsack Problem
#
# Author: Ramon Mandujano III (rmanduj1@students.kennesaw.edu)
# Team:   Jonathan Brockob, Alex Rivera Figueroa, Ocean Tshimbalanga
# File:   tests/test_algorithms.py

"""Correctness tests for the solvers, using brute force as the oracle."""

import random

import pytest

from knapsack import (
    Item,
    KnapsackInstance,
    brute_force,
    dp_01_knapsack,
    dp_01_knapsack_1d,
    generate_instance,
    greedy_by_ratio,
    greedy_by_value,
)
from knapsack.instance import CORRELATION_TYPES


def small_instances(count: int = 200, max_n: int = 12):
    """200 random small instances (n <= 12) across all correlation types."""
    rng = random.Random(12345)
    out = []
    for i in range(count):
        n = rng.randint(1, max_n)
        kind = CORRELATION_TYPES[i % len(CORRELATION_TYPES)]
        inst = generate_instance(n, 1, (1, 50), (1, 30), seed=rng.randint(0, 10**9), correlation=kind)
        inst.capacity = rng.randint(1, max(1, inst.total_weight))
        out.append(inst)
    return out


SMALL = small_instances()


@pytest.mark.parametrize("inst", SMALL, ids=lambda i: i.name)
def test_dp_matches_brute_force(inst):
    assert dp_01_knapsack(inst).value == brute_force(inst).value


@pytest.mark.parametrize("inst", SMALL, ids=lambda i: i.name)
def test_dp_1d_equals_dp_2d(inst):
    assert dp_01_knapsack_1d(inst).value == dp_01_knapsack(inst).value


@pytest.mark.parametrize("inst", SMALL, ids=lambda i: i.name)
def test_greedy_never_exceeds_dp(inst):
    opt = dp_01_knapsack(inst).value
    assert greedy_by_ratio(inst).value <= opt
    assert greedy_by_value(inst).value <= opt


@pytest.mark.parametrize("inst", SMALL, ids=lambda i: i.name)
def test_solutions_are_feasible(inst):
    for solver in (dp_01_knapsack, greedy_by_ratio, greedy_by_value, brute_force):
        sol = solver(inst)
        assert sol.is_feasible(inst), solver.__name__
        assert sol.weight <= inst.capacity


def test_dp_backtracking_recovers_chosen_items_on_larger_instance():
    inst = generate_instance(300, 2000, seed=7, correlation="strong")
    sol = dp_01_knapsack(inst)
    assert sol.is_feasible(inst)
    assert sol.value == dp_01_knapsack_1d(inst).value


def test_empty_instance():
    inst = KnapsackInstance(items=[], capacity=10)
    for solver in (dp_01_knapsack, dp_01_knapsack_1d, greedy_by_ratio, greedy_by_value, brute_force):
        assert solver(inst).value == 0


def test_item_heavier_than_capacity_is_skipped():
    inst = KnapsackInstance(items=[Item(100, 50), Item(5, 5)], capacity=10)
    assert dp_01_knapsack(inst).chosen_indices == [1]
    assert greedy_by_ratio(inst).chosen_indices == [1]
    assert greedy_by_value(inst).chosen_indices == [1]


def test_brute_force_rejects_large_n():
    inst = generate_instance(21, 10, seed=1)
    with pytest.raises(ValueError):
        brute_force(inst)
