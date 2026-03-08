"""
LeetCode 1046: Last Stone Weight

Pattern: Heap - Max-heap (negation trick)
Difficulty: Easy
Time Complexity: O(n log n)
Space Complexity: O(n)
"""

import heapq


def last_stone_weight(stones: list[int]) -> int:
    """
    Simulate smashing the two heaviest stones until at most one remains.

    Each round, take the two heaviest stones. If they're equal, both are
    destroyed. If not, the lighter one is destroyed and the heavier one
    loses weight equal to the lighter stone's weight.

    Uses a max-heap (negated values in Python's min-heap) for O(log n)
    access to the heaviest stones.

    Args:
        stones: List of positive integer stone weights.

    Returns:
        Weight of the last remaining stone, or 0 if none remain.

    Example:
        >>> last_stone_weight([2, 7, 4, 1, 8, 1])
        1
    """
    # Negate for max-heap behavior
    heap = [-s for s in stones]
    heapq.heapify(heap)

    while len(heap) > 1:
        first = -heapq.heappop(heap)  # heaviest
        second = -heapq.heappop(heap)  # second heaviest
        if first != second:
            heapq.heappush(heap, -(first - second))

    return -heap[0] if heap else 0


def last_stone_weight_sort(stones: list[int]) -> int:
    """
    Brute force: sort the list on every iteration.

    Time: O(n^2 log n) - sort on each of up to n rounds
    Space: O(1) extra (in-place sort)
    """
    while len(stones) > 1:
        stones.sort()
        first = stones.pop()
        second = stones.pop()
        if first != second:
            stones.append(first - second)
    return stones[0] if stones else 0


if __name__ == "__main__":
    test_cases = [
        [2, 7, 4, 1, 8, 1],
        [1],
        [3, 3],
        [10, 4, 2, 10],
    ]
    for stones in test_cases:
        result = last_stone_weight(list(stones))
        print(f"last_stone_weight({stones}) = {result}")
