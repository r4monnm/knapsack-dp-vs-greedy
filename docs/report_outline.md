# Report outline

**When Does Greedy Fail? Comparing Dynamic Programming and Greedy Algorithms for the Knapsack Problem**

CS 4306 Algorithm Analysis, Kennesaw State University, Fall 2026
Jonathan Brockob, Ramon Mandujano, Alex Rivera Figueroa, Ocean Tshimbalanga

Every `[TODO: ...]` below is a placeholder. The numbers come from
`results/summary.md` after running `python experiments/run_all.py`; the
charts are in `results/charts/`.

---

## 1. Problem Statement

- Define the 0/1 knapsack problem: n items, item i has value v_i and weight w_i,
  capacity W, choose a subset maximizing total value with total weight <= W.
- Why it matters: resource allocation, budgeting, cargo loading, cutting stock.
- The question we answer: when is the fast greedy heuristic good enough, and
  when does it fail? What does the exact DP cost in time and memory to get the
  guarantee?
- [TODO: one paragraph, cite the textbook definition]

## 2. Background

- NP-hardness of 0/1 knapsack and why DP is pseudo-polynomial (O(nW) depends on
  the numeric value of W, not on its bit length).
- Greedy for the fractional knapsack is optimal (sort by value/weight); explain
  why the same ordering can fail for 0/1 (cannot take part of an item).
- The two greedy variants we test: by ratio and by raw value.
- Pisinger instance families (uncorrelated, weakly correlated, strongly
  correlated) and why strongly correlated instances are hard for greedy.
- [TODO: 2 or 3 references]

## 3. Methodology

- Implementation: Python 3, package `knapsack/`.
  - `dp_01_knapsack`: 2D table (n+1) x (W+1) with backtracking.
  - `dp_01_knapsack_1d`: rolling array of size W+1 (value only).
  - `greedy_by_ratio`, `greedy_by_value`: sort then one pass.
  - `brute_force` as the test oracle for n <= 12.
- Measurement (`knapsack/metrics.py`): wall time with `time.perf_counter`,
  median of 3 runs; peak memory with `tracemalloc` in a separate run.
- Instance generation (`knapsack/instance.py`): fixed seeds for
  reproducibility, values and weights in [1, 100] unless stated.
- Testing: 815 pytest cases (DP = brute force on 200 random instances,
  greedy <= DP, feasibility, 1D = 2D, failure cases).
- Hardware used for the reported numbers: [TODO: CPU, RAM, Python version, OS]

## 4. Evaluation

### Experiment 1: fixed capacity, growing n (`results/exp1_items.csv`)

- Setup: W = 1000, n in {10, 20, 50, 100, 200, 500, 1000, 2000}.
- Figure: `results/charts/exp1_runtime_vs_n.png` (log-log, with O(nW) and
  O(n log n) reference lines) and `results/charts/exp1_memory_vs_n.png`.
- [TODO: DP runtime at n = 2000, greedy runtime at n = 2000, ratio between them]
- [TODO: comment on the slope of each curve on the log-log plot]

### Experiment 2: fixed n, growing capacity (`results/exp2_capacity.csv`)

- Setup: n = 200, W in {100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000}.
- Figure: `results/charts/exp2_runtime_vs_capacity.png` and
  `results/charts/exp2_memory_vs_capacity.png`.
- [TODO: DP 2D runtime and memory at W = 50000; 1D memory at W = 50000;
  greedy runtime, which should be flat]
- Point to make: greedy does not depend on W at all; DP cost is driven by W.

### Experiment 3: solution quality (`results/exp3_quality.csv`, `results/exp3_quality_summary.csv`)

- Setup: 300 random instances, 100 per correlation type, n in [20, 100],
  capacity between 20% and 60% of the total weight.
- Figure: `results/charts/exp3_quality_hist.png`.
- Table: mean %, min %, and % of instances where greedy was optimal, for each
  greedy variant and each instance type (copy from `summary.md`).
- [TODO: greedy-by-ratio mean % and % optimal overall; same for greedy-by-value]
- [TODO: which instance type hurts greedy most and why]

### Experiment 4: hand-built failure cases (`results/exp4_failure_cases.csv`)

- Figure: `results/charts/exp4_failure_cases.png`.
- Walk through each case with the picks of each algorithm:
  1. Classic: capacity 50, items (60,10), (100,20), (120,30). Greedy-by-ratio
     = 160, optimal = 220 (gap 27.3%).
  2. One big item beats several small high-ratio items: greedy-by-ratio = 40,
     optimal = 95 (gap 57.9%).
  3. Greedy-by-value fails: greedy-by-value = 10, optimal = 12 (gap 16.7%).
  4. Both fail badly: greedy-by-ratio = 91, greedy-by-value = 65, optimal = 120.
  5. Control case where both greedy orders are optimal.
- [TODO: explain the mechanism in each case: leftover capacity that cannot be
  filled, or a lure item with a high ratio that blocks the best combination]

## 5. Results

- Summarize the four experiments in one table and 3 or 4 sentences each.
- [TODO: paste the headline numbers from `results/summary.md`]
- Observation: greedy-by-ratio is close to optimal on average but is rarely
  exactly optimal; greedy-by-value is much worse.
- Observation: the DP memory problem is solved by the 1D array, the time
  problem is not.

## 6. Complexity Analysis

- Theoretical: DP O(nW) time, O(nW) or O(W) space; greedy O(n log n) time,
  O(n) space; brute force O(2^n).
- Measured growth vs theory:
  - Experiment 1 (W fixed): fit the slope of log(time) vs log(n). DP should be
    close to 1 (linear in n since W is constant); greedy slightly above 1
    (n log n). [TODO: slopes from the CSV]
  - Experiment 2 (n fixed): DP slope vs log(W) should be close to 1; greedy
    slope close to 0. [TODO: slopes from the CSV]
- Explain why DP is pseudo-polynomial and what that means for large W
  (for example W = 10^9 would be infeasible even though n is small).
- Discuss constant factors: Python lists, tracemalloc overhead, the cost of
  backtracking.

## 7. Conclusion

- Answer the title question: greedy fails when leftover capacity cannot be
  filled by the remaining items, which happens most on strongly correlated
  instances and whenever a high-ratio item blocks a better combination.
- Practical guidance: use greedy-by-ratio when W is huge and a few percent
  loss is acceptable; use DP (1D if only the value is needed) when W is
  moderate and optimality matters; never use greedy-by-value.
- Future work: FPTAS (value scaling), branch and bound, greedy plus the
  "best single item" fix which gives a 1/2 approximation guarantee.
- [TODO: team reflection, division of work]

## Appendix

- How to reproduce: `python -m pytest`, then `python experiments/run_all.py`.
- Full CSVs and the generated `summary.md` in `results/`.
