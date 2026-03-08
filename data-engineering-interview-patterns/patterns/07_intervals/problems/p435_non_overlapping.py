"""
LeetCode 435: Non-overlapping Intervals

Pattern: Intervals - Greedy scheduling
Difficulty: Medium
Time Complexity: O(n log n)
Space Complexity: O(1) extra
"""


def erase_overlap_intervals(intervals: list[list[int]]) -> int:
    """
    Find the minimum number of intervals to remove so that the
    remaining intervals don't overlap.

    Sort by end time. Greedily keep intervals that don't conflict
    with the last kept interval. The greedy choice (earliest end)
    leaves the most room for future intervals.

    Args:
        intervals: List of [start, end] pairs.

    Returns:
        Minimum number of intervals to remove.

    Example:
        >>> erase_overlap_intervals([[1, 2], [2, 3], [3, 4], [1, 3]])
        1
    """
    if not intervals:
        return 0

    intervals.sort(key=lambda x: x[1])  # sort by END time
    kept = 1
    last_end = intervals[0][1]

    for start, end in intervals[1:]:
        if start >= last_end:  # no conflict
            kept += 1
            last_end = end
        # else: skip this interval (it conflicts)

    return len(intervals) - kept


def erase_overlap_intervals_start(intervals: list[list[int]]) -> int:
    """
    Alternative: sort by start time, greedily remove the one
    with the later end when two overlap.

    Time: O(n log n)  Space: O(1)
    """
    if not intervals:
        return 0

    intervals.sort(key=lambda x: x[0])
    removals = 0
    last_end = intervals[0][1]

    for start, end in intervals[1:]:
        if start < last_end:  # overlap
            removals += 1
            last_end = min(last_end, end)  # keep the shorter one
        else:
            last_end = end

    return removals


if __name__ == "__main__":
    cases = [
        [[1, 2], [2, 3], [3, 4], [1, 3]],
        [[1, 2], [1, 2], [1, 2]],
        [[1, 2], [2, 3]],
    ]
    for intervals in cases:
        print(f"erase({intervals}) = {erase_overlap_intervals(list(intervals))}")
