"""
Intervals Pattern Templates

Reusable code patterns for interval-based problems. The foundation
is almost always the same: sort by start time, then scan left to right.
"""

import heapq


def has_overlap(intervals: list[list[int]]) -> bool:
    """
    Check if any two intervals overlap.

    Sort by start, then check if any interval starts before the
    previous one ends.

    Time: O(n log n)  Space: O(1) extra (in-place sort)
    """
    intervals.sort(key=lambda x: x[0])
    for i in range(1, len(intervals)):
        if intervals[i][0] < intervals[i - 1][1]:
            return True
    return False


def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    """
    Merge all overlapping intervals.

    Sort by start, then extend or append each interval based on
    overlap with the current merged interval.

    Time: O(n log n)  Space: O(n) for result
    """
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


def count_max_concurrent(intervals: list[list[int]]) -> int:
    """
    Count the maximum number of concurrent (overlapping) intervals.

    Uses a min-heap of end times. When a new interval starts after
    the earliest ending interval, that interval is "freed."

    Time: O(n log n)  Space: O(n)
    """
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


def min_removals_for_non_overlap(intervals: list[list[int]]) -> int:
    """
    Minimum intervals to remove so no two overlap.

    Sort by end time. Greedily keep intervals that don't conflict
    with the last kept interval.

    Time: O(n log n)  Space: O(1)
    """
    if not intervals:
        return 0
    intervals.sort(key=lambda x: x[1])
    kept = 0
    last_end = float("-inf")
    for start, end in intervals:
        if start >= last_end:
            kept += 1
            last_end = end
    return len(intervals) - kept


def interval_intersection(
    first: list[list[int]], second: list[list[int]]
) -> list[list[int]]:
    """
    Find the intersection of two lists of sorted intervals.

    Uses two pointers, advancing the one with the earlier end time.

    Time: O(n + m)  Space: O(min(n, m)) for result
    """
    result: list[list[int]] = []
    i = j = 0
    while i < len(first) and j < len(second):
        start = max(first[i][0], second[j][0])
        end = min(first[i][1], second[j][1])
        if start <= end:
            result.append([start, end])
        if first[i][1] < second[j][1]:
            i += 1
        else:
            j += 1
    return result
