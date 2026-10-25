# CS 4306 Algorithm Analysis, Fall 2026, Kennesaw State University
# Semester Project: When Does Greedy Fail? Comparing Dynamic Programming and
# Greedy Algorithms for the Knapsack Problem
#
# Author: Ramon Mandujano III (rmanduj1@students.kennesaw.edu)
# Team:   Jonathan Brockob, Alex Rivera Figueroa, Ocean Tshimbalanga
# File:   knapsack/instance.py

"""Knapsack problem instances: data classes, random generation, JSON I/O.

An instance is a list of items (each with an integer value and weight)
and an integer capacity. The random generator follows the three classic
Pisinger instance families:

    uncorrelated : values and weights are independent uniform draws.
    weak         : value = weight + small noise. Ratios are close to 1.
    strong       : value = weight + constant. Ratios are even closer,
                   which is where greedy heuristics struggle most.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass(frozen=True)
class Item:
    """A single item with a value (profit) and a weight (cost)."""

    value: int
    weight: int

    @property
    def ratio(self) -> float:
        """Value per unit of weight. Used by greedy_by_ratio."""
        return self.value / self.weight


@dataclass
class KnapsackInstance:
    """A 0/1 knapsack instance: items plus a capacity limit."""

    items: List[Item]
    capacity: int
    name: str = ""
    correlation: str = "uncorrelated"
    seed: Optional[int] = None
    metadata: dict = field(default_factory=dict)

    @property
    def n(self) -> int:
        """Number of items."""
        return len(self.items)

    @property
    def total_weight(self) -> int:
        return sum(item.weight for item in self.items)

    @property
    def total_value(self) -> int:
        return sum(item.value for item in self.items)

    # ---- JSON helpers ----------------------------------------------------

    def to_json(self) -> str:
        """Serialize to a JSON string (handy for saving failure cases)."""
        payload = {
            "name": self.name,
            "capacity": self.capacity,
            "correlation": self.correlation,
            "seed": self.seed,
            "metadata": self.metadata,
            "items": [{"value": it.value, "weight": it.weight} for it in self.items],
        }
        return json.dumps(payload, indent=2)

    @classmethod
    def from_json(cls, text: str) -> "KnapsackInstance":
        """Build an instance from a JSON string produced by to_json."""
        data = json.loads(text)
        items = [Item(int(d["value"]), int(d["weight"])) for d in data["items"]]
        return cls(
            items=items,
            capacity=int(data["capacity"]),
            name=data.get("name", ""),
            correlation=data.get("correlation", "uncorrelated"),
            seed=data.get("seed"),
            metadata=data.get("metadata", {}),
        )

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(self.to_json())

    @classmethod
    def load(cls, path: str) -> "KnapsackInstance":
        with open(path, "r", encoding="utf-8") as fh:
            return cls.from_json(fh.read())


CORRELATION_TYPES = ("uncorrelated", "weak", "strong")


def generate_instance(
    n: int,
    capacity: int,
    value_range: Tuple[int, int] = (1, 100),
    weight_range: Tuple[int, int] = (1, 100),
    seed: Optional[int] = None,
    correlation: Optional[str] = None,
) -> KnapsackInstance:
    """Create a random instance with n items.

    Parameters
    ----------
    n            : number of items.
    capacity     : knapsack capacity W.
    value_range  : (low, high) inclusive bounds for values. For the
                   correlated families only the upper bound R matters: the
                   noise band is R/10, as in Pisinger's generator.
    weight_range : (low, high) inclusive bounds for weights.
    seed         : seed for reproducibility.
    correlation  : None or "uncorrelated", "weak", "strong".
    """
    kind = correlation or "uncorrelated"
    if kind not in CORRELATION_TYPES:
        raise ValueError(f"correlation must be one of {CORRELATION_TYPES}, got {kind!r}")

    rng = random.Random(seed)
    v_lo, v_hi = value_range
    w_lo, w_hi = weight_range
    band = max(1, v_hi // 10)  # Pisinger uses R/10 as the correlation band

    items: List[Item] = []
    for _ in range(n):
        weight = rng.randint(w_lo, w_hi)
        if kind == "uncorrelated":
            value = rng.randint(v_lo, v_hi)
        elif kind == "weak":
            value = weight + rng.randint(-band, band)
        else:  # strong
            value = weight + band
        value = max(1, value)  # keep every value positive
        items.append(Item(value=value, weight=weight))

    return KnapsackInstance(
        items=items,
        capacity=capacity,
        name=f"{kind}_n{n}_W{capacity}_seed{seed}",
        correlation=kind,
        seed=seed,
    )
