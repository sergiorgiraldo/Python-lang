# DE Scenario: Time-Based Log Lookup

**Run it:** `uv run python -m patterns.03_binary_search.de_scenarios.log_lookup`

## Real-World Context

You have a sorted log file (or sorted event stream) and need to find events near a specific timestamp. Maybe it's for debugging ("what happened around 2:47 PM?"), joining events from different systems by time or extracting a time window from a large sorted dataset.

Linear scanning works but gets slow on large logs. Binary search finds the starting position in O(log n), then you read forward from there.

## The Problem

Given a list of log entries sorted by timestamp, find all entries within a time window [start, end].

## Why Binary Search

Logs sorted by timestamp are the ideal binary search input. The left-boundary variant finds the first entry >= start_time. From there, scan forward until you pass end_time.

This is the same pattern as Python's `bisect.bisect_left()` and directly maps to [LeetCode #35 (Search Insert Position)](../../problems/035_search_insert.md).

## Production Considerations

**File-level vs in-memory:** For small logs loaded into memory, use `bisect`. For large log files on disk, binary search on the file requires seeking to byte positions, reading a line, parsing the timestamp and comparing. Tools like `grep` with sorted files or index files make this practical.

**Approximate timestamps:** Log timestamps might not be perfectly sorted (clock skew between servers, async writes). Allow a small buffer before your start time to catch slightly out-of-order entries.

**Index structures:** In production, you wouldn't binary search a raw log file. Databases use B-tree indexes (which are binary search trees). Columnar formats like Parquet store min/max statistics per row group for the same purpose. Understanding the algorithm helps you understand why these tools work.

## Worked Example

Looking up the first log entry at or after a specific timestamp in a sorted log file. This is the same operation as TimeMap's get, applied to production log analysis.

```
Sorted log file (by timestamp, 5M entries):
  [2024-01-15 00:00:01.123, 2024-01-15 00:00:01.456, ..., 2024-01-15 23:59:59.987]

Query: "Show me the first log entry at or after 14:30:00"

  bisect_left(timestamps, "2024-01-15 14:30:00.000")
  ~23 comparisons (log₂(5M) ≈ 22.3)
  Result: index 3,021,445 → first entry at 14:30:00.012

From there, read forward for all entries in the time range.

Without binary search: scan from the beginning, checking each entry.
Average case: scan ~3M entries to reach the 14:30 mark.
With binary search: 23 comparisons to jump directly there.
```

## Connection to LeetCode

This combines [35. Search Insert Position](../../problems/035_search_insert.md) (find the starting point) with [981. Time Based Key-Value Store](../../problems/981_time_map.md) (timestamp-based lookup).

## Benchmark

See the `.py` file for timing comparisons on 1M log entries.
