# Time Range Overlap Detection

**Run it:** `uv run python -m patterns.07_intervals.de_scenarios.time_range_overlap`

## Real-World Context

Your event ingestion pipeline is receiving duplicate events from multiple sources. Two events covering overlapping time ranges for the same entity might be duplicates or conflicts that need resolution. Detecting these overlaps efficiently is the first step.

## The Problem

Given a list of events with start and end times, find all pairs that overlap in time. Report the overlapping time range for each pair.

## Worked Example

Detecting overlapping partition date ranges - if two partitions overlap, they may contain duplicate data.

```
Partitions:
  [2024-01-01, 2024-01-15]
  [2024-01-10, 2024-01-20]  ← overlaps with first
  [2024-01-20, 2024-01-31]
  [2024-02-01, 2024-02-15]

Sort by start (already sorted). Check adjacent pairs:
  Jan 01-15 vs Jan 10-20: 10 < 15? YES → OVERLAP. Data duplication risk.
  Jan 10-20 vs Jan 20-31: 20 < 20? NO (end-exclusive) → ok.
  Jan 20-31 vs Feb 01-15: 01 < 31? Depends on convention.

Flag: partitions 1 and 2 overlap by 5 days (Jan 10-15).
Investigate for duplicate data or re-partition.
```

## Why Intervals

Sorting by start time lets us skip pairs early. Once we find an event that starts after the current one ends, all subsequent events also start later (sorted order). This turns O(n^2) pairwise comparison into O(n log n + k) where k is the number of actual overlaps.

## Production Considerations

- **Entity grouping:** In practice, you'd group events by entity (user ID, device ID) first, then check overlaps within each group. This reduces n dramatically.
- **Streaming detection:** For real-time overlap detection, maintain a sorted buffer of recent events and check new arrivals against the buffer.
- **Tolerance:** Sometimes "overlapping by less than 5 minutes" is acceptable. Add a tolerance parameter to the overlap check.

## Connection to LeetCode

Direct application of problem 252 (Meeting Rooms) extended to report all overlapping pairs, not just "any overlap exists."

## Benchmark

At 5K events spanning a single day, the sort-based approach finds all overlaps in under a second. Brute force becomes impractical above 1K events due to O(n^2) pairwise checks.
