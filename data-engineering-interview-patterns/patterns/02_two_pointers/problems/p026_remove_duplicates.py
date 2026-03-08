"""
LeetCode 26: Remove Duplicates from Sorted Array

Pattern: Two Pointers - Same Direction (Read/Write)
Difficulty: Easy
Time Complexity: O(n)
Space Complexity: O(1)
"""


def remove_duplicates(nums: list[int]) -> int:
    """
    Remove duplicates from sorted array in place, return new length.

    Uses a write pointer that only advances when a new unique value
    is found. The read pointer scans every element.

    Args:
        nums: Sorted list of integers (modified in place).

    Returns:
        Number of unique elements. The first k elements of nums
        contain the unique values.

    Example:
        >>> nums = [1, 1, 2]
        >>> remove_duplicates(nums)
        2
        >>> nums[:2]
        [1, 2]
    """
    if not nums:
        return 0

    write = 1
    for read in range(1, len(nums)):
        if nums[read] != nums[write - 1]:
            nums[write] = nums[read]
            write += 1

    return write


if __name__ == "__main__":
    test_cases = [
        ([1, 1, 2], 2, [1, 2]),
        ([0, 0, 1, 1, 1, 2, 2, 3, 3, 4], 5, [0, 1, 2, 3, 4]),
        ([], 0, []),
        ([1], 1, [1]),
    ]

    for nums, expected_k, expected_vals in test_cases:
        original = nums.copy()
        k = remove_duplicates(nums)
        status = "PASS" if k == expected_k and nums[:k] == expected_vals else "FAIL"
        print(f"{status}: remove_duplicates({original}) -> k={k}, vals={nums[:k]}")
