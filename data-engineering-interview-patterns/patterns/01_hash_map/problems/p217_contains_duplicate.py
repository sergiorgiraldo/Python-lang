"""
LeetCode 217: Contains Duplicate

Pattern: Hash Map - Existence Check (Set)
Difficulty: Easy
Time Complexity: O(n)
Space Complexity: O(n)
"""


def contains_duplicate(nums: list[int]) -> bool:
    """
    Return True if any value appears more than once.

    Args:
        nums: List of integers.

    Returns:
        True if duplicates exist, False otherwise.

    Example:
        >>> contains_duplicate([1, 2, 3, 1])
        True
    """
    return len(nums) != len(set(nums))


def contains_duplicate_set(nums: list[int]) -> bool:
    """
    Early-exit variant: stop as soon as a duplicate is found.

    Better than the one-liner when duplicates are common and appear
    early in the array, since we don't process the entire input.

    Time: O(n) worst case  Space: O(n)
    """
    seen: set[int] = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False


def contains_duplicate_sort(nums: list[int]) -> bool:
    """
    Sort-based approach: duplicates become adjacent after sorting.

    Time: O(n log n)  Space: O(1) if sort is in-place, O(n) otherwise

    Useful when you can't afford O(n) extra space but can afford
    O(n log n) time and can modify the input.
    """
    nums_sorted = sorted(nums)
    for i in range(1, len(nums_sorted)):
        if nums_sorted[i] == nums_sorted[i - 1]:
            return True
    return False


if __name__ == "__main__":
    test_cases = [
        ([1, 2, 3, 1], True),
        ([1, 2, 3, 4], False),
        ([1, 1, 1, 3, 3, 4, 3, 2, 4, 2], True),
        ([], False),
        ([1], False),
    ]

    for nums, expected in test_cases:
        result = contains_duplicate(nums)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status}: contains_duplicate({nums}) = {result}")
