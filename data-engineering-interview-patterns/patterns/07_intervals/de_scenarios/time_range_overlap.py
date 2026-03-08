"""
DE Scenario: Time Range Overlap Detection

Detecting overlapping time ranges in event data for deduplication
or conflict detection.
"""

import random
import time
from datetime import datetime, timedelta


def detect_overlaps_sort(
    events: list[tuple[str, datetime, datetime]],
) -> list[tuple[str, str, datetime, datetime]]:
    """
    Find all pairs of overlapping events using sort + scan.

    Sort by start time. Check each event against subsequent events
    that start before it ends.

    Time: O(n log n + n * max_overlap)  Space: O(n)
    """
    sorted_events = sorted(events, key=lambda x: x[1])
    overlaps: list[tuple[str, str, datetime, datetime]] = []

    for i in range(len(sorted_events)):
        id_a, start_a, end_a = sorted_events[i]
        for j in range(i + 1, len(sorted_events)):
            id_b, start_b, end_b = sorted_events[j]
            if start_b >= end_a:
                break  # no more overlaps possible
            overlap_start = max(start_a, start_b)
            overlap_end = min(end_a, end_b)
            overlaps.append((id_a, id_b, overlap_start, overlap_end))

    return overlaps


def detect_overlaps_brute(
    events: list[tuple[str, datetime, datetime]],
) -> list[tuple[str, str, datetime, datetime]]:
    """
    Brute force: check every pair.

    Time: O(n^2)  Space: O(n^2) worst case
    """
    overlaps = []
    for i in range(len(events)):
        for j in range(i + 1, len(events)):
            id_a, start_a, end_a = events[i]
            id_b, start_b, end_b = events[j]
            if start_a < end_b and start_b < end_a:
                overlap_start = max(start_a, start_b)
                overlap_end = min(end_a, end_b)
                overlaps.append((id_a, id_b, overlap_start, overlap_end))
    return sorted(overlaps)


def generate_events(
    n: int, base_time: datetime
) -> list[tuple[str, datetime, datetime]]:
    """Generate random events with some intentional overlaps."""
    events = []
    for i in range(n):
        start = base_time + timedelta(minutes=random.randint(0, 1440))
        duration = timedelta(minutes=random.randint(5, 120))
        events.append((f"event_{i:06d}", start, start + duration))
    return events


if __name__ == "__main__":
    random.seed(42)
    base = datetime(2024, 1, 15, 0, 0)

    for n in [100, 1_000, 5_000]:
        events = generate_events(n, base)

        start = time.perf_counter()
        overlaps_sort = detect_overlaps_sort(events)
        sort_time = time.perf_counter() - start

        if n <= 1_000:
            start = time.perf_counter()
            detect_overlaps_brute(events)
            brute_time = time.perf_counter() - start
            brute_str = f"{brute_time:.4f}s"
        else:
            brute_str = "skipped"

        print(
            f"n={n:,}: sort={sort_time:.4f}s, brute={brute_str}, "
            f"overlaps found={len(overlaps_sort)}"
        )
