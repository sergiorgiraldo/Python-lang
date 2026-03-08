"""
LeetCode 35: Search Insert Position

Pattern: Binary Search - Left Boundary
Difficulty: Easy
Time Complexity: O(log n)
Space Complexity: O(1)
"""


def search_insert(nums: list[int], target: int) -> int:
    """
    Find target or return where it would be inserted to keep sorted order.

    This is the left-boundary variant: find the first index where
    nums[i] >= target. Equivalent to bisect.bisect_left().

    Args:
        nums: Sorted list of distinct integers.
        target: Value to find or insert.

    Returns:
        Index of target, or insertion index.

    Example:
        >>> search_insert([1, 3, 5, 6], 5)
        2
        >>> search_insert([1, 3, 5, 6], 2)
        1
    """
    left, right = 0, len(nums)  # right = len, not len-1

    while left < right:  # < not <=
        mid = (left + right) // 2
        if nums[mid] < target:
            left = mid + 1
        else:
            right = mid  # mid could be the answer

    return left


if __name__ == "__main__":
    test_cases = [
        ([1, 3, 5, 6], 5, 2),
        ([1, 3, 5, 6], 2, 1),
        ([1, 3, 5, 6], 7, 4),
        ([1, 3, 5, 6], 0, 0),
    ]

    for nums, target, expected in test_cases:
        result = search_insert(nums, target)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status}: search_insert({nums}, {target}) = {result}")
