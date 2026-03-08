"""
DE Scenario: Binary Search on Answer - Resource Allocation

Find the minimum number of parallel workers to complete all tasks
within a deadline. Same pattern as LeetCode 875.

Usage:
    uv run python -m patterns.03_binary_search.de_scenarios.search_on_answer
"""

import heapq
import math
import time


def can_finish(tasks: list[int], num_workers: int, deadline: int) -> bool:
    """
    Check if num_workers can finish all tasks by the deadline.

    Greedy: assign each task to the worker that finishes earliest.
    Uses a min-heap of worker finish times.

    Time: O(n log w) where w = num_workers
    """
    if num_workers <= 0:
        return False
    if num_workers >= len(tasks):
        return max(tasks) <= deadline

    # Min-heap: each entry is a worker's current finish time
    workers = [0] * num_workers
    heapq.heapify(workers)

    # Sort tasks largest-first for tighter packing
    for task in sorted(tasks, reverse=True):
        earliest = heapq.heappop(workers)
        finish = earliest + task
        if finish > deadline:
            return False
        heapq.heappush(workers, finish)

    return True


def min_workers_binary(tasks: list[int], deadline: int) -> int:
    """
    Binary search on the number of workers. O(n log n * log W).

    Search [1, len(tasks)]. For each candidate count, simulate
    whether they can finish on time.
    """
    left, right = 1, len(tasks)

    while left < right:
        mid = (left + right) // 2
        if can_finish(tasks, mid, deadline):
            right = mid  # This many works, try fewer
        else:
            left = mid + 1  # Not enough, need more

    return left


def min_workers_linear(tasks: list[int], deadline: int) -> int:
    """Try every worker count from 1 upward. O(n^2 log n) worst case."""
    for w in range(1, len(tasks) + 1):
        if can_finish(tasks, w, deadline):
            return w
    return len(tasks)


def min_workers_formula(tasks: list[int], deadline: int) -> int:
    """
    Quick lower-bound estimate: ceil(total_work / deadline).

    This ignores task granularity (you can't split a task across
    workers) so it's a lower bound. Useful as a sanity check
    or starting point.
    """
    return math.ceil(sum(tasks) / deadline)


if __name__ == "__main__":
    # Demo
    tasks = [10, 15, 20, 25, 30]
    deadline = 35

    print("Demo: Minimum workers for tasks", tasks, f"with deadline={deadline}")
    result = min_workers_binary(tasks, deadline)
    estimate = min_workers_formula(tasks, deadline)
    print(f"Binary search result: {result} workers")
    print(f"Lower bound estimate: {estimate} workers")
    print(f"Linear search result: {min_workers_linear(tasks, deadline)} workers")
    print()

    # Verify all tasks finish
    assert can_finish(tasks, result, deadline)
    if result > 1:
        assert not can_finish(tasks, result - 1, deadline)
    print("Verified: result is the minimum.\n")

    # Benchmark
    print("--- Benchmark ---")
    import random

    random.seed(42)
    for n_tasks in [100, 500, 1_000, 5_000]:
        tasks = [random.randint(10, 100) for _ in range(n_tasks)]
        dl = int(sum(tasks) * 0.3)  # Tight deadline

        start_time = time.perf_counter()
        result_bin = min_workers_binary(tasks, dl)
        bin_time = time.perf_counter() - start_time

        start_time = time.perf_counter()
        result_lin = min_workers_linear(tasks, dl)
        lin_time = time.perf_counter() - start_time

        assert result_bin == result_lin
        print(
            f"Tasks: {n_tasks:>5,} | Workers needed: {result_bin:>4} | "
            f"Binary: {bin_time:.4f}s | Linear: {lin_time:.4f}s | "
            f"Speedup: {lin_time / max(bin_time, 0.0001):.1f}x"
        )
