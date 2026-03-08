"""
LeetCode 704: Binary Search

Pattern: Binary Search - Exact Match
Difficulty: Easy
Time Complexity: O(log n)
Space Complexity: O(1)
"""


def binary_search(nums: list[int], target: int) -> int:
    """
    Find target in a sorted array. Returns index or -1 if not found.

    Classic exact-match binary search. Left and right pointers
    define the search space. Each step halves it.

    Args:
        nums: Sorted list of integers
        target: Value to find

    Returns:
        Index of target, or -1

    Example:
        >>> binary_search([2, 5, 8, 12, 16, 23, 34, 45, 67, 78], 34)
        6
    """
    left, right = 0, len(nums) - 1

    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1


def linear_search(nums: list[int], target: int) -> int:
    """
    Linear scan for comparison. O(n) time.

    This is what binary search replaces. At n=1,000,000 the
    difference is ~20 comparisons vs up to 1,000,000.
    """
    for i, num in enumerate(nums):
        if num == target:
            return i
    return -1


if __name__ == "__main__":
    test_cases = [
        ([-1, 0, 3, 5, 9, 12], 9, 4),
        ([-1, 0, 3, 5, 9, 12], 2, -1),
        ([5], 5, 0),
        ([5], -5, -1),
    ]

    for nums, target, expected in test_cases:
        result = binary_search(nums, target)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status}: binary_search({nums}, {target}) = {result}")
