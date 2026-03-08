"""
Benchmark: Heap Top-K vs Full Sort

Shows O(n log k) vs O(n log n) for finding the K largest elements.
The difference is significant when k << n.

Connection: patterns/05_heap/
"""

import heapq
import random
import time


def top_k_sort(nums: list[int], k: int) -> list[int]:
    """O(n log n): sort everything, take last k."""
    return sorted(nums)[-k:]


def top_k_heap(nums: list[int], k: int) -> list[int]:
    """O(n log k): maintain a min-heap of size k."""
    return heapq.nlargest(k, nums)


def benchmark(sizes: list[int] | None = None, k: int = 10) -> list[dict]:
    if sizes is None:
        sizes = [10_000, 100_000, 1_000_000, 10_000_000]

    results = []
    for n in sizes:
        nums = random.sample(range(n * 10), n)

        start = time.perf_counter()
        result_sort = sorted(top_k_sort(nums, k))
        t_sort = time.perf_counter() - start

        start = time.perf_counter()
        result_heap = sorted(top_k_heap(nums, k))
        t_heap = time.perf_counter() - start

        assert result_sort == result_heap, "Results don't match"

        speedup = t_sort / t_heap if t_heap > 0 else float("inf")
        results.append({
            "n": n,
            "k": k,
            "sort_ms": t_sort * 1000,
            "heap_ms": t_heap * 1000,
            "speedup": speedup,
        })

    return results


def print_results(results: list[dict]) -> None:
    k = results[0]["k"]
    print(f"\n  k={k}")
    print(f"{'n':>12} {'Sort O(nlogn) ms':>18} {'Heap O(nlogk) ms':>18} {'Speedup':>10}")
    print("-" * 62)
    for r in results:
        print(f"{r['n']:>12,} {r['sort_ms']:>18.2f} {r['heap_ms']:>18.2f} {r['speedup']:>9.1f}x")
    print()


if __name__ == "__main__":
    print("Heap Top-K vs Full Sort")
    print("=" * 62)

    # k=10 (heap should win clearly)
    results = benchmark(k=10)
    print_results(results)

    # k=1000 (heap advantage smaller)
    results = benchmark(sizes=[100_000, 1_000_000, 10_000_000], k=1000)
    print_results(results)


def test_correctness() -> None:
    nums = [3, 1, 4, 1, 5, 9, 2, 6, 5]
    assert sorted(top_k_sort(nums, 3)) == sorted(top_k_heap(nums, 3))


def test_k_equals_n() -> None:
    nums = [5, 3, 1, 4, 2]
    assert sorted(top_k_sort(nums, 5)) == sorted(top_k_heap(nums, 5))


def test_benchmark_runs() -> None:
    results = benchmark(sizes=[1_000, 10_000], k=5)
    assert len(results) == 2
