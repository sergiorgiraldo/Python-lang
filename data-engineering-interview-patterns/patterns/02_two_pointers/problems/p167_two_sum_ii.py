"""
LeetCode 167: Two Sum II - Input Array Is Sorted

Pattern: Two Pointers - Opposite Ends
Difficulty: Medium
Time Complexity: O(n)
Space Complexity: O(1)
"""


def two_sum_ii(numbers: list[int], target: int) -> list[int]:
    """
    Find two numbers in a sorted array that sum to target.
    Return 1-indexed positions.

    Since the array is sorted, start pointers at opposite ends.
    If the sum is too small, move the left pointer right (increase sum).
    If too large, move the right pointer left (decrease sum).

    Args:
        numbers: Sorted list of integers.
        target: Target sum.

    Returns:
        1-indexed positions of the two numbers.

    Example:
        >>> two_sum_ii([2, 7, 11, 15], 9)
        [1, 2]
    """
    left, right = 0, len(numbers) - 1

    while left < right:
        current = numbers[left] + numbers[right]
        if current == target:
            return [left + 1, right + 1]  # 1-indexed
        elif current < target:
            left += 1
        else:
            right -= 1

    return []  # guaranteed to have a solution per constraints


if __name__ == "__main__":
    test_cases = [
        ([2, 7, 11, 15], 9, [1, 2]),
        ([2, 3, 4], 6, [1, 3]),
        ([-1, 0], -1, [1, 2]),
    ]

    for numbers, target, expected in test_cases:
        result = two_sum_ii(numbers, target)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status}: two_sum_ii({numbers}, {target}) = {result}")
