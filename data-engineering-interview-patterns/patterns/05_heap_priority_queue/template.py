"""
Heap / Priority Queue Pattern Templates

Reusable code patterns for heap-based problems. Python's heapq module
provides a min-heap. For max-heap behavior, negate values before
pushing and after popping.
"""

import heapq
from typing import Generator, Iterable, TypeVar

T = TypeVar("T")


def top_k_largest(items: Iterable[int], k: int) -> list[int]:
    """
    Find the K largest elements from an iterable.

    Uses a min-heap of size K. The heap's minimum is always the Kth
    largest element seen so far. Elements smaller than the heap's
    minimum are discarded without processing.

    Time: O(n log k)  Space: O(k)
    """
    heap: list[int] = []
    for item in items:
        if len(heap) < k:
            heapq.heappush(heap, item)
        elif item > heap[0]:
            heapq.heapreplace(heap, item)
    return sorted(heap, reverse=True)


def top_k_smallest(items: Iterable[int], k: int) -> list[int]:
    """
    Find the K smallest elements from an iterable.

    Uses a max-heap of size K (negated values). The heap's minimum
    (most negative) corresponds to the largest of the K smallest.

    Time: O(n log k)  Space: O(k)
    """
    heap: list[int] = []
    for item in items:
        if len(heap) < k:
            heapq.heappush(heap, -item)
        elif item < -heap[0]:
            heapq.heapreplace(heap, -item)
    return sorted(-x for x in heap)


def merge_k_sorted(lists: list[list[int]]) -> list[int]:
    """
    Merge K sorted lists into a single sorted list.

    Uses a min-heap of size K to always pick the next smallest element
    across all lists. Each element is pushed and popped exactly once.

    Time: O(n log k) where n is total elements across all lists
    Space: O(k) for the heap + O(n) for the result
    """
    heap: list[tuple[int, int, int]] = []
    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst[0], i, 0))

    result: list[int] = []
    while heap:
        val, list_idx, elem_idx = heapq.heappop(heap)
        result.append(val)
        if elem_idx + 1 < len(lists[list_idx]):
            next_val = lists[list_idx][elem_idx + 1]
            heapq.heappush(heap, (next_val, list_idx, elem_idx + 1))
    return result


def merge_k_sorted_lazy(
    iterables: list[Iterable[int]],
) -> Generator[int, None, None]:
    """
    Lazily merge K sorted iterables using a heap.

    Same algorithm as merge_k_sorted but yields one element at a time.
    Memory usage is O(k) regardless of total data size because we
    never build the full result list.

    This is the pattern for merging sorted files or database cursors
    when the combined output doesn't fit in memory.

    Time: O(n log k)  Space: O(k)
    """
    heap: list[tuple[int, int, int]] = []
    iterators = [iter(it) for it in iterables]

    for i, iterator in enumerate(iterators):
        first = next(iterator, None)
        if first is not None:
            heapq.heappush(heap, (first, i, 0))

    while heap:
        val, src_idx, _ = heapq.heappop(heap)
        yield val
        nxt = next(iterators[src_idx], None)
        if nxt is not None:
            heapq.heappush(heap, (nxt, src_idx, 0))


class RunningMedian:
    """
    Track the running median of a stream of numbers.

    Uses two heaps: a max-heap for the lower half and a min-heap for
    the upper half. The median is always accessible in O(1) from the
    tops of the heaps.

    Time: O(log n) per insert, O(1) per median query
    Space: O(n)
    """

    def __init__(self) -> None:
        self.low: list[int] = []  # max-heap (negated)
        self.high: list[int] = []  # min-heap

    def add(self, num: int) -> None:
        """Add a number to the stream."""
        heapq.heappush(self.low, -num)
        heapq.heappush(self.high, -heapq.heappop(self.low))

        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))

    def median(self) -> float:
        """Return the current median."""
        if len(self.low) > len(self.high):
            return -self.low[0]
        return (-self.low[0] + self.high[0]) / 2
