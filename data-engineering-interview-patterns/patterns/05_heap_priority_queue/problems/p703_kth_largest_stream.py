"""
LeetCode 703: Kth Largest Element in a Stream

Pattern: Heap - Min-heap of size K
Difficulty: Easy
Time Complexity: O(n log k) init, O(log k) per add
Space Complexity: O(k)
"""

import heapq


class KthLargest:
    """
    Track the kth largest element in a stream of numbers.

    Maintains a min-heap of size k. The heap's minimum is always the
    kth largest element. New values smaller than the minimum are
    discarded - they can't be in the top k.

    Example:
        >>> kth = KthLargest(3, [4, 5, 8, 2])
        >>> kth.add(3)
        4
        >>> kth.add(5)
        5
        >>> kth.add(10)
        5
    """

    def __init__(self, k: int, nums: list[int]) -> None:
        self.k = k
        self.heap: list[int] = []
        for num in nums:
            self._push(num)

    def _push(self, val: int) -> None:
        """Push a value, maintaining heap size at most k."""
        if len(self.heap) < self.k:
            heapq.heappush(self.heap, val)
        elif val > self.heap[0]:
            heapq.heapreplace(self.heap, val)

    def add(self, val: int) -> int:
        """
        Add a value to the stream and return the kth largest.

        Time: O(log k) - single heap operation
        """
        self._push(val)
        return self.heap[0]


class KthLargestSort:
    """
    Brute force: sort the entire list on each add.

    Time: O(n log n) per add
    Space: O(n)

    Shows why the heap approach matters at scale.
    """

    def __init__(self, k: int, nums: list[int]) -> None:
        self.k = k
        self.nums = sorted(nums, reverse=True)

    def add(self, val: int) -> int:
        self.nums.append(val)
        self.nums.sort(reverse=True)
        return self.nums[self.k - 1]


if __name__ == "__main__":
    kth = KthLargest(3, [4, 5, 8, 2])
    adds = [3, 5, 10, 9, 4]
    for val in adds:
        result = kth.add(val)
        print(f"add({val}) → kth largest = {result}")
