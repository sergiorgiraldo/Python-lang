"""
Benchmark: Binary Search vs Linear Search

Shows O(log n) vs O(n) on sorted arrays.
At n=10M, binary search is ~1000x faster.

Connection: patterns/03_binary_search/
"""

import bisect
import random
import time


def linear_search(arr: list[int], target: int) -> int:
    """O(n): scan every element."""
    for i, val in enumerate(arr):
        if val == target:
            return i
    return -1


def binary_search(arr: list[int], target: int) -> int:
    """O(log n): halve the search space each step."""
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def benchmark(sizes: list[int] | None = None) -> list[dict]:
    """Run the benchmark across multiple input sizes."""
    if sizes is None:
        sizes = [10_000, 100_000, 1_000_000, 10_000_000]

    results = []
    for n in sizes:
        arr = list(range(n))
        # Search for a value near the end (worst case for linear)
        target = n - 7

        # Linear search
        start = time.perf_counter()
        idx_linear = linear_search(arr, target)
        t_linear = time.perf_counter() - start

        # Binary search
        start = time.perf_counter()
        idx_binary = binary_search(arr, target)
        t_binary = time.perf_counter() - start

        assert idx_linear == idx_binary, "Results don't match"

        speedup = t_linear / t_binary if t_binary > 0 else float("inf")
        results.append({
            "n": n,
            "linear_ms": t_linear * 1000,
            "binary_ms": t_binary * 1000,
            "speedup": speedup,
        })

    return results


def print_results(results: list[dict]) -> None:
    """Print benchmark results as a table."""
    print(f"\n{'n':>12} {'Linear (ms)':>12} {'Binary (ms)':>12} {'Speedup':>10}")
    print("-" * 50)
    for r in results:
        print(f"{r['n']:>12,} {r['linear_ms']:>12.3f} {r['binary_ms']:>12.4f} {r['speedup']:>9.0f}x")
    print()


if __name__ == "__main__":
    print("Binary Search vs Linear Search")
    print("=" * 50)
    results = benchmark()
    print_results(results)


# --- Tests ---

def test_correctness() -> None:
    """Both approaches find the same element."""
    arr = list(range(1000))
    for target in [0, 500, 999]:
        assert linear_search(arr, target) == binary_search(arr, target)


def test_not_found() -> None:
    """Both return -1 for missing element."""
    arr = [1, 3, 5, 7, 9]
    assert linear_search(arr, 4) == -1
    assert binary_search(arr, 4) == -1


def test_benchmark_runs() -> None:
    """Benchmark completes and binary is faster for large n."""
    results = benchmark(sizes=[1_000, 100_000])
    assert len(results) == 2
    # Binary should be faster at 100K
    assert results[1]["binary_ms"] < results[1]["linear_ms"]
