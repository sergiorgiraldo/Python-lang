"""
LeetCode 56: Merge Intervals

Pattern: Intervals - Sort and merge
Difficulty: Medium
Time Complexity: O(n log n)
Space Complexity: O(n) for result
"""


def merge(intervals: list[list[int]]) -> list[list[int]]:
    """
    Merge all overlapping intervals.

    Sort by start time, then scan left to right. If the current
    interval overlaps with the last merged interval, extend it.
    Otherwise, start a new merged interval.

    Args:
        intervals: List of [start, end] pairs.

    Returns:
        List of merged intervals with no overlaps.

    Example:
        >>> merge([[1, 3], [2, 6], [8, 10], [15, 18]])
        [[1, 6], [8, 10], [15, 18]]
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


def merge_brute(intervals: list[list[int]]) -> list[list[int]]:
    """
    Brute force: repeatedly merge overlapping pairs until stable.

    Time: O(n^2) in worst case  Space: O(n)
    """
    if not intervals:
        return []

    result = [iv[:] for iv in intervals]
    changed = True

    while changed:
        changed = False
        new_result: list[list[int]] = []
        used = [False] * len(result)

        for i in range(len(result)):
            if used[i]:
                continue
            current = result[i][:]
            for j in range(i + 1, len(result)):
                if used[j]:
                    continue
                if current[0] <= result[j][1] and result[j][0] <= current[1]:
                    current[0] = min(current[0], result[j][0])
                    current[1] = max(current[1], result[j][1])
                    used[j] = True
                    changed = True
            new_result.append(current)
        result = new_result

    return sorted(result, key=lambda x: x[0])


if __name__ == "__main__":
    cases = [
        [[1, 3], [2, 6], [8, 10], [15, 18]],
        [[1, 4], [4, 5]],
        [[1, 4], [0, 4]],
    ]
    for intervals in cases:
        print(f"merge({intervals}) = {merge([iv[:] for iv in intervals])}")
