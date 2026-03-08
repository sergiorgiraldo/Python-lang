"""
LeetCode 1: Two Sum

Pattern: Hash Map - Complement Lookup
Difficulty: Easy
Time Complexity: O(n)
Space Complexity: O(n)
"""


def two_sum(nums: list[int], target: int) -> list[int]:
    """
    Find two numbers that add up to target and return their indices.

    Args:
        nums: List of integers.
        target: Target sum.

    Returns:
        List with two indices whose values sum to target.
        Empty list if no solution exists.

    Example:
        >>> two_sum([2, 7, 11, 15], 9)
        [0, 1]
    """
    seen: dict[int, int] = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []


def two_sum_brute(nums: list[int], target: int) -> list[int]:
    """
    Brute force: check every pair.

    Time: O(n²)  Space: O(1)

    Useful as a starting point in interviews to show you can
    identify the inefficiency and optimize.
    """
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []


if __name__ == "__main__":
    test_cases = [
        ([2, 7, 11, 15], 9, [0, 1]),
        ([-1, -2, -3, -4], -6, [1, 3]),
        ([3, 3], 6, [0, 1]),
        ([0, 4, 3, 0], 0, [0, 3]),
    ]

    for nums, target, expected in test_cases:
        result = two_sum(nums, target)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status}: two_sum({nums}, {target}) = {result}")
