# DE Scenario: Partitioning Data by Category

**Run it:** `uv run python -m patterns.02_two_pointers.de_scenarios.partitioning_data`

## Real-World Context

You need to separate records into categories before routing them to different processing paths. Valid records go to the main pipeline. Records that fail validation go to a review queue. Records with missing required fields go to a dead letter queue.

This is a data quality gate - a common pattern at the boundary between ingestion and transformation.

## The Problem

```python
records = [
    {"id": 1, "email": "alice@co.com", "amount": 50},    # valid
    {"id": 2, "email": None, "amount": 30},                # invalid: no email
    {"id": 3, "email": "bob@co.com", "amount": -5},        # suspicious: negative amount
    {"id": 4, "email": "charlie@co.com", "amount": 100},   # valid
    {"id": 5, "email": "", "amount": 0},                    # invalid: empty email
    {"id": 6, "email": "diana@co.com", "amount": 75},      # valid
]

# Goal: partition into valid / suspicious / invalid
# without creating three separate filtered copies
```

## Worked Example

Partitioning sorted data into segments by detecting boundary changes. Because data is sorted by the partition key, all records in each partition are contiguous.

```
Records sorted by date:
  [("2024-01-15", evt_1), ("2024-01-15", evt_2), ("2024-01-15", evt_3),
   ("2024-01-16", evt_4), ("2024-01-16", evt_5),
   ("2024-01-17", evt_6), ("2024-01-17", evt_7), ("2024-01-17", evt_8)]

  read=0: date=01-15. New partition → start writing to 2024-01-15/
  read=1-2: same date. Continue.
  read=3: date=01-16. BOUNDARY. Close 01-15 (3 records). Start 01-16.
  read=4: same. Continue.
  read=5: date=01-17. BOUNDARY. Close 01-16 (2 records). Start 01-17.
  read=6-7: same. Continue.
  End. Close 01-17 (3 records).

  Result: 3 partitions from one scan. Same logic as writing
  partitioned Parquet files from sorted data.
```

## Why Two Pointers

The Dutch National Flag algorithm (LeetCode 75) partitions into three groups in one pass with O(1) extra space. For two groups, a simple read/write partition works. For three groups, the three-pointer variant handles it.

In practice, creating filtered copies is fine for small data. But when you're processing millions of records, the memory savings of in-place partitioning add up. And in streaming contexts, you can't "go back" to re-read data for a second filter pass.

## When to Use In-Place vs Filtered Copies

**Use in-place (two pointers)** when: memory is tight, data is large, you need to avoid intermediate copies or you're in a streaming context.

**Use filtered copies** when: data is small, readability matters more than performance or you need to preserve the original order within each group (in-place partitioning may not be stable).

## Why Stability Matters for Data Engineering

The Dutch National Flag partition is **not stable** - records within the same category may end up in a different relative order than they started. For LeetCode problems this doesn't matter (you're sorting values, not records). For data pipelines, it can.

Consider: you're partitioning events into valid/suspicious/invalid. The events arrive in timestamp order. After an unstable partition, the valid events might no longer be in timestamp order. If a downstream consumer assumes time-ordering within each category, it breaks silently.

**When this matters:**
- The downstream step assumes ordering within each partition
- Records have timestamps, sequence numbers, or other ordering you need to preserve
- Audit trails or replay logic depends on insertion order

**When it doesn't matter:**
- Each partition gets re-sorted or re-indexed downstream anyway
- Records are independent (no ordering assumption)
- You're routing to different systems that each handle their own ordering

The copy-based approach (`partition_copy_based` in the code) is stable by construction - it appends records in order to each group's list. If you need in-place performance with stability, you'd need a different algorithm (like a stable partition, which requires O(n) extra space anyway, negating the in-place advantage).

## Connection to LeetCode

This is LeetCode 75 (Sort Colors) and 283 (Move Zeroes) applied to data quality routing. The three-way partition from Dutch National Flag maps directly to valid/suspicious/invalid classification.

See: [75. Sort Colors](../problems/075_sort_colors.md), [283. Move Zeroes](../problems/283_move_zeroes.md)

## Benchmark

See the `.py` file for comparisons at scale. At 2M records: in-place 3-way partition runs in ~0.3s, copy-based in ~0.1s. The copy-based approach is faster in Python (fewer swaps, more cache-friendly appends) but uses O(n) extra space.
