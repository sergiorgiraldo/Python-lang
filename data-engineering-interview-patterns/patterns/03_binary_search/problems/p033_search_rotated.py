"""
LeetCode 33: Search in Rotated Sorted Array

Pattern: Binary Search - Modified (Rotated Array)
Difficulty: Medium
Time Complexity: O(log n)
Space Complexity: O(1)
"""


def search(nums: list[int], target: int) -> int:
    """
    Find target in a rotated sorted array. Return index or -1.

    Key insight: at any midpoint, one half is always properly sorted.
    Check if target is in the sorted half's range. If yes, search
    there. Otherwise, search the other half.

    Args:
        nums: Rotated sorted array with unique elements.
        target: Value to find.

    Returns:
        Index of target, or -1.

    Example:
        >>> search([4, 5, 6, 7, 0, 1, 2], 0)
        4
    """
    left, right = 0, len(nums) - 1

    while left <= right:
        mid = (left + right) // 2

        if nums[mid] == target:
            return mid

        # Determine which half is sorted
        if nums[left] <= nums[mid]:
            # Left half [left..mid] is sorted
            if nums[left] <= target < nums[mid]:
                right = mid - 1  # Target is in the sorted left half
            else:
                left = mid + 1  # Target is in the right half
        else:
            # Right half [mid..right] is sorted
            if nums[mid] < target <= nums[right]:
                left = mid + 1  # Target is in the sorted right half
            else:
                right = mid - 1  # Target is in the left half

    return -1


def search_with_pivot(nums: list[int], target: int) -> int:
    """
    Alternative: find the pivot first, then binary search the correct half.

    Two passes of O(log n) = O(log n) total. Easier to understand
    but slightly more code.
    """
    if not nums:
        return -1

    n = len(nums)

    # Find the minimum (rotation pivot)
    lo, hi = 0, n - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        else:
            hi = mid
    pivot = lo

    # Determine which half to search
    if target >= nums[pivot] and target <= nums[n - 1]:
        lo, hi = pivot, n - 1
    else:
        lo, hi = 0, pivot - 1

    # Standard binary search
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1

    return -1


if __name__ == "__main__":
    test_cases = [
        ([4, 5, 6, 7, 0, 1, 2], 0, 4),
        ([4, 5, 6, 7, 0, 1, 2], 3, -1),
        ([1], 0, -1),
        ([1], 1, 0),
        ([1, 3], 3, 1),
    ]

    for nums, target, expected in test_cases:
        result = search(nums, target)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status}: search({nums}, {target}) = {result}")
