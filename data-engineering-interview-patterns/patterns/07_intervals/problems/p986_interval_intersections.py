"""
LeetCode 986: Interval List Intersections

Pattern: Intervals - Two-pointer intersection
Difficulty: Medium
Time Complexity: O(n + m)
Space Complexity: O(min(n, m)) for result
"""


def interval_intersection(
    first_list: list[list[int]], second_list: list[list[int]]
) -> list[list[int]]:
    """
    Find the intersection of two sorted interval lists.

    Each list is pairwise disjoint and sorted. The intersection
    of two intervals (if it exists) is [max(starts), min(ends)].

    Uses two pointers, advancing the one with the earlier end time.

    Args:
        first_list: Sorted, non-overlapping intervals.
        second_list: Sorted, non-overlapping intervals.

    Returns:
        List of intersection intervals.

    Example:
        >>> interval_intersection(
        ...     [[0,2],[5,10],[13,23],[24,25]],
        ...     [[1,5],[8,12],[15,24],[25,26]]
        ... )
        [[1,2],[5,5],[8,10],[15,23],[24,24],[25,25]]
    """
    result: list[list[int]] = []
    i = j = 0

    while i < len(first_list) and j < len(second_list):
        start = max(first_list[i][0], second_list[j][0])
        end = min(first_list[i][1], second_list[j][1])

        if start <= end:
            result.append([start, end])

        # Advance the pointer with the earlier end time
        if first_list[i][1] < second_list[j][1]:
            i += 1
        else:
            j += 1

    return result


def interval_intersection_brute(
    first_list: list[list[int]], second_list: list[list[int]]
) -> list[list[int]]:
    """
    Brute force: check every pair.

    Time: O(n * m)  Space: O(n * m) worst case
    """
    result: list[list[int]] = []
    for a in first_list:
        for b in second_list:
            start = max(a[0], b[0])
            end = min(a[1], b[1])
            if start <= end:
                result.append([start, end])
    return sorted(result)


if __name__ == "__main__":
    a = [[0, 2], [5, 10], [13, 23], [24, 25]]
    b = [[1, 5], [8, 12], [15, 24], [25, 26]]
    print(f"Intersection: {interval_intersection(a, b)}")
