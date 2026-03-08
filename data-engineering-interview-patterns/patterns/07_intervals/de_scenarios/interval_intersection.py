"""
DE Scenario: Interval Intersection (Common Time Windows)

Finding time ranges that appear in both of two schedules.
Uses two-pointer approach from pattern 02.
"""

import random
import time
from datetime import datetime, timedelta


def find_common_availability(
    schedule_a: list[tuple[datetime, datetime]],
    schedule_b: list[tuple[datetime, datetime]],
) -> list[tuple[datetime, datetime]]:
    """
    Find time windows present in both schedules.

    Both schedules are sorted and non-overlapping.
    Uses two pointers, advancing the one with the earlier end.

    Time: O(n + m)  Space: O(min(n, m))
    """
    result: list[tuple[datetime, datetime]] = []
    i = j = 0

    while i < len(schedule_a) and j < len(schedule_b):
        start = max(schedule_a[i][0], schedule_b[j][0])
        end = min(schedule_a[i][1], schedule_b[j][1])

        if start < end:  # strict < for meaningful windows
            result.append((start, end))

        if schedule_a[i][1] < schedule_b[j][1]:
            i += 1
        else:
            j += 1

    return result


def find_common_brute(
    schedule_a: list[tuple[datetime, datetime]],
    schedule_b: list[tuple[datetime, datetime]],
) -> list[tuple[datetime, datetime]]:
    """Brute force: check every pair. O(n * m)."""
    result = []
    for a in schedule_a:
        for b in schedule_b:
            start = max(a[0], b[0])
            end = min(a[1], b[1])
            if start < end:
                result.append((start, end))
    return sorted(result)


def generate_schedule(n_blocks: int, base: datetime) -> list[tuple[datetime, datetime]]:
    """Generate a non-overlapping schedule."""
    blocks = []
    current = base
    for _ in range(n_blocks):
        gap = timedelta(minutes=random.randint(15, 120))
        current += gap
        duration = timedelta(minutes=random.randint(30, 180))
        blocks.append((current, current + duration))
        current += duration
    return blocks


if __name__ == "__main__":
    random.seed(42)
    base = datetime(2024, 6, 1, 8, 0)

    # Simple demo
    sched_a = generate_schedule(10, base)
    sched_b = generate_schedule(10, base)
    common = find_common_availability(sched_a, sched_b)

    print(f"Schedule A: {len(sched_a)} blocks")
    print(f"Schedule B: {len(sched_b)} blocks")
    print(f"Common windows: {len(common)}")
    for start, end in common[:5]:
        duration = (end - start).total_seconds() / 60
        print(
            f"  {start.strftime('%H:%M')} - {end.strftime('%H:%M')} ({duration:.0f}min)"
        )

    # Benchmark
    for n in [100, 1_000, 10_000]:
        a = generate_schedule(n, base)
        b = generate_schedule(n, base)

        start_t = time.perf_counter()
        result = find_common_availability(a, b)
        tp_time = time.perf_counter() - start_t

        print(f"\nn={n:,}: common={len(result)}, time={tp_time:.4f}s")
