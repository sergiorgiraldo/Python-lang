# DE Scenario: Anomaly Detection with Rolling Bounds

**Run it:** `uv run python -m patterns.04_sliding_window.de_scenarios.anomaly_detection`

## Real-World Context

Data quality monitoring often needs to detect values that fall outside "normal" bounds. But what's normal changes over time - seasonal patterns, growth trends and regime changes mean that a fixed threshold breaks quickly.

Rolling bounds adapt: compute the mean and standard deviation over a recent window, flag anything outside mean +/- N standard deviations. This is a fixed-size sliding window that tracks enough statistics to compute bounds at each position.

## The Problem

Given a time series of metric values, detect anomalies: points where the value falls outside the rolling mean +/- (threshold * rolling standard deviation).

## Why Sliding Window

The rolling statistics (mean, std) are fixed-size window computations. Each step adds a new value and removes an old one. With the right running statistics, each update is O(1).

This combines the fixed-window technique from [643. Maximum Average Subarray](../../problems/643_max_average_subarray.md) with the deque-based max tracking from [239. Sliding Window Maximum](../../problems/239_sliding_window_max.md) (for tracking rolling min/max as an alternative to std-based bounds).

## Production Considerations

**Welford's algorithm:** For numerically stable rolling variance, use Welford's online algorithm rather than the naive "sum of squares minus square of sum" formula. The naive version suffers from catastrophic cancellation with large values.

**Cold start:** The first few data points don't have enough history for meaningful bounds. Skip anomaly detection until the window is full.

**Anomaly vs change point:** An anomaly is a temporary deviation. A change point is a permanent shift. Rolling bounds detect anomalies well but will eventually adapt to a new regime. If you need change point detection, look at CUSUM or binary search on metrics (see [Metric Change Detection](../../03_binary_search/de_scenarios/metric_change_detection.md)).

**Multi-metric correlation:** A single metric anomaly might not be interesting. Correlating anomalies across related metrics (latency + error rate + throughput) gives stronger signals.

## Worked Example

Detect values that deviate significantly from a sliding window of recent observations. The window maintains a running sum and count (or mean and standard deviation) and flags values that fall outside a threshold.

```
Server CPU usage (%), sampled every minute:
  [45, 48, 42, 50, 47, 44, 93, 46, 43, 88, 91, 47]

Window size k=5, alert threshold: value > window_mean + 2 × window_std

  Window [45, 48, 42, 50, 47]: mean=46.4, std=2.87
    New value: 44. 44 <= 46.4 + 5.74 = 52.14. Normal.

  Window [48, 42, 50, 47, 44]: mean=46.2, std=2.93
    New value: 93. 93 > 46.2 + 5.86 = 52.06. ANOMALY.

  Window [42, 50, 47, 44, 93]: mean=55.2, std=19.0
    New value: 46. Normal (93 inflated the window stats).

  Window [50, 47, 44, 93, 46]: mean=56.0, std=18.5
    New value: 43. Normal.

  Window [47, 44, 93, 46, 43]: mean=54.6, std=18.9
    New value: 88. 88 > 54.6 + 37.8 = 92.4. Normal (barely).

  Window [44, 93, 46, 43, 88]: mean=62.8, std=22.1
    New value: 91. 91 > 62.8 + 44.2 = 107.0. Normal.

The anomaly detector caught the 93 spike but not the later 88 and 91
because the window had already shifted to include the earlier spike,
raising the baseline. This is a known limitation of simple moving-window
approaches - they adapt to sustained anomalies.
```

## Connection to LeetCode

Fixed-window statistics from [643](../../problems/643_max_average_subarray.md) extended with variance tracking. The deque-based approach from [239](../../problems/239_sliding_window_max.md) is an alternative using rolling min/max instead of standard deviation.

## Benchmark

See the `.py` file for anomaly detection at scale.
