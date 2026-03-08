"""
DE Scenario: Incremental Sync Between Sorted Sources

Compares two sorted datasets using two pointers to classify
records as INSERT, UPDATE, DELETE or UNCHANGED. O(n+m) time,
O(1) extra space (beyond the output).

Pattern: Two Pointers - Parallel Walk on Sorted Sequences
"""

import time
from collections.abc import Iterator
from dataclasses import dataclass, field


@dataclass
class SyncResult:
    """Result of comparing sorted source against sorted target."""

    inserts: list[dict] = field(default_factory=list)
    updates: list[dict] = field(default_factory=list)
    deletes: list[dict] = field(default_factory=list)
    unchanged: list[dict] = field(default_factory=list)

    @property
    def summary(self) -> str:
        return (
            f"inserts={len(self.inserts)}, updates={len(self.updates)}, "
            f"deletes={len(self.deletes)}, unchanged={len(self.unchanged)}"
        )


def records_differ(a: dict, b: dict, key: str = "id") -> bool:
    """Compare two records ignoring the key field."""
    return any(a.get(k) != b.get(k) for k in set(a) | set(b) if k != key)


def sync_sorted(
    source: list[dict],
    target: list[dict],
    key: str = "id",
) -> SyncResult:
    """
    Compare sorted source and target using two pointers.

    Both inputs must be sorted by the key field. Walks through
    both simultaneously, classifying records by their relationship.

    Time: O(n + m) where n = source, m = target
    Space: O(1) extra (output is O(n + m) in the worst case)

    Args:
        source: Sorted current-state records.
        target: Sorted previously-loaded records.
        key: Primary key field name.

    Returns:
        SyncResult with classified records.
    """
    result = SyncResult()
    i, j = 0, 0

    while i < len(source) and j < len(target):
        s_key = source[i][key]
        t_key = target[j][key]

        if s_key < t_key:
            # Source has a record target doesn't -> INSERT
            result.inserts.append(source[i])
            i += 1
        elif s_key > t_key:
            # Target has a record source doesn't -> DELETE
            result.deletes.append(target[j])
            j += 1
        else:
            # Same key - check if content changed
            if records_differ(source[i], target[j], key):
                result.updates.append(source[i])
            else:
                result.unchanged.append(source[i])
            i += 1
            j += 1

    # Remaining source records are all inserts
    while i < len(source):
        result.inserts.append(source[i])
        i += 1

    # Remaining target records are all deletes
    while j < len(target):
        result.deletes.append(target[j])
        j += 1

    return result


def sync_sorted_streaming(
    source: Iterator[dict],
    target: Iterator[dict],
    key: str = "id",
) -> Iterator[tuple[str, dict]]:
    """
    Streaming version that yields (action, record) pairs.

    Memory: O(1) beyond the two current records.
    Suitable for datasets too large to fit in memory.
    """
    s_rec = next(source, None)
    t_rec = next(target, None)

    while s_rec is not None and t_rec is not None:
        s_key = s_rec[key]
        t_key = t_rec[key]

        if s_key < t_key:
            yield ("INSERT", s_rec)
            s_rec = next(source, None)
        elif s_key > t_key:
            yield ("DELETE", t_rec)
            t_rec = next(target, None)
        else:
            if records_differ(s_rec, t_rec, key):
                yield ("UPDATE", s_rec)
            else:
                yield ("UNCHANGED", s_rec)
            s_rec = next(source, None)
            t_rec = next(target, None)

    while s_rec is not None:
        yield ("INSERT", s_rec)
        s_rec = next(source, None)

    while t_rec is not None:
        yield ("DELETE", t_rec)
        t_rec = next(target, None)


if __name__ == "__main__":
    # Correctness check
    source = [
        {"id": 1, "name": "Alice", "email": "alice@new.com"},
        {"id": 2, "name": "Bob", "email": "bob@co.com"},
        {"id": 4, "name": "Diana", "email": "diana@co.com"},
    ]
    target = [
        {"id": 1, "name": "Alice", "email": "alice@old.com"},
        {"id": 2, "name": "Bob", "email": "bob@co.com"},
        {"id": 3, "name": "Charlie", "email": "charlie@co.com"},
    ]

    result = sync_sorted(source, target)
    print(f"Sync result: {result.summary}")
    assert len(result.inserts) == 1 and result.inserts[0]["id"] == 4
    assert len(result.updates) == 1 and result.updates[0]["id"] == 1
    assert len(result.deletes) == 1 and result.deletes[0]["id"] == 3
    assert len(result.unchanged) == 1 and result.unchanged[0]["id"] == 2
    print("Correctness check passed.")

    # Streaming version
    actions = list(sync_sorted_streaming(iter(source), iter(target)))
    assert len(actions) == 4
    print(f"Streaming sync: {len(actions)} actions emitted")
    for action, rec in actions:
        print(f"  {action:>10}: id={rec['id']} {rec.get('name', '')}")

    # Benchmark
    print("\n--- Benchmark ---")
    import random

    random.seed(42)
    n = 100_000
    change_rate = 0.1
    delete_rate = 0.05
    insert_rate = 0.05

    # Build sorted target
    target_large = [
        {"id": i, "name": f"User{i}", "email": f"u{i}@co.com"} for i in range(n)
    ]

    # Build sorted source with modifications
    source_large = []
    for rec in target_large:
        r = random.random()
        if r < delete_rate:
            continue
        if r < delete_rate + change_rate:
            source_large.append({**rec, "email": f"new_{rec['id']}@co.com"})
        else:
            source_large.append(rec)

    # Add new records at the end (keep sorted)
    new_count = int(n * insert_rate)
    for i in range(n, n + new_count):
        source_large.append({"id": i, "name": f"New{i}", "email": f"n{i}@co.com"})

    start = time.perf_counter()
    result = sync_sorted(source_large, target_large)
    elapsed = time.perf_counter() - start
    print(f"Two-pointer sync: {elapsed:.3f}s ({result.summary})")

    # Streaming version benchmark
    start = time.perf_counter()
    action_counts: dict[str, int] = {
        "INSERT": 0,
        "UPDATE": 0,
        "DELETE": 0,
        "UNCHANGED": 0,
    }
    for action, _rec in sync_sorted_streaming(iter(source_large), iter(target_large)):
        action_counts[action] += 1
    stream_elapsed = time.perf_counter() - start
    print(f"Streaming sync:   {stream_elapsed:.3f}s ({action_counts})")
