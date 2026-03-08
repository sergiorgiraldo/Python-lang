# DE Scenario: Data Compaction (In-Place Cleanup)

**Run it:** `uv run python -m patterns.02_two_pointers.de_scenarios.data_compaction`

## Real-World Context

You have a dataset with records that need to be removed - soft-deleted rows, expired entries, null placeholder records, duplicate entries in sorted data. Rather than creating a new copy of the entire dataset minus the junk, you compact in place.

This is the same operation as LSM-tree compaction (RocksDB, LevelDB, Cassandra), log compaction in Kafka or partition maintenance in data warehouses.

## The Problem

```python
# Sorted event log with some records marked for deletion
events = [
    {"id": 1, "status": "active", "data": "..."},
    {"id": 2, "status": "deleted", "data": "..."},  # remove
    {"id": 3, "status": "active", "data": "..."},
    {"id": 4, "status": "deleted", "data": "..."},  # remove
    {"id": 5, "status": "active", "data": "..."},
    {"id": 5, "status": "active", "data": "..."},   # duplicate
]

# Goal: compact to only active, deduplicated records, in place
```

## Worked Example

Data compaction removes unwanted records in-place. Same read/write pattern as Remove Duplicates and Move Zeroes applied to production data.

```
Records (some flagged for deletion):
  [(ts=1, "valid", A), (ts=2, "expired", B), (ts=3, "valid", C),
   (ts=4, "expired", D), (ts=5, "expired", E), (ts=6, "valid", F),
   (ts=7, "valid", G), (ts=8, "expired", H)]

  write=0
  read=0: "valid"   → write[0]=A. write=1.
  read=1: "expired" → skip.
  read=2: "valid"   → write[1]=C. write=2.
  read=3: "expired" → skip.
  read=4: "expired" → skip.
  read=5: "valid"   → write[2]=F. write=3.
  read=6: "valid"   → write[3]=G. write=4.
  read=7: "expired" → skip.

  Compacted: [A, C, F, G]. Truncate at write=4.
  Single pass, O(n), no extra memory.
```

## Why Two Pointers

The read/write pointer pattern from LeetCode 26 (Remove Duplicates) and 283 (Move Zeroes) applies directly. Read scans every record. Write only advances when a record should be kept. O(n) time, O(1) extra space.

Combining multiple cleanup operations in a single pass is the key efficiency gain. Instead of: filter deleted → deduplicate → return (three passes), do everything in one scan.

## Production Considerations

**Compaction triggers.** Don't compact on every write. Common strategies: compact when deleted records exceed a threshold (e.g., 20% of total), on a schedule or when storage exceeds a limit.

**Tombstones vs hard deletes.** In distributed systems, you often can't just remove records - other replicas need to know the record was deleted. Tombstones (markers that say "this was deleted") persist for a retention period before compaction removes them.

**Write amplification.** Compaction rewrites data. In LSM-trees, this is a significant cost. The tradeoff: more frequent compaction improves read performance but increases write amplification.

## Connection to LeetCode

This combines LeetCode 26 (Remove Duplicates) and 283 (Move Zeroes) - the read/write pointer pattern applied to filtering and deduplication in one pass.

See: [26. Remove Duplicates](../problems/026_remove_duplicates.md), [283. Move Zeroes](../problems/283_move_zeroes.md)

## Benchmark

See the `.py` file for timing at scale. At 1M records, in-place compaction runs in ~0.05s vs ~0.08s for the naive copy approach. In-place uses no extra space; the naive version allocates ~2M list entries.
