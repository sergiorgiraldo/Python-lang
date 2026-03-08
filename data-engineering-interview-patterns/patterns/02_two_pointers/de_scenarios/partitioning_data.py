"""
DE Scenario: Partitioning Data by Category

Demonstrates in-place and copy-based partitioning for routing
records to different processing paths. Includes two-way and
three-way partition variants.

Pattern: Two Pointers - Partition (Dutch National Flag variant)
"""

import time
from collections.abc import Callable


def partition_two_way(
    records: list[dict],
    predicate: Callable[[dict], bool],
) -> int:
    """
    Two-way partition: records matching predicate come first.

    Returns the index where the second group starts.
    Modifies the list in place. NOT stable (relative order may change).

    Time: O(n)  Space: O(1)
    """
    write = 0
    for read in range(len(records)):
        if predicate(records[read]):
            records[write], records[read] = records[read], records[write]
            write += 1
    return write


def partition_three_way(
    records: list[dict],
    classify: Callable[[dict], int],
) -> tuple[int, int]:
    """
    Three-way partition using Dutch National Flag algorithm.

    The classify function should return:
        0 = first group (e.g., valid)
        1 = middle group (e.g., suspicious)
        2 = last group (e.g., invalid)

    Returns (boundary1, boundary2) where:
        records[:boundary1] = group 0
        records[boundary1:boundary2] = group 1
        records[boundary2:] = group 2

    Time: O(n)  Space: O(1)
    """
    low, mid, high = 0, 0, len(records) - 1

    while mid <= high:
        category = classify(records[mid])
        if category == 0:
            records[low], records[mid] = records[mid], records[low]
            low += 1
            mid += 1
        elif category == 1:
            mid += 1
        else:
            records[mid], records[high] = records[high], records[mid]
            high -= 1

    return low, mid


def partition_copy_based(
    records: list[dict],
    classify: Callable[[dict], int],
    num_groups: int = 3,
) -> dict[int, list[dict]]:
    """
    Copy-based partitioning into N groups.

    Creates separate lists for each group. Stable (preserves order
    within groups). Uses O(n) extra space.

    Simpler and preserves order, but uses more memory.
    """
    groups: dict[int, list[dict]] = {i: [] for i in range(num_groups)}
    for record in records:
        category = classify(record)
        groups[category].append(record)
    return groups


def validate_record(record: dict) -> int:
    """
    Classify a record for the partitioning demo.

    Returns:
        0 = valid
        1 = suspicious (negative amount, unusually high amount)
        2 = invalid (missing or empty required fields)
    """
    # Invalid: missing required fields
    email = record.get("email")
    if not email:
        return 2

    amount = record.get("amount")
    if amount is None:
        return 2

    # Suspicious: negative or very high amount
    if amount < 0 or amount > 10_000:
        return 1

    return 0


if __name__ == "__main__":
    # Correctness check
    records = [
        {"id": 1, "email": "alice@co.com", "amount": 50},
        {"id": 2, "email": None, "amount": 30},
        {"id": 3, "email": "bob@co.com", "amount": -5},
        {"id": 4, "email": "charlie@co.com", "amount": 100},
        {"id": 5, "email": "", "amount": 0},
        {"id": 6, "email": "diana@co.com", "amount": 75},
    ]

    # Two-way: valid vs not valid
    test_two = records.copy()
    boundary = partition_two_way(test_two, lambda r: validate_record(r) == 0)
    print(f"Two-way partition: {boundary} valid, {len(test_two) - boundary} not valid")
    assert boundary == 3  # 3 valid records

    # Three-way: valid / suspicious / invalid
    test_three = records.copy()
    b1, b2 = partition_three_way(test_three, validate_record)
    valid = test_three[:b1]
    suspicious = test_three[b1:b2]
    invalid = test_three[b2:]
    print(
        f"Three-way partition: {len(valid)} valid,"
        f" {len(suspicious)} suspicious, {len(invalid)} invalid"
    )
    assert len(valid) == 3
    assert len(suspicious) == 1
    assert len(invalid) == 2

    # Copy-based (for comparison)
    groups = partition_copy_based(records, validate_record)
    print(
        f"Copy-based: {len(groups[0])} valid,"
        f" {len(groups[1])} suspicious, {len(groups[2])} invalid"
    )
    assert len(groups[0]) == 3
    assert len(groups[1]) == 1
    assert len(groups[2]) == 2
    print("All approaches agree on counts.")

    # Benchmark
    print("\n--- Benchmark ---")
    import random

    random.seed(42)
    n = 2_000_000

    large_records = []
    for i in range(n):
        r = random.random()
        if r < 0.05:
            # Invalid: missing email
            large_records.append({"id": i, "email": None, "amount": 50})
        elif r < 0.10:
            # Suspicious: negative amount
            large_records.append({"id": i, "email": f"u{i}@co.com", "amount": -10})
        else:
            # Valid
            large_records.append(
                {
                    "id": i,
                    "email": f"u{i}@co.com",
                    "amount": random.randint(1, 500),
                }
            )

    # In-place three-way
    test_inplace = large_records.copy()
    start = time.perf_counter()
    b1, b2 = partition_three_way(test_inplace, validate_record)
    inplace_time = time.perf_counter() - start
    print(
        f"In-place 3-way:  {inplace_time:.3f}s"
        f" ({b1:,} valid, {b2 - b1:,} suspicious,"
        f" {n - b2:,} invalid)"
    )

    # Copy-based
    start = time.perf_counter()
    groups = partition_copy_based(large_records, validate_record)
    copy_time = time.perf_counter() - start
    print(
        f"Copy-based:      {copy_time:.3f}s"
        f" ({len(groups[0]):,} valid, {len(groups[1]):,} suspicious,"
        f" {len(groups[2]):,} invalid)"
    )

    print(f"Speed difference: {copy_time / inplace_time:.1f}x")
    print(
        f"Memory: in-place modifies original;"
        f" copy-based allocates {n:,} new list entries"
    )
