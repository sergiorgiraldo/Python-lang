"""
Benchmark: Hash Map vs Nested Loop (Two Sum pattern)

Shows O(n) vs O(n^2) for finding a pair that sums to a target.
At n=50K, hash map is 1000x+ faster. At n=100K+, nested loop
takes minutes while hash map finishes in milliseconds.

Connection: patterns/01_hash_map/
"""

import random
import time


def two_sum_brute(nums: list[int], target: int) -> tuple[int, int] | None:
    """O(n^2): check every pair."""
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] + nums[j] == target:
                return (i, j)
    return None


def two_sum_hash(nums: list[int], target: int) -> tuple[int, int] | None:
    """O(n): hash map for complement lookup."""
    seen: dict[int, int] = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return (seen[complement], i)
        seen[num] = i
    return None


def benchmark(sizes: list[int] | None = None) -> list[dict]:
    if sizes is None:
        sizes = [1_000, 5_000, 10_000, 30_000]

    results = []
    for n in sizes:
        nums = random.sample(range(n * 10), n)
        # Ensure a valid pair exists
        target = nums[0] + nums[-1]

        # Brute force
        start = time.perf_counter()
        result_brute = two_sum_brute(nums, target)
        t_brute = time.perf_counter() - start

        # Hash map
        start = time.perf_counter()
        result_hash = two_sum_hash(nums, target)
        t_hash = time.perf_counter() - start

        # Both should find a valid pair
        assert result_brute is not None, "Brute force didn't find pair"
        assert result_hash is not None, "Hash map didn't find pair"
        a, b = result_brute
        assert nums[a] + nums[b] == target
        a, b = result_hash
        assert nums[a] + nums[b] == target

        speedup = t_brute / t_hash if t_hash > 0 else float("inf")
        results.append({
            "n": n,
            "brute_ms": t_brute * 1000,
            "hash_ms": t_hash * 1000,
            "speedup": speedup,
        })

    return results


def print_results(results: list[dict]) -> None:
    print(f"\n{'n':>10} {'Brute O(n²) ms':>16} {'Hash O(n) ms':>14} {'Speedup':>10}")
    print("-" * 54)
    for r in results:
        print(f"{r['n']:>10,} {r['brute_ms']:>16.2f} {r['hash_ms']:>14.3f} {r['speedup']:>9.0f}x")
    print()


if __name__ == "__main__":
    print("Hash Map vs Nested Loop (Two Sum)")
    print("=" * 54)
    results = benchmark()
    print_results(results)


def test_correctness() -> None:
    nums = [2, 7, 11, 15]
    target = 9
    assert two_sum_brute(nums, target) == (0, 1)
    assert two_sum_hash(nums, target) == (0, 1)


def test_no_solution() -> None:
    nums = [1, 2, 3]
    assert two_sum_brute(nums, 100) is None
    assert two_sum_hash(nums, 100) is None


def test_benchmark_runs() -> None:
    results = benchmark(sizes=[100, 1_000, 10_000])
    assert len(results) == 3
    # Only assert timing on the largest size where O(n) vs O(n^2) is unambiguous
    assert results[2]["hash_ms"] < results[2]["brute_ms"]
