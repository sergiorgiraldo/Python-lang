"""
LeetCode 153: Find Minimum in Rotated Sorted Array

Pattern: Binary Search - Modified (Rotated Array)
Difficulty: Medium
Time Complexity: O(log n)
Space Complexity: O(1)
"""


def find_min(nums: list[int]) -> int:
    """
    Find the minimum element in a rotated sorted array.

    A sorted array [1,2,3,4,5] rotated at index 3 becomes [4,5,1,2,3].
    The minimum is the rotation pivot point.

    Key insight: compare nums[mid] to nums[right]. If mid > right,
    the minimum is in the right half. Otherwise, it's at mid or to the left.

    Args:
        nums: Rotated sorted array with unique elements.

    Returns:
        The minimum value.

    Example:
        >>> find_min([3, 4, 5, 1, 2])
        1
    """
    left, right = 0, len(nums) - 1

    while left < right:
        mid = (left + right) // 2
        if nums[mid] > nums[right]:
            # Mid is in the left (higher) portion.
            # Minimum must be to the right of mid.
            left = mid + 1
        else:
            # Mid is in the right (lower) portion, or array is fully sorted.
            # Mid could be the minimum - don't skip it.
            right = mid

    return nums[left]


def find_min_linear(nums: list[int]) -> int:
    """Brute force: scan the whole array. O(n)."""
    return min(nums)


if __name__ == "__main__":
    test_cases = [
        ([3, 4, 5, 1, 2], 1),
        ([4, 5, 6, 7, 0, 1, 2], 0),
        ([11, 13, 15, 17], 11),
        ([2, 1], 1),
        ([1], 1),
    ]

    for nums, expected in test_cases:
        result = find_min(nums)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status}: find_min({nums}) = {result}")
