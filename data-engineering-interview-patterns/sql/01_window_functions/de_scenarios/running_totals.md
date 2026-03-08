# Running Totals

## Overview

Running totals (cumulative sums) compute the aggregate of all rows from the start of the sequence up to the current row. They appear in financial reporting (year-to-date revenue), inventory tracking (running balance) and cumulative KPIs (total signups to date).

## The Pattern

```sql
SUM(value) OVER (
    ORDER BY date_column
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
)
```

The frame clause `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` includes every row from the first row in the partition through the current row. This is the default frame for aggregate window functions with an ORDER BY, but specifying it explicitly makes the intent clear.

## Running Total vs Running Average

Running total grows monotonically (for positive values). Running average converges toward the overall mean as more rows are included. Both use the same frame clause with different aggregate functions.

```sql
SELECT
    date,
    revenue,
    SUM(revenue) OVER (ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative,
    AVG(revenue) OVER (ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_avg
FROM daily_revenue
```

## Frame Clause Details

The default frame depends on the context:
- With ORDER BY: `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`
- Without ORDER BY: entire partition

For running totals, ROWS and RANGE produce the same result when there are no duplicate ORDER BY values. When duplicates exist, RANGE includes all tied rows in the current frame (potentially jumping ahead), while ROWS strictly counts physical rows. For running totals, ROWS is usually the safer choice because it is deterministic row-by-row.

## At Scale

Running totals are a single sorted pass: O(n log n) for the sort, O(n) for the accumulation. No additional memory beyond a single running sum variable. This is one of the most efficient window function patterns.

For partitioned running totals (cumulative revenue per region), the sort is per partition. With 100 regions and 1M rows each, the engine sorts 100 partitions of 1M rows rather than one partition of 100M.

## Production Context

**Financial reporting:** Year-to-date revenue, quarterly cumulative targets, running profit/loss. These queries run daily in BI tools and dashboards.

**Inventory:** Running balance = starting inventory + cumulative receipts - cumulative shipments. Window functions avoid self-joins or recursive CTEs for balance calculation.

**Cumulative KPIs:** Total users to date, cumulative orders, lifetime value running totals. Product teams track these to measure growth trajectories.

**Data quality:** Cumulative row counts per day to detect ingestion anomalies (sudden jumps or plateaus in the running total).
