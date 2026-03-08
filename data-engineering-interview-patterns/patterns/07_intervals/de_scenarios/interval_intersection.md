# Interval Intersection (Common Time Windows)

**Run it:** `uv run python -m patterns.07_intervals.de_scenarios.interval_intersection`

## Real-World Context

"When are both the US and EU data processing windows active?" Or more practically: "Find the time ranges where both monitoring system A and system B were reporting data." Interval intersection answers these questions.

## The Problem

Given two sorted, non-overlapping schedules, find all time windows that appear in both.

## Worked Example

Finding when two systems had overlapping outages. Same algorithm as Interval Intersections (problem 986) applied to incident windows.

```
System A outages: [[02:00, 04:00], [08:00, 09:00], [14:00, 18:00]]
System B outages: [[03:00, 05:00], [07:00, 10:00], [16:00, 20:00]]

Two-pointer intersection:
  A=[02:00,04:00] vs B=[03:00,05:00]: overlap [03:00,04:00]
  A=[08:00,09:00] vs B=[07:00,10:00]: overlap [08:00,09:00]
  A=[14:00,18:00] vs B=[16:00,20:00]: overlap [16:00,18:00]

Both systems down simultaneously: 03-04, 08-09, 16-18.
Total dual-outage: 4 hours. Useful for SLA impact analysis.
```

## Why Intervals

Two-pointer intersection is O(n + m) on pre-sorted input. Brute force is O(n * m). For large schedules (thousands of time blocks), the two-pointer approach is significantly faster.

## Production Considerations

- **Multiple schedules:** For intersecting 3+ schedules, intersect pairwise or use a sweep line with a counter.
- **Timezone handling:** Convert all timestamps to UTC before intersection. Timezone-aware intersection is a common source of bugs.
- **Granularity:** For coarse granularity (daily), a simpler set intersection on dates works. Two-pointer is for fine-grained time ranges.

## Connection to LeetCode

Direct application of problem 986 (Interval List Intersections). The two-pointer approach mirrors the pattern from the Two Pointers pattern (02).

## Benchmark

For 10K blocks per schedule, intersection completes in under 50ms. The two-pointer approach scales linearly with input size.
