# Materialized Views vs Scheduled Queries

Materialized views are pre-computed query results stored as a table. They
trade storage space and freshness for fast read performance.

## Core Concept

```
Raw data (expensive to query) → Materialized summary (cheap to query)
```

Instead of running a complex aggregation every time a dashboard loads,
compute the aggregation once and store the result. The dashboard reads
the pre-computed table.

## Refresh Strategies

### Full Refresh

Drop and recreate the materialized table from scratch.

```sql
CREATE OR REPLACE TABLE daily_summary AS
SELECT date, metric, SUM(value) AS total
FROM raw_events
GROUP BY date, metric;
```

**Pros**: simple, always correct, no state management
**Cons**: expensive for large tables, reprocesses everything

**Use when**: source table is small-to-medium, transformation is complex,
or incremental logic would be error-prone.

### Incremental Refresh

Only process new or changed data since the last refresh.

```sql
-- Delete existing data for the refresh window
DELETE FROM daily_summary WHERE date = CURRENT_DATE - 1;

-- Insert only the new data
INSERT INTO daily_summary
SELECT date, metric, SUM(value) AS total
FROM raw_events
WHERE date = CURRENT_DATE - 1
GROUP BY date, metric;
```

**Pros**: fast, processes minimal data, low cost
**Cons**: complex to implement correctly, requires tracking the "watermark"
(what has been processed), late-arriving data can cause gaps

**Use when**: source table is large, new data arrives in append-only fashion
with a reliable timestamp or partition key.

### Merge Refresh

Upsert pattern: insert new rows, update existing ones.

```sql
MERGE INTO daily_summary t
USING (
    SELECT date, metric, SUM(value) AS total
    FROM raw_events
    WHERE date >= CURRENT_DATE - 3  -- reprocess last 3 days for late arrivals
    GROUP BY date, metric
) s ON t.date = s.date AND t.metric = s.metric
WHEN MATCHED THEN UPDATE SET total = s.total
WHEN NOT MATCHED THEN INSERT VALUES (s.date, s.metric, s.total);
```

**Pros**: handles late-arriving data, idempotent
**Cons**: more complex, reprocesses a lookback window

## When to Materialize

**Materialize when:**
- The aggregation is expensive (full scan of a large table)
- The result is queried frequently (dashboards, reports, APIs)
- Freshness requirements allow staleness (minutes to hours is acceptable)
- The query has an SLA (dashboard must load in < 2 seconds)

**Do not materialize when:**
- The source data changes rapidly and queries need real-time freshness
- The aggregation is cheap (small table, already indexed)
- The result is queried rarely (ad-hoc analysis)
- Storage cost exceeds the compute savings

## Dialect Specifics

### BigQuery

```sql
CREATE MATERIALIZED VIEW daily_summary AS
SELECT date, metric, SUM(value) AS total
FROM raw_events
GROUP BY date, metric;
```

- Auto-refresh: BigQuery refreshes materialized views automatically when base
  tables change (within a few minutes)
- Query rewriting: the optimizer may use a materialized view even when the
  query targets the base table
- Limitations: only supports aggregation queries, no JOINs in some cases

### Snowflake

```sql
CREATE MATERIALIZED VIEW daily_summary AS
SELECT date, metric, SUM(value) AS total
FROM raw_events
GROUP BY date, metric;
```

- Auto-refresh with background maintenance service
- Charged for the compute used to refresh
- Supports clustering on the materialized view

### Postgres

```sql
CREATE MATERIALIZED VIEW daily_summary AS
SELECT date, metric, SUM(value) AS total
FROM raw_events
GROUP BY date, metric;

-- Manual refresh (no auto-refresh)
REFRESH MATERIALIZED VIEW daily_summary;
REFRESH MATERIALIZED VIEW CONCURRENTLY daily_summary;  -- no read lock
```

- No auto-refresh: must be triggered manually or via cron/scheduler
- CONCURRENTLY refresh requires a unique index
- Indexes can be created on the materialized view

### dbt (Framework)

dbt models are effectively scheduled materializations:

```yaml
# dbt model config
models:
  - name: daily_summary
    config:
      materialized: table          # full refresh each run
      # materialized: incremental  # append-only or merge
```

- `materialized: table` = full refresh
- `materialized: incremental` = process only new rows (with configurable strategy)
- `materialized: view` = not materialized, always computed fresh

## Cost Considerations

Materializing saves query cost but adds storage and refresh cost:

| Factor | On-the-fly | Materialized |
|---|---|---|
| Query cost | High (scan raw data each time) | Low (scan summary table) |
| Storage cost | None extra | Extra table storage |
| Refresh cost | None | Periodic compute cost |
| Freshness | Real-time | Stale by refresh interval |

**Break-even calculation**: if a dashboard query costs $1 per run and runs 100
times/day, that is $100/day. A materialized view that costs $2 to refresh daily
saves $98/day.

## Staleness vs Cost Tradeoff

| Refresh Interval | Staleness | Refresh Cost | Use Case |
|---|---|---|---|
| Every 5 minutes | Near real-time | High | Operational dashboards |
| Hourly | Up to 1 hour | Moderate | Business metrics |
| Daily | Up to 24 hours | Low | Executive reports |
| Weekly | Up to 7 days | Minimal | Historical analysis |

Choose the longest refresh interval that meets your freshness requirements.
More frequent refreshes cost more and provide diminishing returns for most
use cases.
