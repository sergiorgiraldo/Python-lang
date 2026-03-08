"""
DE Scenario: Running Percentiles (Streaming Median)

Computing streaming median and percentiles as data arrives.
Uses two heaps to maintain O(log n) updates and O(1) queries.
"""

import heapq
import random
import time
from statistics import median as true_median


class StreamingMedian:
    """
    Streaming median using two heaps.

    low: max-heap (negated) for lower half
    high: min-heap for upper half
    """

    def __init__(self) -> None:
        self.low: list[int] = []
        self.high: list[int] = []

    def add(self, num: float) -> None:
        heapq.heappush(self.low, -num)
        heapq.heappush(self.high, -heapq.heappop(self.low))
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))

    def median(self) -> float:
        if len(self.low) > len(self.high):
            return float(-self.low[0])
        return (-self.low[0] + self.high[0]) / 2.0


class NaiveMedian:
    """Brute force: keep sorted list, compute median by indexing."""

    def __init__(self) -> None:
        self.values: list[float] = []

    def add(self, num: float) -> None:
        self.values.append(num)
        self.values.sort()

    def median(self) -> float:
        n = len(self.values)
        if n % 2 == 1:
            return float(self.values[n // 2])
        return (self.values[n // 2 - 1] + self.values[n // 2]) / 2.0


def simulate_latency_stream(n: int) -> list[float]:
    """Generate simulated API latency values (ms)."""
    values = []
    for _ in range(n):
        # Baseline 20-80ms with occasional spikes
        base = random.gauss(50, 15)
        if random.random() < 0.05:  # 5% spike
            base *= random.uniform(2, 5)
        values.append(max(1.0, round(base, 2)))
    return values


if __name__ == "__main__":
    random.seed(42)

    for n in [1_000, 10_000, 50_000]:
        values = simulate_latency_stream(n)

        # Two-heap approach
        sm = StreamingMedian()
        start = time.perf_counter()
        for v in values:
            sm.add(v)
        heap_time = time.perf_counter() - start
        heap_median = sm.median()

        # Naive approach (sort on every add)
        nm = NaiveMedian()
        start = time.perf_counter()
        for v in values:
            nm.add(v)
        naive_time = time.perf_counter() - start
        naive_median = nm.median()

        # Verify
        actual = true_median(values)
        assert abs(heap_median - actual) < 0.01, f"{heap_median} != {actual}"

        print(f"\n--- n={n:,} ---")
        print(f"Two-heap:  {heap_time:.4f}s  (median={heap_median:.2f}ms)")
        print(f"Naive:     {naive_time:.4f}s  (median={naive_median:.2f}ms)")
        print(f"Speedup:   {naive_time / heap_time:.1f}x")
        print(f"True median: {actual:.2f}ms")
