# Running Percentiles (Streaming Median)

**Run it:** `uv run python -m patterns.05_heap_priority_queue.de_scenarios.running_percentiles`

## Real-World Context

Your monitoring dashboard shows P50 API latency updating every second. Behind the scenes, hundreds of latency measurements arrive each second. You need the median to update in real time without re-sorting the entire history.

Streaming percentiles show up in SLA monitoring (is our P99 under 200ms?), data quality checks (has the median order value shifted significantly?) and real-time analytics dashboards.

## The Problem

As numbers arrive one at a time from a data stream, maintain the ability to query the current median at any point. Each update should be fast (not proportional to the total number of values seen).

## Worked Example

Tracking the median (or any percentile) of a data stream in real-time using two heaps. Same as Find Median from Data Stream (problem 295) applied to monitoring.

```
Monitoring API response times (ms), tracking live median:

  t=1: latency=45   max_heap=[45], min_heap=[]         median=45
  t=2: latency=120  max_heap=[45], min_heap=[120]       median=(45+120)/2=82.5
  t=3: latency=67   max_heap=[67,45], min_heap=[120]    median=67
  t=4: latency=200  max_heap=[67,45], min_heap=[120,200] median=(67+120)/2=93.5
  t=5: latency=55   max_heap=[67,55,45], min_heap=[120,200] median=67

  Dashboard shows: "Current median response time: 67ms"

  Each update: O(log n). Query median: O(1).
  For a sliding window variant (last N requests), combine with
  a mechanism to expire old values from the heaps.
```

## Why Heaps

| Approach | Add Time | Median Time | Space |
|----------|----------|-------------|-------|
| Sort on every add | O(n log n) | O(1) | O(n) |
| bisect.insort | O(n) | O(1) | O(n) |
| Two heaps | O(log n) | O(1) | O(n) |

After 1M data points, the sort approach does O(1M × 20) = 20M operations per add. Two heaps do O(20) per add. That's a 1,000,000x difference in per-add cost.

## Production Considerations

- **Memory:** Two heaps store all values (O(n) space). For unbounded streams, this grows forever. Production systems often use windowed medians (sliding window of the last N values) or approximate structures (T-Digest, KLL sketch) that bound memory.
- **T-Digest:** The production standard for streaming percentiles. Provides approximate P50/P95/P99 with O(compression) memory regardless of stream size. Used by Elasticsearch, Datadog and most monitoring systems.
- **Windowed percentiles:** Combine sliding window (pattern 04) with two heaps. Requires "lazy deletion" to handle elements leaving the window. Significantly more complex than the basic two-heap approach.
- **Multiple percentiles:** Two heaps efficiently track one split point (the median). For P50 + P95 + P99 simultaneously, you'd need multiple heap pairs or a more general structure like a balanced BST.

## Connection to LeetCode

Direct application of problem 295 (Find Median from Data Stream). The two-heap approach is the standard solution.

## Benchmark

Running the script processes 50K simulated latency values. The two-heap approach is typically 100-300x faster than the naive sort-on-every-add approach at this scale. The gap grows quadratically because the naive approach's per-add cost increases with n while the heap's per-add cost grows logarithmically.
