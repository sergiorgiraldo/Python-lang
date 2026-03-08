# MERGE / Upsert Patterns

## Overview

MERGE combines insert, update and delete into a single atomic statement. It is the standard pattern for maintaining dimension tables, applying incremental updates and handling slowly changing dimensions. Different engines implement it with different syntax, but the concept is universal.

## Conceptual MERGE

```sql
-- Standard SQL MERGE (supported by BigQuery, Snowflake, Spark)
MERGE INTO dim_customer t
USING staging_customer s ON t.customer_id = s.customer_id

WHEN MATCHED AND s.updated_at > t.updated_at THEN
    UPDATE SET
        name = s.name,
        email = s.email,
        updated_at = s.updated_at

WHEN NOT MATCHED THEN
    INSERT (customer_id, name, email, updated_at)
    VALUES (s.customer_id, s.name, s.email, s.updated_at)

WHEN NOT MATCHED BY SOURCE THEN
    UPDATE SET status = 'deleted';
```

Three clauses handle the three cases:
- **MATCHED:** Record exists in both source and target. Update if changed.
- **NOT MATCHED:** Record in source but not target. Insert.
- **NOT MATCHED BY SOURCE:** Record in target but not source. Soft-delete.

## DuckDB: INSERT ... ON CONFLICT

DuckDB does not support the full MERGE syntax but provides INSERT ON CONFLICT (similar to PostgreSQL's upsert):

```sql
INSERT INTO dim_customer (customer_id, name, email, updated_at)
SELECT customer_id, name, email, updated_at
FROM staging_customer
ON CONFLICT (customer_id) DO UPDATE SET
    name = EXCLUDED.name,
    email = EXCLUDED.email,
    updated_at = EXCLUDED.updated_at;
```

**EXCLUDED** refers to the row that would have been inserted. When a conflict occurs (matching customer_id), the UPDATE clause runs instead.

**Limitation:** INSERT ON CONFLICT does not handle the "delete removed records" case. You need a separate DELETE statement for that.

## Dialect Comparison

| Engine | Syntax | Delete Support |
|---|---|---|
| BigQuery | MERGE INTO ... USING ... | Yes (WHEN NOT MATCHED BY SOURCE) |
| Snowflake | MERGE INTO ... USING ... | Yes |
| Spark (Delta Lake) | MERGE INTO ... USING ... | Yes |
| PostgreSQL | INSERT ... ON CONFLICT | No (separate DELETE) |
| DuckDB | INSERT ... ON CONFLICT | No (separate DELETE) |
| MySQL | INSERT ... ON DUPLICATE KEY | No (separate DELETE) |

## SCD Type 1 vs Type 2

**Type 1 (overwrite):** Update in place. History is lost. This is what the examples above show.

```sql
-- Type 1: just update
WHEN MATCHED THEN UPDATE SET name = s.name, email = s.email
```

**Type 2 (versioned):** Close the old record and insert a new one. Preserves history.

```sql
-- Type 2: close old, insert new
WHEN MATCHED AND s.updated_at > t.updated_at THEN
    UPDATE SET end_date = CURRENT_DATE, is_current = FALSE

-- Then insert the new version separately
INSERT INTO dim_customer (customer_id, name, email, start_date, end_date, is_current)
SELECT s.customer_id, s.name, s.email, CURRENT_DATE, '9999-12-31', TRUE
FROM staging_customer s
JOIN dim_customer t ON s.customer_id = t.customer_id
WHERE t.is_current = FALSE AND s.updated_at > t.updated_at;
```

SCD Type 2 is more complex because MERGE cannot insert and update the same matched row. Production implementations typically use a multi-step process.

## Dedup Before MERGE

Staging tables often contain duplicates (from at-least-once delivery). MERGE will fail or produce nondeterministic results if multiple staging rows match the same target row.

```sql
-- Dedup staging before MERGE
WITH deduped AS (
    SELECT *, ROW_NUMBER() OVER (
        PARTITION BY customer_id ORDER BY updated_at DESC
    ) AS rn
    FROM staging_customer
)
MERGE INTO dim_customer t
USING (SELECT * FROM deduped WHERE rn = 1) s
ON t.customer_id = s.customer_id
...
```

## At Scale

MERGE performance depends on:
- **Join between staging and target:** Hash join on the merge key. O(n + m).
- **Update/insert operations:** Each matched row is an update (write amplification), each unmatched row is an insert.
- **Concurrency:** MERGE locks the target table or partition during execution. For high-frequency updates, micro-batching reduces lock contention.

Optimization strategies:
- **Partition MERGE:** Only merge into affected partitions, not the entire table
- **Clustered merge keys:** If the target is clustered by the merge key, matched rows are co-located on disk
- **Pre-filter staging:** Remove unchanged rows from staging before MERGE to reduce write operations

## Common Applications

- **Dimension table maintenance:** Keep dimensions in sync with source systems
- **Slowly changing dimensions:** SCD Type 1 (overwrite) and Type 2 (versioned)
- **Idempotent pipeline writes:** MERGE makes pipeline reruns safe (same result regardless of how many times you run)
- **Real-time table updates:** Micro-batch MERGE from streaming staging tables
