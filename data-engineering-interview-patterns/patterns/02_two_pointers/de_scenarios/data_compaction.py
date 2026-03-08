"""
DE Scenario: Data Compaction

Demonstrates in-place compaction of sorted data - removing
deleted records and duplicates in a single pass using
read/write pointers.

Pattern: Two Pointers - Same Direction (Read/Write)
"""

import time
from typing import Any


def compact_deleted(
    records: list[dict],
    status_field: str = "status",
    deleted_value: str = "deleted",
) -> int:
    """
    Remove soft-deleted records in place.

    Returns the new length. Records beyond that index are garbage.

    Time: O(n)  Space: O(1)
    """
    write = 0
    for read in range(len(records)):
        if records[read][status_field] != deleted_value:
            records[write] = records[read]
            write += 1
    return write


def compact_duplicates_sorted(
    records: list[dict],
    key: str = "id",
) -> int:
    """
    Remove duplicate records from sorted data in place (keep first occurrence).

    Time: O(n)  Space: O(1)
    """
    if not records:
        return 0

    write = 1
    for read in range(1, len(records)):
        if records[read][key] != records[read - 1][key]:
            records[write] = records[read]
            write += 1
    return write


def compact_full(
    records: list[dict],
    key: str = "id",
    status_field: str = "status",
    deleted_value: str = "deleted",
) -> int:
    """
    Combined compaction: remove deleted AND deduplicate in one pass.

    For sorted data, this handles both operations simultaneously.
    The write pointer only advances when the record is:
    1. Not deleted, AND
    2. Not a duplicate of the previous written record

    Time: O(n)  Space: O(1)
    """
    if not records:
        return 0

    write = 0
    last_written_key: Any = None

    for read in range(len(records)):
        record = records[read]

        # Skip deleted records
        if record.get(status_field) == deleted_value:
            continue

        # Skip duplicates (compared against last written, not last read)
        if record[key] == last_written_key:
            continue

        records[write] = record
        last_written_key = record[key]
        write += 1

    return write


def compact_naive(
    records: list[dict],
    key: str = "id",
    status_field: str = "status",
    deleted_value: str = "deleted",
) -> list[dict]:
    """
    Naive approach: filter, then deduplicate as separate steps.
    Creates new lists at each step.

    Time: O(n)  Space: O(n) - creates multiple intermediate copies
    """
    # Step 1: filter deleted
    active = [r for r in records if r.get(status_field) != deleted_value]

    # Step 2: deduplicate (sorted assumption)
    if not active:
        return active

    deduped = [active[0]]
    for i in range(1, len(active)):
        if active[i][key] != active[i - 1][key]:
            deduped.append(active[i])

    return deduped


if __name__ == "__main__":
    # Correctness check
    events = [
        {"id": 1, "status": "active", "data": "a"},
        {"id": 2, "status": "deleted", "data": "b"},
        {"id": 3, "status": "active", "data": "c"},
        {"id": 4, "status": "deleted", "data": "d"},
        {"id": 5, "status": "active", "data": "e"},
        {"id": 5, "status": "active", "data": "e"},  # duplicate
    ]

    # Test individual operations
    test1 = events.copy()
    new_len = compact_deleted(test1)
    assert new_len == 4  # removed 2 deleted records
    print(f"After removing deleted: {new_len} records")

    test2 = events.copy()
    new_len = compact_duplicates_sorted(test2)
    assert new_len == 5  # removed 1 duplicate
    print(f"After deduplicating: {new_len} records")

    # Test combined compaction
    test3 = events.copy()
    new_len = compact_full(test3)
    assert new_len == 3  # removed 2 deleted + 1 duplicate
    remaining = test3[:new_len]
    assert [r["id"] for r in remaining] == [1, 3, 5]
    print(
        f"After full compaction: {new_len} records"
        f" -> ids {[r['id'] for r in remaining]}"
    )

    # Compare with naive
    naive_result = compact_naive(events)
    assert len(naive_result) == new_len
    assert [r["id"] for r in naive_result] == [r["id"] for r in remaining]
    print("Naive matches in-place result.")

    # Benchmark
    print("\n--- Benchmark ---")
    import random

    random.seed(42)
    n = 1_000_000
    delete_rate = 0.15
    dup_rate = 0.10

    large_records: list[dict] = []
    current_id = 0
    for _ in range(n):
        if random.random() < dup_rate and large_records:
            # Duplicate previous record
            large_records.append(large_records[-1].copy())
        else:
            current_id += 1
            status = "deleted" if random.random() < delete_rate else "active"
            large_records.append({"id": current_id, "status": status, "data": "x"})

    # In-place compaction
    test_inplace = large_records.copy()
    start = time.perf_counter()
    new_len = compact_full(test_inplace)
    inplace_time = time.perf_counter() - start
    print(f"In-place compaction: {inplace_time:.3f}s ({n:,} -> {new_len:,} records)")

    # Naive (filter + dedup with copies)
    start = time.perf_counter()
    naive_result = compact_naive(large_records)
    naive_time = time.perf_counter() - start
    print(
        f"Naive (copies):      {naive_time:.3f}s"
        f" ({n:,} -> {len(naive_result):,} records)"
    )

    assert new_len == len(naive_result)
    print(
        f"Memory: in-place uses no extra space; naive allocates ~{n * 2} list entries"
    )
