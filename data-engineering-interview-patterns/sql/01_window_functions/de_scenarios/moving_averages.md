# Moving Averages

## Overview

Moving averages smooth noisy time series by averaging over a sliding window. A 7-day moving average replaces each data point with the average of itself and the preceding 6 days. They are fundamental in trend detection, anomaly detection baselines and metric dashboards.

## The Pattern

```sql
AVG(value) OVER (
    ORDER BY date_column
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
) AS moving_avg_7day
```

The number in `N PRECEDING` is N-1 for an N-day window (6 preceding + current row = 7 rows).

## ROWS vs RANGE

This is one of the most important distinctions in window function frames:

**ROWS BETWEEN 6 PRECEDING AND CURRENT ROW:**
- Counts physical rows, regardless of their values
- If dates have gaps (missing days), ROWS still looks back 6 rows
- The 6 preceding rows might span more than 6 days
- Deterministic: always includes exactly min(7, rows_available) rows

**RANGE BETWEEN INTERVAL '6 days' PRECEDING AND CURRENT ROW:**
- Counts by logical value (date distance)
- Only includes rows within 6 calendar days of the current row
- If 3 days are missing, only 4 rows are included
- Semantically correct for "7-day average" with gaps

When to use which:
- **ROWS** when data is dense (no gaps) or you want a fixed-width window regardless of gaps
- **RANGE** when data has gaps and you want the average to reflect the true time window

## Warming Up Period

The first N-1 rows of a moving average have fewer than N data points. The average is computed over whatever rows are available, which biases the early values. In production, either:
- Exclude the warm-up period: `WHERE row_number >= N`
- Label it: add a column indicating whether the full window is available
- Accept it: many dashboards simply show the biased early values

## At Scale

Moving averages are a single sorted pass with a sliding window buffer of N rows: O(n log n) for the sort, O(n) for the scan, O(N) memory for the buffer. For N=7 and 1B rows, the buffer is trivial.

RANGE-based frames are slightly more expensive because the engine must evaluate the range predicate for each row rather than simply shifting a fixed-size buffer. For most practical window sizes, the difference is negligible.

## Production Context

**Metric dashboards:** 7-day and 30-day moving averages smooth daily noise in revenue, DAU and conversion rates. Stakeholders see trends rather than day-to-day volatility.

**Anomaly detection:** Compare the current value to the moving average. A value more than 2-3 standard deviations from the moving average triggers an alert. The moving average serves as the "expected" baseline.

**Trend detection:** When the 7-day moving average crosses above the 30-day moving average, it signals an uptrend. This "crossover" technique comes from financial technical analysis but applies to any time series.

**Capacity planning:** Moving averages of resource usage (CPU, memory, storage) reveal trends for capacity forecasting. Daily spikes average out, revealing the underlying growth rate.
