# When Does Greedy Fail?

> **CS 4306 Algorithm Analysis, Fall 2026, Kennesaw State University**
> Semester Project: When Does Greedy Fail? Comparing Dynamic Programming and Greedy Algorithms for the Knapsack Problem
> Author: Ramon Mandujano III (rmanduj1@students.kennesaw.edu)
> Team: Jonathan Brockob, Alex Rivera Figueroa, Ocean Tshimbalanga


Comparing Dynamic Programming and Greedy Algorithms for the 0/1 Knapsack Problem.

Semester project for **CS 4306 Algorithm Analysis**, Kennesaw State University, Fall 2026.
Presentation and demo: **November 9, 2026**.

**Team:** Jonathan Brockob, Ramon Mandujano, Alex Rivera Figueroa, Ocean Tshimbalanga

## What this project does

The 0/1 knapsack problem asks: given n items with values and weights and a bag of
capacity W, which items give the most value without exceeding W? Dynamic
programming (DP) solves it exactly in O(nW) time. Greedy heuristics run in
O(n log n) but are not guaranteed to be optimal. This repository measures the
trade-off with four experiments and a set of hand-built counterexamples.

Solvers (all share the signature `solve(instance) -> Solution`):

| solver | file | guarantee | time | space |
|---|---|---|---|---|
| `dp_01_knapsack` | `knapsack/algorithms.py` | optimal, recovers items | O(nW) | O(nW) |
| `dp_01_knapsack_1d` | `knapsack/algorithms.py` | optimal value only | O(nW) | O(W) |
| `greedy_by_ratio` | `knapsack/algorithms.py` | heuristic | O(n log n) | O(n) |
| `greedy_by_value` | `knapsack/algorithms.py` | heuristic | O(n log n) | O(n) |
| `brute_force` | `knapsack/algorithms.py` | optimal, n <= 20, tests only | O(2^n) | O(n) |

## Install

Python 3.9 or newer. Only `matplotlib` (charts) and `pytest` (tests) are needed.

```bash
git clone <this repo>
cd knapsack-dp-vs-greedy
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Optional, installs the `knapsack` package in editable mode so it can be imported
from anywhere: `pip install -e .`

## Run the tests

```bash
python -m pytest
```

The tests check that DP matches brute force on 200 random small instances,
that greedy never beats DP, that every solution respects the capacity, that the
1D and 2D DP agree, and that the hand-built failure cases produce the expected
values.

## Run the experiments

From the repo root:

```bash
python experiments/run_all.py        # all four experiments plus results/summary.md
python experiments/exp1_items.py     # or any one of them on its own
python experiments/exp2_capacity.py
python experiments/exp3_quality.py
python experiments/exp4_failure_cases.py
```

`run_all.py` takes about 90 seconds on a laptop. Experiment 2 is the slow one
because the 2D DP table at W = 50,000 is 200 x 50,001 cells.

## Where the outputs land

```
results/
  exp1_items.csv              runtime, peak memory, value per algorithm as n grows
  exp2_capacity.csv           same, as W grows with n fixed
  exp3_quality.csv            one row per random instance (300 rows)
  exp3_quality_summary.csv    mean / min / % optimal per greedy variant and instance type
  exp4_failure_cases.csv      picks, values and gaps for the hand-built cases
  summary.md                  key numbers pulled from the CSVs, ready for the report
  charts/
    exp1_runtime_vs_n.png     log-log runtime with O(nW) and O(n log n) reference lines
    exp1_memory_vs_n.png
    exp2_runtime_vs_capacity.png
    exp2_memory_vs_capacity.png
    exp3_quality_hist.png     histogram of greedy value as % of optimum
    exp4_failure_cases.png
```

Charts are rendered with the matplotlib Agg backend, so no display is needed.

## Project layout

```
knapsack/            the library
  instance.py        Item, KnapsackInstance, generate_instance (Pisinger families), JSON I/O
  algorithms.py      the five solvers listed above
  metrics.py         time_and_memory (perf_counter median of 3, tracemalloc peak), gap_percent
experiments/         one script per experiment plus run_all.py and common.py
tests/               pytest suite
docs/report_outline.md   section-by-section outline of the written report
results/             generated CSVs, charts and summary.md
```

## The experiments in one paragraph each

1. **Items grow, capacity fixed.** W = 1000, n = 10 to 2000. DP runtime grows
   linearly in n (because W is constant), greedy grows as n log n but is two
   to three orders of magnitude faster in absolute terms.
2. **Capacity grows, items fixed.** n = 200, W = 100 to 50,000. DP runtime and
   memory grow linearly with W; greedy does not depend on W at all. The 1D
   rolling array removes the memory blow-up but not the time.
3. **Solution quality.** 300 random instances, 100 each uncorrelated, weakly
   correlated and strongly correlated. Greedy-by-ratio is usually within a few
   percent of optimal and does worst on strongly correlated instances;
   greedy-by-value is much worse.
4. **Failure cases.** Small hand-built instances, including the textbook
   example (capacity 50, items (60,10), (100,20), (120,30)) where
   greedy-by-ratio gets 160 instead of 220, one where a single big item beats
   several small high-ratio items, one where greedy-by-value fails, and one
   where both fail badly.

## Reproducibility

Every random instance is created from a fixed seed, so rerunning the
experiments gives the same instances and the same values. Runtimes and memory
will of course vary by machine.
