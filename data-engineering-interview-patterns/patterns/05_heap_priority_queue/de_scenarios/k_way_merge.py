"""
DE Scenario: K-Way Merge of Sorted Partitions

Merging K sorted files/partitions into a single sorted output.
Uses a min-heap of size K to always pick the next smallest element.

This is the core algorithm behind external sort, sorted partition
merging and LSM tree compaction.
"""

import heapq
import random
import time
from typing import Generator, Iterable


def generate_sorted_partition(size: int, start: int, gap: int) -> list[int]:
    """Generate a sorted partition with some randomness."""
    values = []
    current = start
    for _ in range(size):
        current += random.randint(1, gap)
        values.append(current)
    return values


def merge_k_heap(partitions: list[list[int]]) -> list[int]:
    """
    K-way merge using a min-heap.

    Time: O(n log k)  Space: O(k) + O(n) for result
    """
    heap: list[tuple[int, int, int]] = []
    for i, partition in enumerate(partitions):
        if partition:
            heapq.heappush(heap, (partition[0], i, 0))

    result: list[int] = []
    while heap:
        val, part_idx, elem_idx = heapq.heappop(heap)
        result.append(val)
        if elem_idx + 1 < len(partitions[part_idx]):
            next_val = partitions[part_idx][elem_idx + 1]
            heapq.heappush(heap, (next_val, part_idx, elem_idx + 1))
    return result


def merge_k_heap_lazy(
    partitions: list[Iterable[int]],
) -> Generator[int, None, None]:
    """
    Lazy K-way merge yielding one element at a time.

    Space: O(k) regardless of total data.
    """
    heap: list[tuple[int, int]] = []
    iterators = [iter(p) for p in partitions]
    for i, it in enumerate(iterators):
        first = next(it, None)
        if first is not None:
            heapq.heappush(heap, (first, i))

    while heap:
        val, src = heapq.heappop(heap)
        yield val
        nxt = next(iterators[src], None)
        if nxt is not None:
            heapq.heappush(heap, (nxt, src))


def merge_k_concat_sort(partitions: list[list[int]]) -> list[int]:
    """
    Brute force: concatenate and sort.

    Time: O(n log n)  Space: O(n)
    """
    combined = []
    for p in partitions:
        combined.extend(p)
    return sorted(combined)


def merge_k_sequential(partitions: list[list[int]]) -> list[int]:
    """
    Sequential merge: merge pairs one at a time.

    Time: O(n * k)  Space: O(n)
    """
    if not partitions:
        return []
    result = list(partitions[0])
    for i in range(1, len(partitions)):
        merged = []
        a, b = result, partitions[i]
        ai = bi = 0
        while ai < len(a) and bi < len(b):
            if a[ai] <= b[bi]:
                merged.append(a[ai])
                ai += 1
            else:
                merged.append(b[bi])
                bi += 1
        merged.extend(a[ai:])
        merged.extend(b[bi:])
        result = merged
    return result


if __name__ == "__main__":
    random.seed(42)

    for k, partition_size in [(10, 10_000), (100, 1_000), (1_000, 100)]:
        n_total = k * partition_size
        partitions = [
            generate_sorted_partition(partition_size, random.randint(0, 100), 5)
            for _ in range(k)
        ]

        start = time.perf_counter()
        result_heap = merge_k_heap(partitions)
        heap_time = time.perf_counter() - start

        start = time.perf_counter()
        result_sort = merge_k_concat_sort(partitions)
        sort_time = time.perf_counter() - start

        start = time.perf_counter()
        result_seq = merge_k_sequential(partitions)
        seq_time = time.perf_counter() - start

        # Verify correctness
        assert result_heap == result_sort == result_seq

        print(f"\n--- k={k}, partition_size={partition_size:,} (total={n_total:,}) ---")
        print(f"Heap merge:       {heap_time:.4f}s")
        print(f"Concat+sort:      {sort_time:.4f}s")
        print(f"Sequential merge: {seq_time:.4f}s")

    # Demonstrate lazy merge memory advantage
    print("\n--- Lazy merge demo (k=100, 1000 elements each) ---")
    partitions = [
        generate_sorted_partition(1000, random.randint(0, 100), 5) for _ in range(100)
    ]
    start = time.perf_counter()
    count = sum(1 for _ in merge_k_heap_lazy(partitions))
    lazy_time = time.perf_counter() - start
    print(f"Lazy merge: {lazy_time:.4f}s, {count:,} elements yielded")
    print("Memory: O(100) for heap vs O(100,000) for full result")
