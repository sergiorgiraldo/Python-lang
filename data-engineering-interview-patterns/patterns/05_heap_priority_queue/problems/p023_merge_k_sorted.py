"""
LeetCode 23: Merge K Sorted Lists

Pattern: Heap - K-way merge
Difficulty: Hard
Time Complexity: O(n log k) where n = total elements, k = number of lists
Space Complexity: O(k) for the heap
"""

from __future__ import annotations

import heapq
from typing import Generator, Iterable


class ListNode:
    """Singly linked list node (LeetCode's definition)."""

    def __init__(self, val: int = 0, next: ListNode | None = None) -> None:
        self.val = val
        self.next = next

    def __repr__(self) -> str:
        vals = []
        node = self
        while node:
            vals.append(str(node.val))
            node = node.next
        return " -> ".join(vals)


def merge_k_sorted_lists(lists: list[ListNode | None]) -> ListNode | None:
    """
    Merge k sorted linked lists into one sorted linked list.

    Uses a min-heap of size k. Each entry is (value, list_index, node).
    The list_index breaks ties in heap comparison (nodes aren't comparable).

    Args:
        lists: List of sorted linked list heads (may include None).

    Returns:
        Head of the merged sorted linked list.

    Example:
        >>> # [1->4->5, 1->3->4, 2->6]
        >>> # Result: 1->1->2->3->4->4->5->6
    """
    heap: list[tuple[int, int, ListNode]] = []
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))

    dummy = ListNode(0)
    current = dummy

    while heap:
        val, idx, node = heapq.heappop(heap)
        current.next = node
        current = current.next
        if node.next:
            heapq.heappush(heap, (node.next.val, idx, node.next))

    return dummy.next


def merge_k_sorted_arrays(lists: list[list[int]]) -> list[int]:
    """
    Merge k sorted arrays into one sorted array.

    Same algorithm as merge_k_sorted_lists but with arrays.
    This is the version you'd use in data engineering.

    Time: O(n log k)  Space: O(k) for heap + O(n) for result
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
    Lazily merge k sorted iterables.

    Yields one element at a time. Memory usage is O(k) regardless
    of total data size. This is the pattern for merging sorted files,
    database cursors or Kafka partitions.

    Time: O(n log k)  Space: O(k)
    """
    heap: list[tuple[int, int]] = []
    iterators = [iter(it) for it in iterables]

    for i, iterator in enumerate(iterators):
        first = next(iterator, None)
        if first is not None:
            heapq.heappush(heap, (first, i))

    while heap:
        val, src_idx = heapq.heappop(heap)
        yield val
        nxt = next(iterators[src_idx], None)
        if nxt is not None:
            heapq.heappush(heap, (nxt, src_idx))


def merge_k_sorted_brute(lists: list[list[int]]) -> list[int]:
    """
    Brute force: concatenate all and sort.

    Time: O(n log n)  Space: O(n)
    """
    combined = []
    for lst in lists:
        combined.extend(lst)
    return sorted(combined)


def merge_k_sorted_sequential(lists: list[list[int]]) -> list[int]:
    """
    Merge lists one pair at a time (sequential two-way merge).

    Merge list 0 with list 1, then result with list 2, etc.

    Time: O(n * k) - each element might be merged k times
    Space: O(n)
    """
    if not lists:
        return []

    def merge_two(a: list[int], b: list[int]) -> list[int]:
        result = []
        i = j = 0
        while i < len(a) and j < len(b):
            if a[i] <= b[j]:
                result.append(a[i])
                i += 1
            else:
                result.append(b[j])
                j += 1
        result.extend(a[i:])
        result.extend(b[j:])
        return result

    merged = lists[0]
    for i in range(1, len(lists)):
        merged = merge_two(merged, lists[i])
    return merged


# Helper to build linked lists from arrays (for testing)
def build_linked_list(vals: list[int]) -> ListNode | None:
    if not vals:
        return None
    head = ListNode(vals[0])
    current = head
    for val in vals[1:]:
        current.next = ListNode(val)
        current = current.next
    return head


def linked_list_to_array(head: ListNode | None) -> list[int]:
    result = []
    while head:
        result.append(head.val)
        head = head.next
    return result


if __name__ == "__main__":
    lists = [[1, 4, 5], [1, 3, 4], [2, 6]]
    print(f"Heap merge: {merge_k_sorted_arrays(lists)}")
    print(f"Lazy merge: {list(merge_k_sorted_lazy(lists))}")
    print(f"Brute force: {merge_k_sorted_brute(lists)}")
    print(f"Sequential: {merge_k_sorted_sequential(lists)}")
