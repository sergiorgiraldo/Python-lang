"""
DE Scenario: Single-Pass Aggregation (GROUP BY in Python)

Demonstrates how to implement SQL-style GROUP BY operations
in Python using hash maps. Includes count, sum, average
and multi-metric aggregations.

Pattern: Hash Map - Frequency Count / Group By
"""

import random
import time
from collections import defaultdict
from dataclasses import dataclass


def count_by_key(records: list[dict], key: str) -> dict[str, int]:
    """
    COUNT(*) GROUP BY key.

    Equivalent SQL:
        SELECT key, COUNT(*) FROM table GROUP BY key
    """
    counts: dict[str, int] = defaultdict(int)
    for record in records:
        counts[record[key]] += 1
    return dict(counts)


def sum_by_key(records: list[dict], group_key: str, value_key: str) -> dict[str, float]:
    """
    SUM(value) GROUP BY key.

    Equivalent SQL:
        SELECT group_key, SUM(value_key) FROM table GROUP BY group_key
    """
    totals: dict[str, float] = defaultdict(float)
    for record in records:
        totals[record[group_key]] += record[value_key]
    return dict(totals)


def avg_by_key(records: list[dict], group_key: str, value_key: str) -> dict[str, float]:
    """
    AVG(value) GROUP BY key.

    Tracks sum and count per group, computes average at the end.
    Single pass over the data.
    """
    sums: dict[str, float] = defaultdict(float)
    counts: dict[str, int] = defaultdict(int)

    for record in records:
        k = record[group_key]
        sums[k] += record[value_key]
        counts[k] += 1

    return {k: sums[k] / counts[k] for k in sums}


@dataclass
class GroupStats:
    """Accumulator for multi-metric aggregation."""

    count: int = 0
    total: float = 0.0
    min_val: float = float("inf")
    max_val: float = float("-inf")

    @property
    def avg(self) -> float:
        return self.total / self.count if self.count > 0 else 0.0

    def update(self, value: float) -> None:
        self.count += 1
        self.total += value
        self.min_val = min(self.min_val, value)
        self.max_val = max(self.max_val, value)


def multi_agg_by_key(
    records: list[dict], group_key: str, value_key: str
) -> dict[str, GroupStats]:
    """
    Multiple aggregations in a single pass.

    Equivalent SQL:
        SELECT group_key,
               COUNT(*) as count,
               SUM(value_key) as total,
               AVG(value_key) as avg,
               MIN(value_key) as min_val,
               MAX(value_key) as max_val
        FROM table
        GROUP BY group_key
    """
    groups: dict[str, GroupStats] = defaultdict(GroupStats)

    for record in records:
        groups[record[group_key]].update(record[value_key])

    return dict(groups)


def conditional_count(
    records: list[dict],
    group_key: str,
    conditions: dict[str, callable],
) -> dict[str, dict[str, int]]:
    """
    Conditional aggregation - COUNT with CASE WHEN.

    Equivalent SQL:
        SELECT group_key,
               COUNT(CASE WHEN condition1 THEN 1 END) as label1,
               COUNT(CASE WHEN condition2 THEN 1 END) as label2
        FROM table
        GROUP BY group_key
    """
    results: dict[str, dict[str, int]] = defaultdict(
        lambda: {label: 0 for label in conditions}
    )

    for record in records:
        group = record[group_key]
        for label, condition in conditions.items():
            if condition(record):
                results[group][label] += 1

    return dict(results)


if __name__ == "__main__":
    transactions = [
        {"category": "food", "amount": 12.50, "status": "completed"},
        {"category": "transport", "amount": 35.00, "status": "completed"},
        {"category": "food", "amount": 8.75, "status": "refunded"},
        {"category": "entertainment", "amount": 15.00, "status": "completed"},
        {"category": "food", "amount": 22.00, "status": "completed"},
        {"category": "transport", "amount": 12.00, "status": "pending"},
    ]

    # COUNT
    counts = count_by_key(transactions, "category")
    print(f"Counts: {counts}")
    assert counts["food"] == 3

    # SUM
    sums = sum_by_key(transactions, "category", "amount")
    print(f"Sums: {sums}")
    assert abs(sums["food"] - 43.25) < 0.01

    # AVG
    avgs = avg_by_key(transactions, "category", "amount")
    print(f"Averages: {avgs}")
    assert abs(avgs["transport"] - 23.50) < 0.01

    # Multi-metric
    stats = multi_agg_by_key(transactions, "category", "amount")
    print("\nMulti-metric for 'food':")
    food = stats["food"]
    print(f"  count={food.count}, total={food.total}, avg={food.avg:.2f}")
    print(f"  min={food.min_val}, max={food.max_val}")
    assert food.count == 3

    # Conditional
    cond_counts = conditional_count(
        transactions,
        "category",
        {
            "completed": lambda r: r["status"] == "completed",
            "not_completed": lambda r: r["status"] != "completed",
        },
    )
    print(f"\nConditional counts: {dict(cond_counts)}")
    assert cond_counts["food"]["completed"] == 2
    assert cond_counts["food"]["not_completed"] == 1

    # Benchmark
    print("\n--- Benchmark ---")
    random.seed(42)
    categories = [f"cat_{i}" for i in range(100)]
    large_data = [
        {
            "category": random.choice(categories),
            "amount": random.uniform(1, 100),
        }
        for _ in range(1_000_000)
    ]

    start = time.perf_counter()
    multi_agg_by_key(large_data, "category", "amount")
    elapsed = time.perf_counter() - start
    print(f"Multi-agg 1M records, 100 groups: {elapsed:.3f}s")
