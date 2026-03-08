"""
LeetCode 875: Koko Eating Bananas

Pattern: Binary Search on Answer
Difficulty: Medium
Time Complexity: O(n * log(max(piles)))
Space Complexity: O(1)
"""

import math


def min_eating_speed(piles: list[int], h: int) -> int:
    """
    Find the minimum eating speed k so Koko finishes all piles in h hours.

    Each hour, Koko eats up to k bananas from one pile. If the pile has
    fewer than k, she eats the whole pile and waits. Find the smallest k
    that lets her finish in h hours.

    Binary search on the answer space [1, max(piles)]. For each
    candidate speed, calculate total hours needed. If it's <= h,
    try a smaller speed. Otherwise, need a larger speed.

    Args:
        piles: List of banana pile sizes.
        h: Hours available.

    Returns:
        Minimum integer eating speed.

    Example:
        >>> min_eating_speed([3, 6, 7, 11], 8)
        4
    """
    left, right = 1, max(piles)

    while left < right:
        mid = (left + right) // 2
        hours_needed = sum(math.ceil(pile / mid) for pile in piles)

        if hours_needed <= h:
            right = mid  # This speed works, try slower
        else:
            left = mid + 1  # Too slow, need faster

    return left


def min_eating_speed_brute(piles: list[int], h: int) -> int:
    """Try every speed from 1 upward. O(max(piles) * n)."""
    for k in range(1, max(piles) + 1):
        hours = sum(math.ceil(pile / k) for pile in piles)
        if hours <= h:
            return k
    return max(piles)  # Unreachable if h >= len(piles)


if __name__ == "__main__":
    test_cases = [
        ([3, 6, 7, 11], 8, 4),
        ([30, 11, 23, 4, 20], 5, 30),
        ([30, 11, 23, 4, 20], 6, 23),
        ([1], 1, 1),
    ]

    for piles, h, expected in test_cases:
        result = min_eating_speed(piles, h)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status}: min_eating_speed({piles}, {h}) = {result}")
