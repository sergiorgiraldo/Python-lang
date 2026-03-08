"""
LeetCode 57: Insert Interval

Pattern: Intervals - Insert and merge
Difficulty: Medium
Time Complexity: O(n)
Space Complexity: O(n) for result
"""


def insert(intervals: list[list[int]], new_interval: list[int]) -> list[list[int]]:
    """
    Insert a new interval into a sorted list of non-overlapping intervals,
    merging if necessary.

    Three phases:
    1. Add all intervals that end before the new one starts.
    2. Merge all intervals that overlap with the new one.
    3. Add all intervals that start after the new one ends.

    Args:
        intervals: Sorted, non-overlapping intervals.
        new_interval: The interval to insert.

    Returns:
        Updated sorted list of non-overlapping intervals.

    Example:
        >>> insert([[1,3],[6,9]], [2,5])
        [[1,5],[6,9]]
    """
    result: list[list[int]] = []
    i = 0
    n = len(intervals)

    # Phase 1: before the new interval
    while i < n and intervals[i][1] < new_interval[0]:
        result.append(intervals[i])
        i += 1

    # Phase 2: overlapping with the new interval
    while i < n and intervals[i][0] <= new_interval[1]:
        new_interval = [
            min(new_interval[0], intervals[i][0]),
            max(new_interval[1], intervals[i][1]),
        ]
        i += 1
    result.append(new_interval)

    # Phase 3: after the new interval
    while i < n:
        result.append(intervals[i])
        i += 1

    return result


def insert_binary_search(
    intervals: list[list[int]], new_interval: list[int]
) -> list[list[int]]:
    """
    Use binary search to find the insertion point, then merge.

    Time: O(n) (merge step is still linear)  Space: O(n)

    The binary search saves comparisons for finding where the new
    interval belongs but the overall complexity is still O(n) because
    we need to shift/merge elements.
    """
    import bisect

    if not intervals:
        return [new_interval]

    starts = [iv[0] for iv in intervals]
    pos = bisect.bisect_left(starts, new_interval[0])

    # Insert and merge using the standard merge algorithm
    intervals.insert(pos, new_interval)

    merged = [intervals[0][:]]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])

    return merged


if __name__ == "__main__":
    print(insert([[1, 3], [6, 9]], [2, 5]))
    print(insert([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]))
    print(insert([], [5, 7]))
