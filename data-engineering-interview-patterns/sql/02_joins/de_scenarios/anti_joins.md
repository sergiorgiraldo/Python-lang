# Anti-Joins for Finding Gaps

## Overview

Anti-joins find rows in one table that have no corresponding row in another table. This is the most common data quality pattern in production pipelines: "what is missing?"

## The Three Syntaxes

### 1. LEFT JOIN + IS NULL

```sql
SELECT e.partition_date
FROM expected_dates e
LEFT JOIN actual_partitions a ON e.partition_date = a.partition_date
WHERE a.partition_date IS NULL;
```

The LEFT JOIN preserves all expected dates. Dates with no actual partition get NULLs in the right-side columns. The WHERE clause filters for those NULLs.

**Check the right table's primary key or a non-nullable column for NULL, not the join key.** If the join key itself can be NULL in the right table, checking it for IS NULL would conflate "no match" with "matched a NULL."

### 2. NOT EXISTS

```sql
SELECT e.partition_date
FROM expected_dates e
WHERE NOT EXISTS (
    SELECT 1 FROM actual_partitions a
    WHERE a.partition_date = e.partition_date
);
```

For each expected date, the subquery checks whether a matching actual partition exists. NOT EXISTS returns true when the subquery is empty. This is often the most readable form.

### 3. NOT IN (with NULL caveat)

```sql
SELECT partition_date
FROM expected_dates
WHERE partition_date NOT IN (
    SELECT partition_date FROM actual_partitions
    WHERE partition_date IS NOT NULL
);
```

The WHERE IS NOT NULL guard is critical. Without it, if any partition_date in actual_partitions is NULL, NOT IN returns UNKNOWN for every row, producing zero results. This is the most common NULL-related bug in production SQL.

## When to Use Each

| Syntax | Pros | Cons |
|---|---|---|
| LEFT JOIN + IS NULL | Familiar, flexible (can access right-side columns) | Slightly verbose |
| NOT EXISTS | Most readable, NULL-safe | Correlated subquery syntax |
| NOT IN | Shortest syntax | NULL trap, potentially slower |

**Recommendation:** Use LEFT JOIN + IS NULL or NOT EXISTS. Avoid NOT IN unless you can guarantee no NULLs in the subquery.

## Query Plans

Modern optimizers convert all three to the same physical anti-join operator. You can verify with EXPLAIN:

```sql
EXPLAIN SELECT ...
-- Look for "Anti Join" or "Hash Anti Join" in the plan
```

If NOT IN is not converted to an anti-join, the optimizer materializes the subquery as a list and checks membership for each row, which can be O(n * m) instead of O(n + m).

## Production Example: Pipeline Monitoring

```sql
-- Generate expected dates for the last 30 days
WITH expected AS (
    SELECT CAST(generate_series AS DATE) AS partition_date
    FROM generate_series(
        CURRENT_DATE - INTERVAL '30 days',
        CURRENT_DATE - INTERVAL '1 day',
        INTERVAL '1 day'
    )
)
SELECT e.partition_date AS missing_date,
       CURRENT_DATE - e.partition_date AS days_missing
FROM expected e
LEFT JOIN information_schema.tables t
    ON t.table_name = 'events_' || REPLACE(CAST(e.partition_date AS VARCHAR), '-', '')
WHERE t.table_name IS NULL
ORDER BY missing_date;
```

This checks whether partitioned tables exist for each of the last 30 days. Missing partitions trigger alerts.

## At Scale

Anti-joins are O(n + m) with hash-based implementations: build a hash set from the right table (actual partitions) and probe with the left table (expected dates). For gap detection, the right table is usually much larger (actual data) while the left table is small (expected schedule), making the hash set construction cheap.

In distributed engines, if the expected table is small, broadcast it to every node for a broadcast anti-join, avoiding a shuffle.

## Common Applications

- **Missing partition detection:** Expected daily/hourly partitions vs actual
- **SLA monitoring:** Expected file deliveries vs received files
- **Referential integrity:** Fact table foreign keys vs dimension table primary keys
- **Coverage gaps:** Expected test runs vs actual test results
- **Churn detection:** Active users last month vs active users this month (who left?)
