"""
LeetCode 347: Top K Frequent Elements

Pattern: Hash Map - Frequency Counting + Selection
Difficulty: Medium
Time Complexity: O(n) with bucket sort approach
Space Complexity: O(n)
"""

import heapq
from collections import Counter


def top_k_frequent(nums: list[int], k: int) -> list[int]:
    """
    Return the k most frequent elements.

    Uses Counter for frequency counting and most_common() for
    selection. The most_common method uses a heap internally.

    Args:
        nums: List of integers.
        k: Number of top elements to return.

    Returns:
        List of k most frequent elements (order doesn't matter).

    Example:
        >>> sorted(top_k_frequent([1,1,1,2,2,3], 2))
        [1, 2]
    """
    counts = Counter(nums)
    return [num for num, _ in counts.most_common(k)]


def top_k_frequent_heap(nums: list[int], k: int) -> list[int]:
    """
    Explicit heap approach: count frequencies, then use a min-heap of size k.

    For each frequency, push to heap. If heap exceeds size k, pop the
    smallest. After processing all elements, the heap contains the top k.

    Time: O(n log k) - n elements, each heap operation is O(log k)
    Space: O(n) for the frequency map + O(k) for the heap

    Better than full sort O(n log n) when k << n.
    """
    counts = Counter(nums)
    return heapq.nlargest(k, counts, key=counts.get)


def top_k_frequent_bucket(nums: list[int], k: int) -> list[int]:
    """
    Bucket sort approach: O(n) time.

    Create buckets where index = frequency. Bucket[i] holds all
    elements that appear exactly i times. Walk buckets from high
    to low, collecting elements until we have k.

    Time: O(n)  Space: O(n)

    This is the optimal approach and worth knowing for interviews.
    The insight: frequency is bounded by n, so we can use array
    indices instead of comparison-based sorting.
    """
    counts = Counter(nums)
    # Bucket index = frequency, value = list of elements with that frequency
    buckets: list[list[int]] = [[] for _ in range(len(nums) + 1)]
    for num, freq in counts.items():
        buckets[freq].append(num)

    result: list[int] = []
    for freq in range(len(buckets) - 1, 0, -1):
        for num in buckets[freq]:
            result.append(num)
            if len(result) == k:
                return result
    return result


if __name__ == "__main__":
    test_cases = [
        ([1, 1, 1, 2, 2, 3], 2, {1, 2}),
        ([1], 1, {1}),
        ([4, 1, -1, 2, -1, 2, 3], 2, {-1, 2}),
    ]

    for nums, k, expected_set in test_cases:
        result = top_k_frequent(nums, k)
        status = "PASS" if set(result) == expected_set else "FAIL"
        print(f"{status}: top_k_frequent({nums}, {k}) = {result}")
