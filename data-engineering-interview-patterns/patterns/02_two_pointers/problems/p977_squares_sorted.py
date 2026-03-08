"""
LeetCode 977: Squares of a Sorted Array

Pattern: Two Pointers - Opposite Ends (Transform and Merge)
Difficulty: Easy
Time Complexity: O(n)
Space Complexity: O(n)
"""


def sorted_squares(nums: list[int]) -> list[int]:
    """
    Return the squares of each number, sorted in non-decreasing order.

    The input is sorted, which means the largest squares are at the
    extremes (large negatives or large positives). Use opposite-end
    pointers, compare absolute values, and fill the result from the back.

    Args:
        nums: Sorted list of integers (may include negatives).

    Returns:
        Sorted list of squares.

    Example:
        >>> sorted_squares([-4, -1, 0, 3, 10])
        [0, 1, 9, 16, 100]
    """
    n = len(nums)
    result = [0] * n
    left, right = 0, n - 1
    write = n - 1  # fill from the back (largest first)

    while left <= right:
        left_sq = nums[left] ** 2
        right_sq = nums[right] ** 2

        if left_sq >= right_sq:
            result[write] = left_sq
            left += 1
        else:
            result[write] = right_sq
            right -= 1
        write -= 1

    return result


def sorted_squares_simple(nums: list[int]) -> list[int]:
    """
    Simple approach: square everything, then sort.

    Time: O(n log n) due to sorting
    Space: O(n)
    """
    return sorted(x * x for x in nums)


if __name__ == "__main__":
    test_cases = [
        ([-4, -1, 0, 3, 10], [0, 1, 9, 16, 100]),
        ([-7, -3, 2, 3, 11], [4, 9, 9, 49, 121]),
        ([0, 1, 2], [0, 1, 4]),
    ]

    for nums, expected in test_cases:
        result = sorted_squares(nums)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status}: sorted_squares({nums}) = {result}")
