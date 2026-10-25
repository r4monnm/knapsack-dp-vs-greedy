# CS 4306 Algorithm Analysis, Fall 2026, Kennesaw State University
# Semester Project: When Does Greedy Fail? Comparing Dynamic Programming and
# Greedy Algorithms for the Knapsack Problem
#
# Author: Ramon Mandujano III (rmanduj1@students.kennesaw.edu)
# Team:   Jonathan Brockob, Alex Rivera Figueroa, Ocean Tshimbalanga
# File:   tests/test_failure_cases.py

"""The hand-built cases from experiment 4 must produce the expected values."""

import pytest

from exp4_failure_cases import FAILURE_CASES
from knapsack import brute_force, dp_01_knapsack, greedy_by_ratio, greedy_by_value


@pytest.mark.parametrize("case", FAILURE_CASES, ids=lambda c: c["instance"].name)
def test_failure_case_values(case):
    inst = case["instance"]
    expected = case["expected"]
    assert brute_force(inst).value == expected["optimal"]
    assert dp_01_knapsack(inst).value == expected["optimal"]
    assert greedy_by_ratio(inst).value == expected["greedy_ratio"]
    assert greedy_by_value(inst).value == expected["greedy_value"]


def test_classic_example_picks():
    inst = FAILURE_CASES[0]["instance"]  # capacity 50, (60,10), (100,20), (120,30)
    assert greedy_by_ratio(inst).chosen_indices == [0, 1]
    assert sorted(dp_01_knapsack(inst).chosen_indices) == [1, 2]
