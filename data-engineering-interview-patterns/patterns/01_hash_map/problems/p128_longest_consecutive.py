"""
LeetCode 128: Longest Consecutive Sequence

Pattern: Hash Map - Set for O(1) Neighbor Checks
Difficulty: Medium
Time Complexity: O(n)
Space Complexity: O(n)
"""


def longest_consecutive(nums: list[int]) -> int:
    """
    Find the length of the longest consecutive element sequence.

    The key insight: only start counting from sequence beginnings.
    A number is a sequence start if (num - 1) is not in the set.
    This avoids redundant work and keeps time at O(n) despite
    the nested while loop.

    Args:
        nums: Unsorted list of integers.

    Returns:
        Length of the longest consecutive sequence.

    Example:
        >>> longest_consecutive([100, 4, 200, 1, 3, 2])
        4
    """
    if not nums:
        return 0

    num_set = set(nums)
    longest = 0

    for num in num_set:
        # Only start counting from sequence beginnings
        if num - 1 not in num_set:
            current = num
            streak = 1

            while current + 1 in num_set:
                current += 1
                streak += 1

            longest = max(longest, streak)

    return longest


def longest_consecutive_sort(nums: list[int]) -> int:
    """
    Sort-based approach for comparison.

    Sort the array, then scan for consecutive runs. Handle
    duplicates by skipping them.

    Time: O(n log n)  Space: O(1) if in-place sort, O(n) otherwise

    Easier to reason about but doesn't meet the O(n) requirement
    if the problem asks for it.
    """
    if not nums:
        return 0

    nums_sorted = sorted(set(nums))  # deduplicate and sort
    longest = 1
    streak = 1

    for i in range(1, len(nums_sorted)):
        if nums_sorted[i] == nums_sorted[i - 1] + 1:
            streak += 1
            longest = max(longest, streak)
        else:
            streak = 1

    return longest


if __name__ == "__main__":
    test_cases = [
        ([100, 4, 200, 1, 3, 2], 4),
        ([0, 3, 7, 2, 5, 8, 4, 6, 0, 1], 9),
        ([], 0),
        ([1], 1),
    ]

    for nums, expected in test_cases:
        result = longest_consecutive(nums)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status}: longest_consecutive({nums}) = {result}")
