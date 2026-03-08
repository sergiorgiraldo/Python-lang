# DE Scenario: Incremental Sync Between Sorted Sources

**Run it:** `uv run python -m patterns.02_two_pointers.de_scenarios.incremental_sync`

## Real-World Context

You have two sorted datasets - typically a "source of truth" and a "target" that should mirror it. You need to find what's been added, removed and changed. Both datasets are sorted by the same key.

This is different from the hash map diff detection scenario. When both inputs are already sorted, you can diff them in O(n + m) time with O(1) extra space using two pointers. No hash maps needed. This matters when the datasets are too large to fit in memory.

Examples: syncing a database table with a file export, comparing two sorted partition files, reconciling two sorted ledgers.

## The Problem

```python
# Sorted source (current truth)
source = [
    {"id": 1, "name": "Alice", "email": "alice@new.com"},
    {"id": 2, "name": "Bob", "email": "bob@co.com"},
    {"id": 4, "name": "Diana", "email": "diana@co.com"},
]

# Sorted target (what we have loaded)
target = [
    {"id": 1, "name": "Alice", "email": "alice@old.com"},
    {"id": 2, "name": "Bob", "email": "bob@co.com"},
    {"id": 3, "name": "Charlie", "email": "charlie@co.com"},
]

# id=1: changed (email differs)
# id=2: unchanged
# id=3: deleted (in target but not source)
# id=4: new (in source but not target)
```

## Worked Example

Two pointers classify every record between two sorted datasets in a single pass: matches (unchanged/updated), source-only (inserts), target-only (deletes). This is database MERGE/CDC logic.

```
Source (sorted by ID): [101, 103, 105, 107, 109, 111]
Target (sorted by ID): [101, 102, 105, 107, 108, 111]

  src→101, tgt→101: match → compare content → UNCHANGED. Both advance.
  src→103, tgt→102: 102 < 103 → target-only → DELETE 102. Advance tgt.
  src→103, tgt→105: 103 < 105 → source-only → INSERT 103. Advance src.
  src→105, tgt→105: match → UNCHANGED. Both advance.
  src→107, tgt→107: match → content differs → UPDATE. Both advance.
  src→109, tgt→108: 108 < 109 → DELETE 108. Advance tgt.
  src→109, tgt→111: 109 < 111 → INSERT 109. Advance src.
  src→111, tgt→111: match → UNCHANGED. Both advance.

  inserts: [103, 109], updates: [107], deletes: [102, 108], unchanged: [101, 105, 111]
  Single pass, no hash maps. O(n + m).
```

## Why Two Pointers

Both lists are sorted by ID. Walk through them simultaneously:
- If source ID < target ID → source has a record target doesn't (INSERT)
- If source ID > target ID → target has a record source doesn't (DELETE)
- If IDs match → compare fields to detect UPDATE or UNCHANGED

O(n + m) time, O(1) extra space. Processes records sequentially, which means it works with file iterators and database cursors.

## Comparing Approaches: Two Pointers vs Hash Map

This scenario uses two pointers for O(n + m) diff detection on **sorted** data with O(1) extra space. The hash map approach (from Pattern 01) handles **unsorted** data at the cost of O(n + m) space:

See: [Incremental Diff Detection (Hash Map)](../../../01_hash_map/de_scenarios/incremental_diff_detection.md)

| Approach | Time | Extra Space | Requires Sorted Input |
|----------|------|-------------|----------------------|
| Two pointers (this scenario) | O(n + m) | O(1) | Yes |
| Hash map | O(n + m) | O(n + m) | No |

Choose based on your data. Database exports sorted by primary key? Two pointers. Unsorted API responses or event streams? Hash map. If you have unsorted data but the datasets are too large for the hash map approach, sort both first. The O(n log n) sort cost is a one-time price for O(1)-space diffing.

## Production Considerations

**Choose based on your data.** If data is already sorted (common for database exports, partitioned files, indexed queries) - use two pointers. If unsorted, sorting first adds O(n log n), which may be worse than the hash map approach.

**Handle the comparison carefully.** Field-by-field comparison is brittle if schemas change. Content hashing works but adds compute cost. In practice, a last-modified timestamp or version number is the cheapest change detection.

## Connection to LeetCode

This combines the merge pattern from LeetCode 88 with comparison logic. Two sorted sequences, walked in parallel, classified by their relationship.

See: [88. Merge Sorted Array](../problems/088_merge_sorted.md)

## Benchmark

See the `.py` file for timing at scale. At 100K records, two-pointer sync and streaming sync both complete in ~0.04s with O(1) extra space.
