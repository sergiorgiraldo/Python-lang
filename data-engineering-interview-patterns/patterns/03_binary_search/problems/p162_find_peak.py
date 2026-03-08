"""
LeetCode 162: Find Peak Element

Pattern: Binary Search - Local Property (not globally sorted)
Difficulty: Medium
Time Complexity: O(log n)
Space Complexity: O(1)
"""


def find_peak_element(nums: list[int]) -> int:
    """
    Find any index where nums[i] > nums[i-1] and nums[i] > nums[i+1].
    Boundaries are treated as -infinity.

    Binary search works here because we don't need the array to be sorted.
    We only need a local property: if the right neighbor is larger, a peak
    must exist to the right (values are still rising). If the right
    neighbor is smaller, mid is a peak or there's one to the left.

    Args:
        nums: Array where no two adjacent elements are equal.

    Returns:
        Index of any peak element.

    Example:
        >>> find_peak_element([1, 2, 3, 1])
        2
    """
    left, right = 0, len(nums) - 1

    while left < right:
        mid = (left + right) // 2
        if nums[mid] < nums[mid + 1]:
            # Rising slope - peak must be to the right
            left = mid + 1
        else:
            # Falling slope - mid could be a peak, or peak is to the left
            right = mid

    return left


def find_peak_linear(nums: list[int]) -> int:
    """Linear scan: find first element larger than its right neighbor. O(n)."""
    for i in range(len(nums) - 1):
        if nums[i] > nums[i + 1]:
            return i
    return len(nums) - 1  # Last element (everything was ascending)


if __name__ == "__main__":
    test_cases = [
        ([1, 2, 3, 1], 2),
        ([1, 2, 1, 3, 5, 6, 4], [1, 5]),  # Multiple valid peaks
        ([1], 0),
        ([1, 2], 1),
        ([2, 1], 0),
    ]

    for case in test_cases:
        nums = case[0]
        expected = case[1]
        result = find_peak_element(nums)
        if isinstance(expected, list):
            status = "PASS" if result in expected else "FAIL"
        else:
            status = "PASS" if result == expected else "FAIL"
        print(f"{status}: find_peak_element({nums}) = {result}")
