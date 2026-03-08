"""
DE Scenario: Incremental Diff Detection

Compares source and target datasets to classify records as
INSERT, UPDATE, DELETE or UNCHANGED. Uses hash maps for O(n+m)
comparison.

Pattern: Hash Map - Set Operations + Complement Lookup
"""

import hashlib
import json
import random
import time
from dataclasses import dataclass


@dataclass
class DiffResult:
    """Result of comparing source against target."""

    inserts: list[dict]
    updates: list[dict]
    deletes: list[dict]
    unchanged: list[dict]

    @property
    def summary(self) -> str:
        return (
            f"inserts={len(self.inserts)}, updates={len(self.updates)}, "
            f"deletes={len(self.deletes)}, unchanged={len(self.unchanged)}"
        )


def record_hash(record: dict, exclude_keys: set[str] | None = None) -> str:
    """
    Compute a content hash for change detection.

    Excludes specified keys (like 'id' or 'updated_at') so the
    hash only reflects business data changes.
    """
    if exclude_keys is None:
        exclude_keys = set()
    filtered = {k: v for k, v in sorted(record.items()) if k not in exclude_keys}
    content = json.dumps(filtered, sort_keys=True, default=str)
    return hashlib.md5(content.encode()).hexdigest()


def detect_changes(
    source: list[dict],
    target: list[dict],
    key: str = "id",
) -> DiffResult:
    """
    Compare source and target to find new, changed and deleted records.

    Builds hash maps from both datasets keyed by the primary key.
    Computes content hashes to detect changes without comparing
    every field individually.

    Time: O(n + m) where n = source records, m = target records
    Space: O(n + m)

    Args:
        source: Current state of the data.
        target: Previously loaded state.
        key: Primary key field name.

    Returns:
        DiffResult with classified records.
    """
    # Build lookup maps
    source_map = {r[key]: r for r in source}
    target_map = {r[key]: r for r in target}

    # Compute content hashes (exclude the key field itself)
    source_hashes = {
        k: record_hash(r, exclude_keys={key}) for k, r in source_map.items()
    }
    target_hashes = {
        k: record_hash(r, exclude_keys={key}) for k, r in target_map.items()
    }

    source_keys = set(source_map.keys())
    target_keys = set(target_map.keys())

    inserts = [source_map[k] for k in source_keys - target_keys]
    deletes = [target_map[k] for k in target_keys - source_keys]

    updates = []
    unchanged = []
    for k in source_keys & target_keys:
        if source_hashes[k] != target_hashes[k]:
            updates.append(source_map[k])
        else:
            unchanged.append(source_map[k])

    return DiffResult(
        inserts=inserts,
        updates=updates,
        deletes=deletes,
        unchanged=unchanged,
    )


def detect_changes_naive(
    source: list[dict],
    target: list[dict],
    key: str = "id",
) -> DiffResult:
    """
    Naive O(n*m) approach for comparison.

    For each source record, scan the entire target list.
    Then scan source for each target record to find deletes.
    """
    inserts = []
    updates = []
    unchanged = []

    for s_rec in source:
        found = False
        for t_rec in target:
            if s_rec[key] == t_rec[key]:
                found = True
                # Compare all non-key fields
                s_data = {k: v for k, v in s_rec.items() if k != key}
                t_data = {k: v for k, v in t_rec.items() if k != key}
                if s_data != t_data:
                    updates.append(s_rec)
                else:
                    unchanged.append(s_rec)
                break
        if not found:
            inserts.append(s_rec)

    deletes = []
    source_keys = {r[key] for r in source}
    for t_rec in target:
        if t_rec[key] not in source_keys:
            deletes.append(t_rec)

    return DiffResult(
        inserts=inserts,
        updates=updates,
        deletes=deletes,
        unchanged=unchanged,
    )


if __name__ == "__main__":
    # Correctness check
    target = [
        {"id": 1, "name": "Alice", "email": "alice@old.com"},
        {"id": 2, "name": "Bob", "email": "bob@co.com"},
        {"id": 3, "name": "Charlie", "email": "charlie@co.com"},
    ]
    source = [
        {"id": 1, "name": "Alice", "email": "alice@new.com"},
        {"id": 2, "name": "Bob", "email": "bob@co.com"},
        {"id": 4, "name": "Diana", "email": "diana@co.com"},
    ]

    result = detect_changes(source, target)
    print(f"Diff result: {result.summary}")
    assert len(result.inserts) == 1 and result.inserts[0]["id"] == 4
    assert len(result.updates) == 1 and result.updates[0]["id"] == 1
    assert len(result.deletes) == 1 and result.deletes[0]["id"] == 3
    assert len(result.unchanged) == 1 and result.unchanged[0]["id"] == 2
    print("Correctness check passed.")

    # Verify naive matches optimal
    naive_result = detect_changes_naive(source, target)
    assert len(naive_result.inserts) == len(result.inserts)
    assert len(naive_result.updates) == len(result.updates)
    assert len(naive_result.deletes) == len(result.deletes)
    print("Naive matches optimal.")

    # Benchmark
    print("\n--- Benchmark ---")
    random.seed(42)

    num_records = 50_000
    change_rate = 0.1
    delete_rate = 0.05
    insert_rate = 0.05

    target_large = [
        {"id": i, "name": f"User{i}", "email": f"user{i}@co.com"}
        for i in range(num_records)
    ]

    # Build source: modify some, delete some, add some
    source_large = []
    for rec in target_large:
        if random.random() < delete_rate:
            continue  # deleted
        if random.random() < change_rate:
            source_large.append({**rec, "email": f"updated_{rec['id']}@co.com"})
        else:
            source_large.append(rec)

    # Add new records
    new_count = int(num_records * insert_rate)
    for i in range(num_records, num_records + new_count):
        source_large.append({"id": i, "name": f"New{i}", "email": f"new{i}@co.com"})

    start = time.perf_counter()
    result = detect_changes(source_large, target_large)
    optimal_time = time.perf_counter() - start
    print(f"Hash map diff: {optimal_time:.3f}s ({result.summary})")

    # Naive on smaller input
    small_target = target_large[:2_000]
    small_source = [r for r in source_large if r["id"] < 2_000]
    start = time.perf_counter()
    detect_changes_naive(small_source, small_target)
    naive_time = time.perf_counter() - start
    projected = naive_time * (num_records / 2_000)
    print(f"Naive (2K records): {naive_time:.3f}s")
    print(f"Naive projected for {num_records:,}: ~{projected:.1f}s")
    print(f"Speedup: ~{projected / optimal_time:.0f}x")
