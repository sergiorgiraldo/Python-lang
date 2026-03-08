"""
DE Scenario: Finding Partition Boundaries for Backfill

Binary search to find which partitions overlap with a date range.
Left-boundary search applied twice: start and end of range.

Usage:
    uv run python -m patterns.03_binary_search.de_scenarios.partition_boundaries
"""

import bisect
import time
from datetime import date, timedelta


def find_partitions_linear(
    boundaries: list[date],
    start: date,
    end: date,
) -> list[date]:
    """
    Linear scan to find partitions in range. O(n).

    Returns partition start dates where the partition overlaps [start, end].
    Each partition covers [boundaries[i], boundaries[i+1]).
    """
    result = []
    for i in range(len(boundaries) - 1):
        partition_start = boundaries[i]
        partition_end = boundaries[i + 1]
        # Partition overlaps if it starts before range ends
        # and ends after range starts
        if partition_start < end and partition_end > start:
            result.append(partition_start)
    return result


def find_partitions_binary(
    boundaries: list[date],
    start: date,
    end: date,
) -> list[date]:
    """
    Binary search to find partitions in range. O(log n + k) where k = result size.

    Uses bisect to find the first and last relevant partitions, then
    returns the slice between them.
    """
    # Find first partition that could contain data >= start.
    # We want the last partition whose start is <= start.
    # bisect_right(start) gives the first boundary > start,
    # so bisect_right(start) - 1 is the partition containing start.
    first_idx = bisect.bisect_right(boundaries, start) - 1
    first_idx = max(first_idx, 0)

    # Find last partition that could contain data < end.
    # bisect_left(end) gives the first boundary >= end.
    # Partitions before that index might still overlap.
    last_idx = bisect.bisect_left(boundaries, end)
    last_idx = min(last_idx, len(boundaries) - 1)

    # Return partition start dates (each boundary[i] is a partition start)
    return boundaries[first_idx:last_idx]


if __name__ == "__main__":
    # Demo with small dataset
    boundaries = [
        date(2024, 1, 1),
        date(2024, 2, 1),
        date(2024, 3, 1),
        date(2024, 4, 1),
        date(2024, 5, 1),
        date(2024, 6, 1),
    ]

    start = date(2024, 2, 15)
    end = date(2024, 4, 15)

    linear_result = find_partitions_linear(boundaries, start, end)
    binary_result = find_partitions_binary(boundaries, start, end)

    print("Demo: Find partitions for backfill range 2024-02-15 to 2024-04-15")
    print(f"Partition boundaries: {[str(b) for b in boundaries]}")
    print(f"Linear result:  {[str(d) for d in linear_result]}")
    print(f"Binary result:  {[str(d) for d in binary_result]}")
    print()

    # Verify both approaches agree
    assert linear_result == binary_result, "Results don't match"
    print("Both approaches agree.\n")

    # Benchmark at scale
    print("--- Benchmark ---")
    n_partitions = 100_000
    base = date(2000, 1, 1)
    large_boundaries = [base + timedelta(days=i) for i in range(n_partitions)]

    # Query a range in the middle
    query_start = base + timedelta(days=40_000)
    query_end = base + timedelta(days=40_100)

    start_time = time.perf_counter()
    result_lin = find_partitions_linear(large_boundaries, query_start, query_end)
    linear_time = time.perf_counter() - start_time

    start_time = time.perf_counter()
    result_bin = find_partitions_binary(large_boundaries, query_start, query_end)
    binary_time = time.perf_counter() - start_time

    assert result_lin == result_bin
    print(f"Partitions: {n_partitions:,}")
    print("Query range: 100 days in the middle")
    print(f"Result size: {len(result_bin)} partitions")
    print(f"Linear scan: {linear_time:.4f}s")
    print(f"Binary search: {binary_time:.6f}s")
    if binary_time > 0:
        print(f"Speedup: {linear_time / binary_time:.0f}x")
