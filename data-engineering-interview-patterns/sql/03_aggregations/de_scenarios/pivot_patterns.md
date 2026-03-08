# Pivot Patterns

## Overview

Pivoting transforms row-based data into columnar format: distinct values in one column become separate columns in the output. Unpivoting does the reverse. These transformations are essential for reshaping data between normalized (row-per-event) and denormalized (column-per-feature) formats.

## Manual Pivot with Conditional Aggregation

The universal approach that works in every SQL engine:

```sql
SELECT
    user_id,
    SUM(CASE WHEN event_type = 'page_view' THEN event_count ELSE 0 END) AS page_views,
    SUM(CASE WHEN event_type = 'click' THEN event_count ELSE 0 END) AS clicks,
    SUM(CASE WHEN event_type = 'purchase' THEN event_count ELSE 0 END) AS purchases
FROM user_events
GROUP BY user_id;
```

Each CASE expression extracts one category's value into its own column. GROUP BY collapses the multiple rows per user into one row. The column names must be known at query time.

## DuckDB PIVOT Syntax

```sql
PIVOT user_events
ON event_type
USING SUM(event_count)
GROUP BY user_id;
```

DuckDB's PIVOT syntax is concise and automatically generates column names from the distinct values in the ON column. It is equivalent to the manual conditional aggregation approach.

## Manual Unpivot with UNION ALL

The universal approach for converting columns back to rows:

```sql
SELECT user_id, 'page_view' AS event_type, page_views AS event_count
FROM user_features
UNION ALL
SELECT user_id, 'click', clicks
FROM user_features
UNION ALL
SELECT user_id, 'purchase', purchases
FROM user_features;
```

Each SELECT extracts one column with a literal label. UNION ALL stacks the results. The table is scanned once per column being unpivoted.

## DuckDB UNPIVOT Syntax

```sql
UNPIVOT user_features
ON page_views, clicks, purchases
INTO NAME event_type VALUE event_count;
```

## When to Pivot in SQL vs Application Layer

| Criteria | Pivot in SQL | Pivot in Application |
|---|---|---|
| Known categories at query time | Yes | Either |
| Dynamic/unknown categories | Difficult (needs dynamic SQL) | Natural |
| Downstream consumer is SQL/BI tool | SQL pivot preferred | N/A |
| Downstream consumer is Python/pandas | Either | df.pivot() is easier |
| Large dataset, want to reduce transfer | SQL pivot (fewer rows) | N/A |
| Need flexible reshaping | N/A | Application layer |

**Rule of thumb:** If the pivot values are known and fixed (like months, statuses or a small set of categories), pivot in SQL. If the values are dynamic or the consumer can easily reshape, leave the data in row format.

## Dynamic Pivoting

When the column values are not known at query time, you need dynamic SQL:

```python
# Python example: build the pivot query dynamically
categories = conn.execute(
    "SELECT DISTINCT event_type FROM user_events"
).fetchall()

case_expressions = ", ".join(
    f"SUM(CASE WHEN event_type = '{cat[0]}' THEN event_count ELSE 0 END) AS {cat[0]}"
    for cat in categories
)

query = f"SELECT user_id, {case_expressions} FROM user_events GROUP BY user_id"
```

This is why pivoting often lives in the application layer or in orchestration tools (dbt macros, Airflow templates) rather than in raw SQL.

## Dialect Notes

| Feature | DuckDB | Postgres | BigQuery | Snowflake | MySQL |
|---|---|---|---|---|---|
| Manual pivot (CASE) | Yes | Yes | Yes | Yes | Yes |
| PIVOT keyword | Yes | No | Yes | Yes | No |
| UNPIVOT keyword | Yes | No | Yes | Yes | No |
| crosstab() | No | Yes (tablefunc) | No | No | No |
| Spark pivot() | N/A | N/A | N/A | N/A | N/A |

Spark SQL supports `SELECT ... FROM table PIVOT (agg FOR col IN (val1, val2, ...))`.

## At Scale

Pivoting is a wide GROUP BY. Memory is O(groups * pivot_values). For 100M users with 20 event types, the hash table has 100M entries, each with 20 counters. This is roughly 100M * 20 * 8 bytes = 16GB, which may require spilling to disk.

In distributed engines, the GROUP BY triggers a shuffle by user_id. Each node computes partial aggregates locally before shuffling, reducing network traffic.

Unpivoting with UNION ALL scans the table N times (once per column). For large tables, this can be expensive. DuckDB's UNPIVOT scans once. In Spark, `stack()` is the single-scan unpivot function.

## Production Example: ML Feature Engineering

Transform event logs into a user-feature matrix for model training:

```sql
SELECT
    user_id,
    SUM(CASE WHEN event_type = 'page_view' THEN event_count ELSE 0 END) AS feature_page_views,
    SUM(CASE WHEN event_type = 'click' THEN event_count ELSE 0 END) AS feature_clicks,
    SUM(CASE WHEN event_type = 'purchase' THEN event_count ELSE 0 END) AS feature_purchases,
    SUM(CASE WHEN event_type = 'search' THEN event_count ELSE 0 END) AS feature_searches
FROM user_events_last_30d
GROUP BY user_id;
```

The output is a flat table suitable for feeding into scikit-learn, XGBoost or a feature store. Each column is a feature, each row is an observation.
