# Deduplication with ROW_NUMBER

## Overview

ROW_NUMBER-based deduplication is the most common window function pattern in production data engineering. Message queues, event streaming systems and API integrations frequently deliver duplicate records. The standard approach assigns a row number within each group of duplicates and keeps only row 1.

## The Pattern

```sql
SELECT *
FROM (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY <duplicate_key>
               ORDER BY <tiebreaker> DESC
           ) AS rn
    FROM raw_table
) ranked
WHERE rn = 1
```

Three decisions define a deduplication query:

1. **PARTITION BY** defines "what is a duplicate." Two rows are duplicates if they share the same partition key.
2. **ORDER BY** defines "which one to keep." Typically the most recent record (ORDER BY timestamp DESC).
3. **ROW_NUMBER** (not RANK or DENSE_RANK) ensures exactly one row per group, even if tiebreaker values are identical.

## Why ROW_NUMBER, Not RANK

ROW_NUMBER always assigns distinct numbers: 1, 2, 3. RANK and DENSE_RANK assign the same number to tied rows. For deduplication, we want exactly one winner per group. If two rows have the same timestamp, ROW_NUMBER arbitrarily picks one (deterministic within the engine but not guaranteed across runs). RANK would keep both, defeating the purpose.

If you need deterministic tiebreaking, add secondary ORDER BY columns: `ORDER BY received_at DESC, event_id DESC`.

## Production Variations

**Dedup by primary key:**
```sql
PARTITION BY entity_id
ORDER BY updated_at DESC
```

**Dedup by composite key:**
```sql
PARTITION BY user_id, event_type, DATE_TRUNC('day', event_time)
ORDER BY event_time DESC
```

**Dedup with content hash:**
```sql
PARTITION BY MD5(CONCAT(col1, col2, col3))
ORDER BY ingestion_time DESC
```

## At Scale

The sort is the bottleneck. For 1B rows with 100M distinct partition keys, the engine sorts 1B rows by the partition + order key. In distributed engines (Spark, BigQuery, Snowflake), this is a shuffle operation: data is redistributed by partition key, then sorted locally. The shuffle cost dominates for large datasets. Pre-partitioning the source table by the dedup key reduces shuffle.

Memory usage: the window function buffer holds one partition at a time. If one partition has 1M duplicates, the buffer is 1M rows. Skewed partition keys (one entity with vastly more duplicates) cause memory pressure on individual executors.

## Dialect Notes

BigQuery, Snowflake and DuckDB support QUALIFY, which eliminates the subquery:

```sql
SELECT *
FROM raw_table
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY user_id, event_type
    ORDER BY received_at DESC
) = 1
```

Postgres and MySQL require the subquery wrapper. Spark SQL supports both forms.

## When to Use This

- Ingesting from Kafka or Kinesis (at-least-once delivery guarantees duplicates)
- Merging incremental loads into a warehouse (MERGE with dedup in staging)
- Cleaning historical data after schema migration
- Consolidating records from multiple source systems
