# DE Scenario: Moving Averages on Time-Series Data

**Run it:** `uv run python -m patterns.04_sliding_window.de_scenarios.moving_averages`

## Real-World Context

Dashboard metrics, SLA reports and trend analysis all rely on smoothing noisy data with rolling averages. A 7-day moving average of daily active users, a 5-minute rolling average of API latency, a 30-day revenue trend - these are fixed-size sliding windows computing an aggregate over each position.

The naive approach recomputes the sum for every window from scratch. The sliding window approach maintains a running sum, adding the new value and subtracting the one that fell off.

## The Problem

Given a time-ordered sequence of metric values and a window size k, compute the moving average at each position.

## Why Sliding Window

This is [LeetCode #643 (Maximum Average Subarray)](../../problems/643_max_average_subarray.md) applied to a practical context. Instead of finding the maximum average, we compute all of them.

Each window overlaps with the previous one by k-1 elements. Recomputing the full sum wastes O(k) work per position. The sliding approach does O(1) work per position.

## Production Considerations

**Gaps in time series:** Real data has missing timestamps (weekends, outages, gaps). A naive positional window treats whatever is adjacent as "within the window." For time-aware windows, you need to check actual timestamps, not just array positions. SQL handles this with range-based frames: `AVG(value) OVER (ORDER BY ts RANGE BETWEEN INTERVAL '7 days' PRECEDING AND CURRENT ROW)`.

**Warm-up period:** The first k-1 positions don't have a full window. Some systems emit NULL, others emit a partial average. Decide upfront and document it.

**Streaming vs batch:** In batch (pandas, SQL), rolling windows are built-in. In streaming (Flink, Spark Streaming), the sliding window state is maintained incrementally - same algorithm as what we're implementing here, just with checkpointing and fault tolerance on top.

**Weighted averages:** Exponential moving averages (EMA) don't use a fixed window. They weight recent values more heavily. Same conceptual idea but different implementation - no need for a deque or explicit window tracking.

## Worked Example

Moving averages smooth noisy data by averaging the last k observations. This is the fixed-size sliding window applied to time-series monitoring. Instead of re-summing k values at each step, the window adds the new value and subtracts the one that fell off.

```
Metric: API response times (ms), arriving every second:
  [120, 85, 340, 95, 210, 150, 88, 445, 110, 75]

Moving average with window k=4:

  Window [120, 85, 340, 95]:   sum=640,  avg=160.0 ms
  Window [85, 340, 95, 210]:   sum=730,  avg=182.5 ms  (added 210, removed 120)
  Window [340, 95, 210, 150]:  sum=795,  avg=198.75 ms
  Window [95, 210, 150, 88]:   sum=543,  avg=135.75 ms
  Window [210, 150, 88, 445]:  sum=893,  avg=223.25 ms ← spike
  Window [150, 88, 445, 110]:  sum=793,  avg=198.25 ms
  Window [88, 445, 110, 75]:   sum=718,  avg=179.5 ms

The raw data has a spike at 445ms. The moving average shows it as a
gradual rise and fall (223 → 198 → 179) rather than a sharp spike,
which is better for alerting (fewer false positives).

SQL equivalent:
  AVG(response_ms) OVER (ORDER BY ts ROWS BETWEEN 3 PRECEDING AND CURRENT ROW)
```

## Connection to LeetCode

Direct application of [643. Maximum Average Subarray I](../../problems/643_max_average_subarray.md). Same O(1) update per step, same running sum technique.

## Benchmark

See the `.py` file for timing comparisons at scale.
