"""
LeetCode 252: Meeting Rooms (Premium)

Pattern: Intervals - Overlap detection
Difficulty: Easy
Time Complexity: O(n log n)
Space Complexity: O(1) extra
"""


def can_attend(intervals: list[list[int]]) -> bool:
    """
    Determine if a person can attend all meetings (no overlaps).

    Sort by start time. If any meeting starts before the previous
    one ends, there's a conflict.

    Args:
        intervals: List of [start, end] meeting times.

    Returns:
        True if no meetings overlap, False otherwise.

    Example:
        >>> can_attend([[0, 30], [5, 10], [15, 20]])
        False
        >>> can_attend([[7, 10], [2, 4]])
        True
    """
    intervals.sort(key=lambda x: x[0])
    for i in range(1, len(intervals)):
        if intervals[i][0] < intervals[i - 1][1]:
            return False
    return True


def can_attend_brute(intervals: list[list[int]]) -> bool:
    """
    Brute force: check every pair for overlap.

    Time: O(n^2)  Space: O(1)
    """
    for i in range(len(intervals)):
        for j in range(i + 1, len(intervals)):
            a_start, a_end = intervals[i]
            b_start, b_end = intervals[j]
            if a_start < b_end and b_start < a_end:
                return False
    return True


if __name__ == "__main__":
    print(f"Overlap: {can_attend([[0, 30], [5, 10], [15, 20]])}")
    print(f"No overlap: {can_attend([[7, 10], [2, 4]])}")
