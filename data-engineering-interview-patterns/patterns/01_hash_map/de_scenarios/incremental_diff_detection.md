# DE Scenario: Incremental Diff Detection (New / Changed / Deleted)

**Run it:** `uv run python -m patterns.01_hash_map.de_scenarios.incremental_diff_detection`

## Real-World Context

You're running an incremental pipeline. Source data has changed since your last run. You need to figure out which records are new, which changed and which were deleted - then apply the appropriate action.

This is the core of any incremental load strategy. Full refreshes are simple but expensive. Incremental loads are cheaper but require diff detection.

## The Problem

```python
# What we loaded last time
target = [
    {"id": 1, "name": "Alice", "email": "alice@old.com"},
    {"id": 2, "name": "Bob", "email": "bob@co.com"},
    {"id": 3, "name": "Charlie", "email": "charlie@co.com"},
]

# What the source looks like now
source = [
    {"id": 1, "name": "Alice", "email": "alice@new.com"},  # changed
    {"id": 2, "name": "Bob", "email": "bob@co.com"},       # unchanged
    {"id": 4, "name": "Diana", "email": "diana@co.com"},   # new
]

# id=3 is missing from source -> deleted
```

## Worked Example

Delta/incremental loads avoid reprocessing unchanged data. The technique: hash the current state of each record and store those hashes in a dict keyed by record ID. On the next run, compare new hashes against stored ones. New IDs are inserts, changed hashes are updates, missing IDs are deletes. Each comparison is O(1).

This is the same "have I seen this before?" pattern as Contains Duplicate, applied to change detection between two snapshots of a dataset.

```
Yesterday's snapshot (loaded into a dict - key = record ID, value = content hash):
  previous = {
    "user_101": "hash_abc",   (Alice, active)
    "user_102": "hash_def",   (Bob, active)
    "user_103": "hash_ghi",   (Carol, inactive)
    "user_104": "hash_jkl",   (Dave, active)
    "user_105": "hash_mno",   (Eve, active)
  }

Today's snapshot:
  current = {
    "user_101": "hash_abc",   (Alice, no changes)
    "user_102": "hash_xyz",   (Bob, address changed → different hash)
    "user_103": "hash_ghi",   (Carol, no changes)
    "user_105": "hash_mno",   (Eve, no changes)
    "user_106": "hash_pqr",   (Frank, new employee)
  }

Diff detection (two passes using dict lookups):
  Pass 1 - scan current keys against previous:
    user_101: in previous? Yes (O(1) lookup). Same hash? abc==abc → UNCHANGED
    user_102: in previous? Yes. Same hash? xyz != def           → UPDATED
    user_103: in previous? Yes. Same hash? ghi==ghi             → UNCHANGED
    user_105: in previous? Yes. Same hash? mno==mno             → UNCHANGED
    user_106: in previous? No                                   → NEW (insert)

  Pass 2 - scan previous keys not in current:
    user_101: in current? Yes → skip (already handled)
    user_102: in current? Yes → skip
    user_103: in current? Yes → skip
    user_104: in current? No  → DELETED
    user_105: in current? Yes → skip

Result:
  new:       [user_106]     → INSERT into target table
  updated:   [user_102]     → UPDATE in target table
  deleted:   [user_104]     → soft-DELETE or remove from target
  unchanged: [user_101, user_103, user_105] → skip (no processing needed)

Instead of reloading all records, we only process 3 changes.
At production scale (50M records, 0.1% daily change rate), this
means processing 50K records instead of 50M. 10 dict lookups
per record (5 in each pass) vs a full table comparison.
```

## Why Hash Maps

Building hash maps keyed by ID from both source and target lets you classify every record in O(n + m) time. Without maps, you'd need nested loops for O(n * m) or sorting both sets for O(n log n + m log m).

## The SQL Equivalent

This is a FULL OUTER JOIN with CASE logic:

```sql
SELECT
    COALESCE(s.id, t.id) as id,
    CASE
        WHEN t.id IS NULL THEN 'INSERT'
        WHEN s.id IS NULL THEN 'DELETE'
        WHEN s.hash != t.hash THEN 'UPDATE'
        ELSE 'UNCHANGED'
    END as action
FROM source s
FULL OUTER JOIN target t ON s.id = t.id
```

The Python hash map approach is the same logic without SQL.

## Comparing Approaches: Hash Map vs Two Pointers

This scenario uses hash maps for O(n + m) diff detection on **unsorted** data. If your source and target are both **sorted by key**, the two-pointer approach achieves the same O(n + m) time with O(1) extra space:

See: [Incremental Sync (Two Pointers)](../../../02_two_pointers/de_scenarios/incremental_sync.md)

| Approach | Time | Extra Space | Requires Sorted Input |
|----------|------|-------------|----------------------|
| Hash map (this scenario) | O(n + m) | O(n + m) | No |
| Two pointers | O(n + m) | O(1) | Yes |

Choose based on your data. Database exports sorted by primary key? Two pointers. Unsorted API responses or event streams? Hash map. If unsorted data is large enough that O(n + m) extra space is a concern, consider sorting first - the O(n log n) sort cost may be worth the O(1) space during the diff.

## Production Considerations

**Use hashing for change detection.** Comparing every field is expensive and brittle (what if a column is added?). Hash the row content and compare hashes. If hashes differ, the row changed.

**Ordering matters for application.** Apply deletes before inserts if there are ID collisions. Or better, use MERGE/upsert at the target.

**Track your watermark.** Store the max timestamp or sequence number you've processed so the next run knows where to start.

## Connection to LeetCode

This is the Two Sum complement pattern and set intersection/difference combined. Build maps from both sides, then compare keys and values.

See: [1. Two Sum](../problems/001_two_sum.md), [217. Contains Duplicate](../problems/217_contains_duplicate.md)

## Benchmark

See the `.py` file for timing comparisons. At 50K records, hash map diff runs in ~0.2s vs a projected ~0.7s for the naive approach - roughly 4x faster.
