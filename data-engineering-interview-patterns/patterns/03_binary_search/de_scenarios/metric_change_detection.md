# DE Scenario: Metric Change Detection (Bisecting for Root Cause)

**Run it:** `uv run python -m patterns.03_binary_search.de_scenarios.metric_change_detection`

## Real-World Context

A data quality metric was fine last week but is failing today. Somewhere in between, something changed - a schema update, a bad deploy, a data source change. You need to find when it broke.

Checking every day between "last known good" and "first known bad" is linear. If you've got months of daily snapshots, binary search finds the change point in about 7-8 checks instead of 30+.

This is the same concept as `git bisect` - and it's a left-boundary binary search.

## The Problem

Given a time-ordered sequence of metric values and a threshold, find the first point where the metric crossed the threshold.

## Why Binary Search

The metric was below threshold, then above (or vice versa). That's a monotonic property: there's a single transition point. Binary search finds it in O(log n).

This maps directly to [LeetCode #35 (Search Insert Position)](../../problems/035_search_insert.md) - finding the first element that satisfies a condition.

## Production Considerations

**The check might be expensive.** In `git bisect`, each check means building and testing the code. In data pipelines, each check might mean running a query against a daily snapshot. Binary search minimizes the number of checks, which matters when each one takes minutes.

**Multiple change points.** If the metric bounced above and below the threshold multiple times, binary search finds one transition - not necessarily the one you want. For multiple transitions, you need a different approach (or domain knowledge about which time range to search).

**Noisy metrics.** If the metric fluctuates naturally, a single threshold crossing might not indicate a real change. Consider using a buffer zone or a sustained-violation check (metric above threshold for N consecutive days).

## Worked Example

Finding when a metric changed significantly in sorted time-series data. Binary search on the time axis to find the change point: the first timestamp where the metric crosses a threshold.

```
Daily revenue data, sorted by date (365 days):
  [Jan 1: $45K, Jan 2: $47K, ..., Jun 15: $52K, ..., Jun 16: $31K, ..., Dec 31: $33K]

  Revenue was ~$45-55K for the first half, then dropped to ~$28-35K.
  Find the first day where revenue dropped below $40K.

  Binary search for the change point:
    left=0 (Jan 1), right=364 (Dec 31)

    mid=182 (Jul 1): revenue = $32K < $40K → change happened before this. right=182.
    mid=91 (Apr 1): revenue = $48K >= $40K → change is after this. left=92.
    mid=137 (May 17): revenue = $51K >= $40K → left=138.
    mid=160 (Jun 9): revenue = $50K >= $40K → left=161.
    mid=171 (Jun 20): revenue = $29K < $40K → right=171.
    mid=166 (Jun 15): revenue = $52K >= $40K → left=167.
    mid=168 (Jun 17): revenue = $33K < $40K → right=168.
    mid=167 (Jun 16): revenue = $31K < $40K → right=167.
    left=167 == right=167 → change point is Jun 16.

  9 steps to find the change point in a year of daily data.
  Linear scan would check up to 167 days from the start.
```

## Connection to LeetCode

This is [162. Find Peak Element](../../problems/162_find_peak.md) meets [35. Search Insert Position](../../problems/035_search_insert.md). You're binary searching for a transition point using a local property (metric above/below threshold) to determine which half to search.

## Benchmark

See the `.py` file for timing comparison on large metric histories.
