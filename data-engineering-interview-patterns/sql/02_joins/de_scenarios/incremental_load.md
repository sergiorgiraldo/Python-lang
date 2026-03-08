# Incremental Load Detection

## Overview

Incremental loading updates a target table with only the changes from a source system, rather than reloading everything. The three operations (insert new, update changed, delete removed) are detected using joins between source and target.

## The Three Detections

### New Records

```sql
SELECT s.*
FROM source_customers s
LEFT JOIN target_customers t ON s.customer_id = t.customer_id
WHERE t.customer_id IS NULL;
```

Records in the source that have no match in the target are new. This is the anti-join pattern.

### Changed Records

```sql
SELECT s.*
FROM source_customers s
INNER JOIN target_customers t ON s.customer_id = t.customer_id
WHERE s.updated_at > t.updated_at;
```

Records in both tables where the source has a newer timestamp. The INNER JOIN restricts to records that exist in both places. The WHERE clause identifies those that have changed.

**Alternative change detection:** Compare a hash of all columns instead of relying on timestamps:

```sql
WHERE MD5(CONCAT(s.name, s.email)) != MD5(CONCAT(t.name, t.email))
```

Hash comparison catches changes even when timestamps are unreliable.

### Deleted Records

```sql
SELECT t.*
FROM target_customers t
LEFT JOIN source_customers s ON t.customer_id = s.customer_id
WHERE s.customer_id IS NULL;
```

Records in the target with no match in the source have been deleted upstream. This is the reverse anti-join. Note: many pipelines skip delete detection and use soft deletes (flagging records) instead.

## Full Incremental Load Pattern

```sql
-- Step 1: Insert new records
INSERT INTO target_customers
SELECT s.*
FROM source_customers s
LEFT JOIN target_customers t ON s.customer_id = t.customer_id
WHERE t.customer_id IS NULL;

-- Step 2: Update changed records
UPDATE target_customers t
SET name = s.name,
    email = s.email,
    updated_at = s.updated_at
FROM source_customers s
WHERE t.customer_id = s.customer_id
  AND s.updated_at > t.updated_at;

-- Step 3: (Optional) Delete removed records
DELETE FROM target_customers t
WHERE NOT EXISTS (
    SELECT 1 FROM source_customers s
    WHERE s.customer_id = t.customer_id
);
```

## Connection to MERGE

The three-step insert/update/delete pattern above is exactly what MERGE (or upsert) encapsulates in a single statement. See the merge_upsert scenario for that approach.

## At Scale

For large tables, full-table joins between source and target are expensive. Production optimizations:

- **Timestamp-based filtering:** Only pull source records with updated_at > last_load_timestamp, reducing the source side to recently changed records
- **Partition-level comparison:** Compare row counts and checksums per partition before doing row-level joins
- **CDC from database logs:** Use Debezium, DMS or native CDC to capture changes from the transaction log, avoiding source-target comparison entirely
- **Watermark tracking:** Store the high-water mark (max updated_at processed) and only process records above it

## Timestamp vs Hash Detection

| Method | Pros | Cons |
|---|---|---|
| Timestamp (updated_at) | Fast comparison, indexable | Requires reliable timestamps |
| Column hash (MD5/SHA) | Catches all changes | Expensive to compute, not indexable |
| Row version number | Simple increment check | Requires source system support |

## Common Applications

- **Warehouse daily loads:** Detect what changed in the source OLTP since yesterday
- **Data lake incremental updates:** New files detected by anti-join on file paths
- **API sync:** Compare local cache with API responses to find new/changed records
- **Configuration drift detection:** Compare current infrastructure state with desired state
