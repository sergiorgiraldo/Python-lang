"""
DE Scenario: Top-K Streaming Aggregations

Finding the top N records by some metric from a large dataset
without sorting the entire thing.

Uses a min-heap of size K to track the K largest values.
Memory: O(K) regardless of input size.
"""

import heapq
import random
import time
from dataclasses import dataclass


@dataclass
class QueryLog:
    """Simulated query log entry."""

    query_id: str
    duration_ms: float
    table_name: str


def top_k_queries_heap(logs: list[QueryLog], k: int) -> list[QueryLog]:
    """
    Find the K slowest queries using a min-heap.

    The heap stores (duration, index, log) tuples. The index
    breaks ties deterministically (QueryLog isn't comparable).

    Time: O(n log k)  Space: O(k)
    """
    heap: list[tuple[float, int, QueryLog]] = []
    for i, log in enumerate(logs):
        if len(heap) < k:
            heapq.heappush(heap, (log.duration_ms, i, log))
        elif log.duration_ms > heap[0][0]:
            heapq.heapreplace(heap, (log.duration_ms, i, log))

    # Sort results by duration descending
    return [log for _, _, log in sorted(heap, reverse=True)]


def top_k_queries_sort(logs: list[QueryLog], k: int) -> list[QueryLog]:
    """
    Brute force: sort all logs by duration.

    Time: O(n log n)  Space: O(n)
    """
    return sorted(logs, key=lambda x: x.duration_ms, reverse=True)[:k]


def top_k_queries_nlargest(logs: list[QueryLog], k: int) -> list[QueryLog]:
    """
    Production approach using heapq.nlargest.

    Time: O(n log k)  Space: O(k)
    """
    return heapq.nlargest(k, logs, key=lambda x: x.duration_ms)


def generate_query_logs(n: int) -> list[QueryLog]:
    """Generate simulated query logs with realistic distribution."""
    tables = ["orders", "users", "events", "products", "sessions"]
    logs = []
    for i in range(n):
        # Most queries are fast, a few are slow (log-normal-ish)
        duration = random.expovariate(1 / 50)  # mean 50ms
        if random.random() < 0.01:  # 1% are very slow
            duration *= 10
        logs.append(
            QueryLog(
                query_id=f"q_{i:08d}",
                duration_ms=round(duration, 2),
                table_name=random.choice(tables),
            )
        )
    return logs


if __name__ == "__main__":
    random.seed(42)

    for n in [10_000, 100_000, 1_000_000]:
        logs = generate_query_logs(n)
        k = 10

        start = time.perf_counter()
        result_heap = top_k_queries_heap(logs, k)
        heap_time = time.perf_counter() - start

        start = time.perf_counter()
        result_sort = top_k_queries_sort(logs, k)
        sort_time = time.perf_counter() - start

        start = time.perf_counter()
        result_nlargest = top_k_queries_nlargest(logs, k)
        nlargest_time = time.perf_counter() - start

        print(f"\n--- n={n:,}, k={k} ---")
        print(f"Heap:     {heap_time:.4f}s")
        print(f"Sort:     {sort_time:.4f}s")
        print(f"nlargest: {nlargest_time:.4f}s")
        print(f"Speedup (sort/heap): {sort_time / heap_time:.1f}x")

    print("\nTop 5 slowest (from last run):")
    for log in result_heap[:5]:
        print(f"  {log.query_id}: {log.duration_ms:.2f}ms on {log.table_name}")
