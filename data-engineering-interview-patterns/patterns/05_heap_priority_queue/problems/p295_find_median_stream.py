"""
LeetCode 295: Find Median from Data Stream

Pattern: Heap - Two-heap technique
Difficulty: Hard
Time Complexity: O(log n) per add, O(1) per findMedian
Space Complexity: O(n)
"""

import heapq
from bisect import insort


class MedianFinder:
    """
    Find the median from a data stream using two heaps.

    The lower half is stored in a max-heap (negated values).
    The upper half is stored in a min-heap.
    The median is always at one or both of the heap tops.

    Invariant: len(max_heap) == len(min_heap) or len(max_heap) == len(min_heap) + 1

    Example:
        >>> mf = MedianFinder()
        >>> mf.add_num(1); mf.add_num(2)
        >>> mf.find_median()
        1.5
        >>> mf.add_num(3)
        >>> mf.find_median()
        2.0
    """

    def __init__(self) -> None:
        self.low: list[int] = []  # max-heap (negated) - lower half
        self.high: list[int] = []  # min-heap - upper half

    def add_num(self, num: int) -> None:
        """
        Add a number to the data stream.

        Always push to low first (as negated value), then move the
        top of low to high. If high becomes larger, move its top
        back to low.

        Time: O(log n)
        """
        # Push to low (max-heap), then balance
        heapq.heappush(self.low, -num)
        # Move max of low to high
        heapq.heappush(self.high, -heapq.heappop(self.low))
        # Rebalance if high is larger
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))

    def find_median(self) -> float:
        """
        Return the current median.

        If odd count, the median is the top of low (the larger heap).
        If even count, the median is the average of both tops.

        Time: O(1)
        """
        if len(self.low) > len(self.high):
            return float(-self.low[0])
        return (-self.low[0] + self.high[0]) / 2.0


class MedianFinderSort:
    """
    Brute force: maintain a sorted list using bisect.insort.

    Time: O(n) per add (insertion into sorted list shifts elements)
    Space: O(n)
    """

    def __init__(self) -> None:
        self.sorted_list: list[int] = []

    def add_num(self, num: int) -> None:
        insort(self.sorted_list, num)

    def find_median(self) -> float:
        n = len(self.sorted_list)
        if n % 2 == 1:
            return float(self.sorted_list[n // 2])
        return (self.sorted_list[n // 2 - 1] + self.sorted_list[n // 2]) / 2.0


if __name__ == "__main__":
    mf = MedianFinder()
    stream = [5, 2, 8, 1, 9, 3, 7]
    for num in stream:
        mf.add_num(num)
        print(f"add({num}) → median = {mf.find_median()}")
