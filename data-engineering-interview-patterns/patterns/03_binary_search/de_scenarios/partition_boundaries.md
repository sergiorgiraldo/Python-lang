# DE Scenario: Finding Partition Boundaries for Backfill

**Run it:** `uv run python -m patterns.03_binary_search.de_scenarios.partition_boundaries`

## Real-World Context

You need to backfill a date-partitioned table. The data lives in sorted partitions (by date or ID range), and you need to figure out which partitions overlap with your backfill range. Scanning all partition metadata linearly works for 50 partitions but not for 50,000.

Binary search finds the start and end partitions for any date range in O(log n), no matter how many partitions exist.

## The Problem

Given a sorted list of partition boundaries and a target date range, find which partitions need to be processed.

## Why Binary Search

Partition boundaries are sorted by definition. Finding "the first partition that could contain data >= start_date" is exactly the left-boundary binary search from LeetCode #35.

A linear scan through 50,000 partition boundaries takes up to 50,000 comparisons. Binary search takes about 16.

## Production Considerations

**Partition metadata source:** In practice, you'd query a catalog (Hive metastore, Glue catalog, Iceberg metadata) for partition boundaries. The catalog might already support range queries, but understanding the algorithm helps when building your own partitioning logic or when the catalog doesn't support efficient range lookups.

**Off-by-one at boundaries:** A partition covers a range [start, end). If your backfill start falls exactly on a partition boundary, make sure you include that partition. The left-boundary binary search handles this naturally.

**Non-uniform partitions:** Real partitions aren't always uniform (daily partitions might have gaps for days with no data). Binary search still works as long as the boundaries are sorted - it just means some partitions in the range might be empty.

**Combining with partition pruning:** Most query engines do this automatically for simple date predicates. This pattern matters when you're building custom tooling, like a backfill framework that needs to enumerate affected partitions programmatically.

## Worked Example

When splitting sorted data into partitions (by date range, value range or size budget), binary search finds the boundary indices in O(log n) per boundary instead of scanning the entire dataset.

This is boundary-finding binary search: "where is the first element >= this value?"

```
Sorted dataset of 10M records by timestamp:
  [2024-01-01 00:00, ..., 2024-12-31 23:59]

Need quarterly partition boundaries (Q1, Q2, Q3, Q4):
  Q2 starts at first record >= 2024-04-01
  Q3 starts at first record >= 2024-07-01
  Q4 starts at first record >= 2024-10-01

Binary search for each boundary:
  Q2 boundary: bisect_left(timestamps, "2024-04-01")
    ~24 comparisons for 10M records (log₂(10M) ≈ 23.3)
    Result: index 2,478,301 → Q1 is records [0..2,478,300]

  Q3 boundary: bisect_left(timestamps, "2024-07-01")
    ~24 comparisons → index 4,982,100

  Q4 boundary: bisect_left(timestamps, "2024-10-01")
    ~24 comparisons → index 7,513,422

Total: ~72 comparisons to partition 10M records.
Linear scan for each boundary would take ~25M comparisons total.
```

## Connection to LeetCode

This is [35. Search Insert Position](../../problems/035_search_insert.md) applied twice: once to find the starting partition and once to find the ending partition. The left-boundary variant gives you the insertion point, which is exactly the first partition >= your start date.

## Benchmark

See the `.py` file's output for timing comparisons at scale (100K partitions).
