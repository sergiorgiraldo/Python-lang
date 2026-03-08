"""
DE Scenario: Resource Scheduling (Concurrent Job Slots)

Determining how many parallel execution slots are needed
for a set of scheduled jobs.
"""

import heapq
import random
import time
from datetime import datetime, timedelta


def compute_peak_concurrency(
    jobs: list[tuple[str, datetime, datetime]],
) -> dict[str, int | list[tuple[str, str]]]:
    """
    Find peak concurrency and which jobs are running at peak.

    Uses sweep line (event-based) approach.
    """
    events: list[tuple[datetime, int, str]] = []
    for name, start, end in jobs:
        events.append((start, 1, name))
        events.append((end, -1, name))

    events.sort(key=lambda x: (x[0], x[1]))

    current = 0
    peak = 0
    active: list[str] = []
    peak_jobs: list[str] = []

    for ts, delta, name in events:
        if delta == 1:
            active.append(name)
        else:
            active.remove(name)
        current += delta
        if current > peak:
            peak = current
            peak_jobs = list(active)

    return {"peak_concurrency": peak, "peak_jobs": peak_jobs}


def compute_peak_heap(
    jobs: list[tuple[str, datetime, datetime]],
) -> int:
    """
    Min-heap approach (same as Meeting Rooms II).

    Time: O(n log n)  Space: O(n)
    """
    sorted_jobs = sorted(jobs, key=lambda x: x[1])
    heap: list[datetime] = []

    for _, start, end in sorted_jobs:
        if heap and heap[0] <= start:
            heapq.heapreplace(heap, end)
        else:
            heapq.heappush(heap, end)

    return len(heap)


def generate_jobs(n: int, base: datetime) -> list[tuple[str, datetime, datetime]]:
    """Generate random job schedules."""
    jobs = []
    for i in range(n):
        start = base + timedelta(minutes=random.randint(0, 480))
        duration = timedelta(minutes=random.randint(10, 60))
        jobs.append((f"job_{i:04d}", start, start + duration))
    return jobs


if __name__ == "__main__":
    random.seed(42)
    base = datetime(2024, 6, 1, 8, 0)

    jobs = generate_jobs(50, base)
    result = compute_peak_concurrency(jobs)
    print(f"Peak concurrency: {result['peak_concurrency']}")
    print(f"Jobs at peak: {', '.join(result['peak_jobs'][:5])}...")

    for n in [100, 1_000, 10_000]:
        jobs = generate_jobs(n, base)
        start = time.perf_counter()
        peak = compute_peak_heap(jobs)
        elapsed = time.perf_counter() - start
        print(f"\nn={n:,}: peak={peak}, time={elapsed:.4f}s")
