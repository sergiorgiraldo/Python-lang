"""
DE Scenario: Merging Sorted Files

Demonstrates two-pointer merge on sorted sequences. Includes
both in-memory and generator-based (streaming) approaches.

Pattern: Two Pointers - Merge Two Sorted Sequences
"""

import time
from collections.abc import Iterator


def merge_sorted_lists(
    a: list[dict],
    b: list[dict],
    key: str = "ts",
) -> list[dict]:
    """
    Merge two sorted lists of dicts by a key field.

    Classic two-pointer merge. O(n + m) time, O(n + m) space.

    Args:
        a: First sorted list.
        b: Second sorted list.
        key: Field to sort/merge on.

    Returns:
        Merged sorted list.
    """
    result: list[dict] = []
    i, j = 0, 0

    while i < len(a) and j < len(b):
        if a[i][key] <= b[j][key]:
            result.append(a[i])
            i += 1
        else:
            result.append(b[j])
            j += 1

    result.extend(a[i:])
    result.extend(b[j:])
    return result


def merge_sorted_generators(
    a: Iterator[dict],
    b: Iterator[dict],
    key: str = "ts",
) -> Iterator[dict]:
    """
    Streaming merge using generators. Memory: O(1) beyond the two
    current records.

    This is the production approach for large files. Each input can
    be a file reader, database cursor, or Kafka consumer - anything
    that yields sorted records.
    """
    rec_a = next(a, None)
    rec_b = next(b, None)

    while rec_a is not None and rec_b is not None:
        if rec_a[key] <= rec_b[key]:
            yield rec_a
            rec_a = next(a, None)
        else:
            yield rec_b
            rec_b = next(b, None)

    # Drain remaining
    while rec_a is not None:
        yield rec_a
        rec_a = next(a, None)
    while rec_b is not None:
        yield rec_b
        rec_b = next(b, None)


def concat_and_sort(
    a: list[dict],
    b: list[dict],
    key: str = "ts",
) -> list[dict]:
    """
    Naive approach: concatenate and re-sort.

    Time: O((n+m) log(n+m))
    Space: O(n+m)

    Wastes the fact that inputs are already sorted.
    """
    combined = a + b
    combined.sort(key=lambda x: x[key])
    return combined


if __name__ == "__main__":
    # Correctness check
    stream_a = [
        {"ts": "2024-01-01T00:01", "event": "login", "user": "alice"},
        {"ts": "2024-01-01T00:05", "event": "click", "user": "alice"},
        {"ts": "2024-01-01T00:12", "event": "purchase", "user": "alice"},
    ]
    stream_b = [
        {"ts": "2024-01-01T00:03", "event": "login", "user": "bob"},
        {"ts": "2024-01-01T00:07", "event": "click", "user": "bob"},
        {"ts": "2024-01-01T00:15", "event": "logout", "user": "bob"},
    ]

    merged = merge_sorted_lists(stream_a, stream_b)
    timestamps = [r["ts"] for r in merged]
    assert timestamps == sorted(timestamps)
    assert len(merged) == 6
    print(f"Merged {len(stream_a)} + {len(stream_b)} -> {len(merged)} records")
    for r in merged:
        print(f"  {r['ts']} {r['user']:>8} {r['event']}")

    # Generator version
    gen_merged = list(merge_sorted_generators(iter(stream_a), iter(stream_b)))
    assert gen_merged == merged
    print("\nGenerator merge matches list merge.")

    # Benchmark
    print("\n--- Benchmark ---")
    import random

    random.seed(42)
    n = 500_000

    # Generate two sorted lists of timestamps
    base_a = sorted(random.randint(0, 10_000_000) for _ in range(n))
    base_b = sorted(random.randint(0, 10_000_000) for _ in range(n))
    list_a = [{"ts": t, "data": "x"} for t in base_a]
    list_b = [{"ts": t, "data": "x"} for t in base_b]

    start = time.perf_counter()
    result_merge = merge_sorted_lists(list_a, list_b)
    merge_time = time.perf_counter() - start
    print(f"Two-pointer merge: {merge_time:.3f}s ({n * 2:,} total records)")

    start = time.perf_counter()
    result_sort = concat_and_sort(list_a, list_b)
    sort_time = time.perf_counter() - start
    print(f"Concat + re-sort:  {sort_time:.3f}s ({n * 2:,} total records)")

    if merge_time < sort_time:
        print(f"Two-pointer merge was {sort_time / merge_time:.1f}x faster")
    else:
        print(
            f"Concat+sort was {merge_time / sort_time:.1f}x faster"
            " (Timsort is C-optimized for sorted runs)"
        )

    # Generator benchmark (the real advantage: streaming with O(1) memory)
    start = time.perf_counter()
    count = 0
    for _ in merge_sorted_generators(iter(list_a), iter(list_b)):
        count += 1
    gen_time = time.perf_counter() - start
    print(f"Generator merge:   {gen_time:.3f}s ({count:,} records, O(1) memory)")
    print()
    print("Note: Timsort (Python's built-in sort) is C-implemented and detects")
    print("sorted runs, making it surprisingly fast on pre-sorted input. The")
    print("two-pointer merge wins on memory: the generator version holds only")
    print("two records at a time, enabling processing of files larger than RAM.")
