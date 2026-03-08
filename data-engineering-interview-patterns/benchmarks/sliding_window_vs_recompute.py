"""
Benchmark: Sliding Window vs Recompute

Shows O(n) vs O(n*k) for computing a moving average.
The recompute approach sums k elements for every position.
The sliding window updates incrementally.

Connection: patterns/04_sliding_window/
"""

import random
import time


def moving_avg_recompute(nums: list[int], k: int) -> list[float]:
    """O(n*k): recompute sum for each window position."""
    result = []
    for i in range(len(nums) - k + 1):
        window_sum = sum(nums[i:i + k])
        result.append(window_sum / k)
    return result


def moving_avg_sliding(nums: list[int], k: int) -> list[float]:
    """O(n): maintain running sum, add new element, remove old."""
    result = []
    window_sum = sum(nums[:k])
    result.append(window_sum / k)

    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]
        result.append(window_sum / k)

    return result


def benchmark(sizes: list[int] | None = None, k: int = 1000) -> list[dict]:
    if sizes is None:
        sizes = [10_000, 50_000, 100_000, 500_000]

    results = []
    for n in sizes:
        nums = [random.randint(0, 1000) for _ in range(n)]

        start = time.perf_counter()
        result_recompute = moving_avg_recompute(nums, k)
        t_recompute = time.perf_counter() - start

        start = time.perf_counter()
        result_sliding = moving_avg_sliding(nums, k)
        t_sliding = time.perf_counter() - start

        # Check results match (floating point tolerance)
        assert len(result_recompute) == len(result_sliding)
        for a, b in zip(result_recompute[:100], result_sliding[:100]):
            assert abs(a - b) < 1e-9, f"Mismatch: {a} vs {b}"

        speedup = t_recompute / t_sliding if t_sliding > 0 else float("inf")
        results.append({
            "n": n,
            "k": k,
            "recompute_ms": t_recompute * 1000,
            "sliding_ms": t_sliding * 1000,
            "speedup": speedup,
        })

    return results


def print_results(results: list[dict]) -> None:
    k = results[0]["k"]
    print(f"\n  k={k}")
    print(f"{'n':>12} {'Recompute O(nk) ms':>20} {'Sliding O(n) ms':>17} {'Speedup':>10}")
    print("-" * 63)
    for r in results:
        print(f"{r['n']:>12,} {r['recompute_ms']:>20.2f} {r['sliding_ms']:>17.2f} {r['speedup']:>9.0f}x")
    print()


if __name__ == "__main__":
    print("Sliding Window vs Recompute (Moving Average)")
    print("=" * 63)
    results = benchmark(k=1000)
    print_results(results)

    # Smaller k (difference less dramatic)
    results = benchmark(sizes=[50_000, 100_000, 500_000], k=100)
    print_results(results)


def test_correctness() -> None:
    nums = [1, 2, 3, 4, 5]
    assert moving_avg_recompute(nums, 3) == moving_avg_sliding(nums, 3)


def test_single_element_window() -> None:
    nums = [1, 2, 3, 4, 5]
    assert moving_avg_recompute(nums, 1) == [1.0, 2.0, 3.0, 4.0, 5.0]
    assert moving_avg_sliding(nums, 1) == [1.0, 2.0, 3.0, 4.0, 5.0]


def test_full_window() -> None:
    nums = [1, 2, 3, 4, 5]
    assert moving_avg_recompute(nums, 5) == [3.0]
    assert moving_avg_sliding(nums, 5) == [3.0]


def test_benchmark_runs() -> None:
    results = benchmark(sizes=[1_000, 5_000], k=100)
    assert len(results) == 2
    assert results[1]["sliding_ms"] < results[1]["recompute_ms"]
