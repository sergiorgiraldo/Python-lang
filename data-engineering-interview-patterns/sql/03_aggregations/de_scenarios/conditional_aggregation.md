# Conditional Aggregation with CASE

## Overview

Conditional aggregation embeds CASE expressions inside aggregate functions to compute multiple filtered metrics in a single table scan. Instead of writing N separate queries with N different WHERE clauses, you write one query with N conditional aggregates.

This is the SQL equivalent of "iterate once, update multiple counters."

## The Pattern

### SUM with CASE

```sql
SUM(CASE WHEN condition THEN value ELSE 0 END)
```

Returns the sum of `value` only for rows matching `condition`. Rows that do not match contribute 0 (or are skipped if you omit ELSE, since SUM ignores NULLs).

### COUNT with CASE

```sql
COUNT(CASE WHEN condition THEN 1 END)
```

Counts only rows matching `condition`. Non-matching rows produce NULL (no ELSE clause), and COUNT ignores NULLs. This is equivalent to `COUNT(*) - COUNT(CASE WHEN NOT condition THEN 1 END)`.

### FILTER Clause (DuckDB/Postgres)

```sql
SUM(amount) FILTER (WHERE status = 'completed')
COUNT(*) FILTER (WHERE category = 'electronics')
```

The FILTER clause is syntactic sugar for the CASE pattern. It is more readable and expresses intent directly. Available in DuckDB and Postgres. Not supported in BigQuery, Snowflake or MySQL.

## Why Conditional Aggregation Beats Multiple Queries

| Approach | Table Scans | Rows Read (10M table) | Shuffle (distributed) |
|---|---|---|---|
| 5 separate queries with WHERE | 5 | 50M | 5 shuffles |
| 1 query with 5 conditional aggregates | 1 | 10M | 1 shuffle |

The single-scan approach is 5x more efficient in I/O and network cost. On columnar storage, the difference is less dramatic (column pruning helps) but the shuffle savings in distributed engines are significant.

## Pivot-Like Transformation

Conditional aggregation naturally produces a pivot: rows become columns.

```sql
-- Input: one row per order with a category column
-- Output: one row per month with a column per category

SELECT
    DATE_TRUNC('month', order_date) AS month,
    SUM(CASE WHEN category = 'electronics' THEN amount ELSE 0 END) AS electronics,
    SUM(CASE WHEN category = 'clothing' THEN amount ELSE 0 END) AS clothing,
    SUM(CASE WHEN category = 'food' THEN amount ELSE 0 END) AS food
FROM orders
GROUP BY DATE_TRUNC('month', order_date);
```

This is a manual pivot. The column names must be known at query time. For dynamic pivots (unknown categories), see the pivot_patterns scenario.

## Production Example

Revenue breakdown for a dashboard that needs completed, pending and refunded amounts per day:

```sql
SELECT
    order_date,
    SUM(amount) FILTER (WHERE status = 'completed') AS revenue,
    SUM(amount) FILTER (WHERE status = 'pending') AS pending_revenue,
    SUM(amount) FILTER (WHERE status = 'refunded') AS refunds,
    COUNT(*) FILTER (WHERE status = 'completed') AS completed_orders,
    COUNT(*) AS total_orders
FROM orders
GROUP BY order_date
ORDER BY order_date;
```

One scan, six metrics. Without conditional aggregation, this would be three separate queries or a complex subquery join.

## Dialect Notes

| Feature | DuckDB | Postgres | BigQuery | Snowflake | MySQL |
|---|---|---|---|---|---|
| SUM(CASE WHEN ...) | Yes | Yes | Yes | Yes | Yes |
| COUNT(CASE WHEN ...) | Yes | Yes | Yes | Yes | Yes |
| FILTER (WHERE ...) | Yes | Yes | No | No | No |
| PIVOT keyword | Yes | No (use crosstab) | Yes | Yes | No |

**Recommendation:** Use SUM(CASE WHEN ...) for maximum portability. Use FILTER (WHERE ...) in DuckDB/Postgres for readability.

## Common Mistakes

- **Forgetting ELSE 0 in SUM:** Without ELSE, non-matching rows produce NULL. SUM ignores NULLs so the result is still correct, but it is better to be explicit. For COUNT, omitting ELSE is intentional (COUNT ignores NULLs).
- **Using ELSE 0 in COUNT:** `COUNT(CASE WHEN x THEN 1 ELSE 0 END)` counts all rows because 0 is not NULL. Omit the ELSE or use SUM instead.
- **Mixing up WHERE and conditional aggregate:** WHERE filters rows before aggregation (removing them entirely). Conditional aggregates include the row in the GROUP BY but only count it for specific metrics.
