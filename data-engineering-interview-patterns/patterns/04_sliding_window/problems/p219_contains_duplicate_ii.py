"""
LeetCode 219: Contains Duplicate II

Pattern: Sliding Window - Fixed Size + Hash Set
Difficulty: Easy
Time Complexity: O(n)
Space Complexity: O(k)
"""


def contains_nearby_duplicate(nums: list[int], k: int) -> bool:
    """
    Check if any value appears twice within a window of size k+1.

    Maintain a hash set of elements in the current window. If a
    new element is already in the set, we found a nearby duplicate.
    When the window exceeds size k+1, remove the oldest element.

    Args:
        nums: List of integers.
        k: Maximum distance between duplicates.

    Returns:
        True if duplicate exists within distance k.

    Example:
        >>> contains_nearby_duplicate([1, 2, 3, 1], 3)
        True
    """
    window: set[int] = set()

    for i, num in enumerate(nums):
        if num in window:
            return True
        window.add(num)
        # Keep window size at most k+1
        if len(window) > k:
            window.remove(nums[i - k])

    return False


def contains_nearby_duplicate_brute(nums: list[int], k: int) -> bool:
    """Brute force: check every pair within distance k. O(n * k)."""
    for i in range(len(nums)):
        for j in range(i + 1, min(i + k + 1, len(nums))):
            if nums[i] == nums[j]:
                return True
    return False


if __name__ == "__main__":
    test_cases = [
        ([1, 2, 3, 1], 3, True),
        ([1, 0, 1, 1], 1, True),
        ([1, 2, 3, 1, 2, 3], 2, False),
        ([], 0, False),
    ]

    for nums, k, expected in test_cases:
        result = contains_nearby_duplicate(nums, k)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status}: contains_nearby_duplicate({nums}, {k}) = {result}")
