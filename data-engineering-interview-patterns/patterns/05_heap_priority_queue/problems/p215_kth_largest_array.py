"""
LeetCode 215: Kth Largest Element in an Array

Pattern: Heap - Selection problem
Difficulty: Medium
Time Complexity: O(n log k) heap, O(n) average quickselect
Space Complexity: O(k) heap, O(1) quickselect
"""

import heapq
import random


def find_kth_largest(nums: list[int], k: int) -> int:
    """
    Find the kth largest element using a min-heap of size k.

    Maintains a heap of the k largest elements seen so far.
    The top of the heap (minimum) is the kth largest.

    Args:
        nums: List of integers (may contain duplicates).
        k: Position from largest (1-indexed). k=1 means the largest.

    Returns:
        The kth largest element.

    Example:
        >>> find_kth_largest([3, 2, 1, 5, 6, 4], 2)
        5
    """
    heap: list[int] = []
    for num in nums:
        if len(heap) < k:
            heapq.heappush(heap, num)
        elif num > heap[0]:
            heapq.heapreplace(heap, num)
    return heap[0]


def find_kth_largest_sort(nums: list[int], k: int) -> int:
    """
    Brute force: sort the entire array.

    Time: O(n log n)  Space: O(n) for sorted copy
    """
    return sorted(nums, reverse=True)[k - 1]


def find_kth_largest_nlargest(nums: list[int], k: int) -> int:
    """
    Pythonic production approach using heapq.nlargest.

    Internally uses a heap. Cleaner than manual heap management.

    Time: O(n log k)  Space: O(k)
    """
    return heapq.nlargest(k, nums)[-1]


def find_kth_largest_quickselect(nums: list[int], k: int) -> int:
    """
    Quickselect algorithm (Hoare's selection algorithm).

    Partition the array around a pivot. If the pivot lands at the
    target index, we're done. Otherwise, recurse into the half
    that contains the target index.

    Time: O(n) average, O(n^2) worst case
    Space: O(1) extra (in-place partitioning)

    The random pivot makes worst case extremely unlikely.
    """
    target_idx = len(nums) - k  # kth largest = (n-k)th smallest

    def quickselect(left: int, right: int) -> int:
        if left == right:
            return nums[left]

        # Random pivot to avoid worst case
        pivot_idx = random.randint(left, right)
        nums[pivot_idx], nums[right] = nums[right], nums[pivot_idx]
        pivot = nums[right]

        # Partition: elements < pivot go left, >= pivot go right
        store = left
        for i in range(left, right):
            if nums[i] < pivot:
                nums[store], nums[i] = nums[i], nums[store]
                store += 1
        nums[store], nums[right] = nums[right], nums[store]

        if store == target_idx:
            return nums[store]
        elif store < target_idx:
            return quickselect(store + 1, right)
        else:
            return quickselect(left, store - 1)

    return quickselect(0, len(nums) - 1)


if __name__ == "__main__":
    test_cases = [
        ([3, 2, 1, 5, 6, 4], 2),
        ([3, 2, 3, 1, 2, 4, 5, 5, 6], 4),
        ([1], 1),
    ]
    for nums, k in test_cases:
        result = find_kth_largest(list(nums), k)
        print(f"find_kth_largest({nums}, {k}) = {result}")
