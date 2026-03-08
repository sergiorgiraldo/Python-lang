"""
Benchmark: Interval merge approaches.

Compares:
1. Sort + scan merge: O(n log n)
2. Brute force repeated merge: O(n^2)
3. Built-in sort behavior (Timsort) on pre-sorted chunks

Also benchmarks overlap detection and concurrent count.
"""

import heapq
import random
import time


def merge_sort_scan(intervals: list[list[int]]) -> list[list[int]]:
    """Sort + linear scan merge."""
    if not intervals:
        return []
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0][:]]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged


def merge_brute(intervals: list[list[int]]) -> list[list[int]]:
    """Repeated pairwise merge until stable."""
    if not intervals:
        return []
    result = [iv[:] for iv in intervals]
    changed = True
    while changed:
        changed = False
        new_result = []
        used = [False] * len(result)
        for i in range(len(result)):
            if used[i]:
                continue
            current = result[i][:]
            for j in range(i + 1, len(result)):
                if used[j]:
                    continue
                if current[0] <= result[j][1] and result[j][0] <= current[1]:
                    current = [
                        min(current[0], result[j][0]),
                        max(current[1], result[j][1]),
                    ]
                    used[j] = True
                    changed = True
            new_result.append(current)
        result = new_result
    return sorted(result, key=lambda x: x[0])


def peak_concurrent_heap(intervals: list[list[int]]) -> int:
    """Min-heap for peak concurrent count."""
    if not intervals:
        return 0
    intervals.sort(key=lambda x: x[0])
    heap: list[int] = []
    for start, end in intervals:
        if heap and heap[0] <= start:
            heapq.heapreplace(heap, end)
        else:
            heapq.heappush(heap, end)
    return len(heap)


def generate_intervals(n: int, max_val: int = 100_000) -> list[list[int]]:
    """Generate random intervals."""
    intervals = []
    for _ in range(n):
        start = random.randint(0, max_val)
        end = start + random.randint(1, max_val // 10)
        intervals.append([start, end])
    return intervals


def run_benchmark() -> None:
    random.seed(42)

    print("Interval Operations Benchmark")
    print("=" * 70)

    configs = [
        (100, True),
        (1_000, True),
        (10_000, True),
        (100_000, False),  # skip brute force
    ]

    print(
        f"\n{'n':>10} {'sort+scan':>12} {'brute':>12} "
        f"{'heap_peak':>12} {'merged':>10} {'peak':>6}"
    )
    print("-" * 74)

    for n, run_brute in configs:
        intervals = generate_intervals(n)

        start = time.perf_counter()
        merged = merge_sort_scan([iv[:] for iv in intervals])
        sort_time = time.perf_counter() - start

        if run_brute and n <= 1_000:
            start = time.perf_counter()
            merge_brute([iv[:] for iv in intervals])
            brute_time = time.perf_counter() - start
            brute_str = f"{brute_time:.4f}s"
        else:
            brute_str = "skipped"

        start = time.perf_counter()
        peak = peak_concurrent_heap([iv[:] for iv in intervals])
        heap_time = time.perf_counter() - start

        print(
            f"{n:>10,} {sort_time:>12.4f}s {brute_str:>12} "
            f"{heap_time:>12.4f}s {len(merged):>10,} {peak:>6}"
        )

    print("\nSort+scan is O(n log n) regardless of overlap density.")
    print("Brute force degrades to O(n^2) and is impractical above ~1000 intervals.")


if __name__ == "__main__":
    run_benchmark()


def test_merge_sort_scan() -> None:
    intervals = [[1, 3], [2, 6], [8, 10], [15, 18]]
    assert merge_sort_scan(intervals) == [[1, 6], [8, 10], [15, 18]]


def test_merge_brute() -> None:
    intervals = [[1, 3], [2, 6], [8, 10], [15, 18]]
    assert merge_brute(intervals) == [[1, 6], [8, 10], [15, 18]]


def test_merge_empty() -> None:
    assert merge_sort_scan([]) == []
    assert merge_brute([]) == []


def test_peak_concurrent() -> None:
    intervals = [[1, 5], [2, 6], [8, 10]]
    assert peak_concurrent_heap(intervals) == 2


def test_approaches_agree() -> None:
    random.seed(99)
    intervals = generate_intervals(100, max_val=500)
    assert merge_sort_scan([iv[:] for iv in intervals]) == merge_brute([iv[:] for iv in intervals])
