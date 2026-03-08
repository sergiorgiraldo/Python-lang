# Gap Detection

## Overview

Gap detection finds missing values in a sequence by comparing expected values against actual values. The core pattern is: generate the expected set, LEFT JOIN to the actual set, filter for NULLs. This is the anti-join pattern applied to generated sequences.

## The Pattern

```sql
-- 1. Generate expected values
-- 2. LEFT JOIN actual values
-- 3. Filter for NULLs (missing)

SELECT expected.value AS missing
FROM expected_set expected
LEFT JOIN actual_set actual ON expected.value = actual.value
WHERE actual.value IS NULL;
```

The expected set can come from generate_series (dates, integers), a reference table (regions, products) or a CROSS JOIN of dimensions.

## Finding Missing Dates

The most common gap detection in data engineering: are all daily partitions present?

```sql
SELECT expected.d AS missing_date
FROM generate_series(
    DATE '2024-01-01',
    DATE '2024-01-07',
    INTERVAL '1 day'
) AS expected(d)
LEFT JOIN daily_partitions dp ON expected.d = dp.partition_date
WHERE dp.partition_date IS NULL
ORDER BY missing_date;
```

generate_series produces one row per day. The LEFT JOIN matches each expected date against actual partitions. NULLs indicate missing dates.

## Finding Gaps in Sequential IDs

```sql
SELECT gs.id AS missing_id
FROM generate_series(1, (SELECT MAX(id) FROM events)) AS gs(id)
LEFT JOIN events e ON gs.id = e.id
WHERE e.id IS NULL
ORDER BY missing_id;
```

Useful for detecting deleted records or gaps in auto-increment sequences.

## Finding Missing Combinations (CROSS JOIN)

When the expected set is the Cartesian product of two dimensions:

```sql
SELECT r.region_name, p.product_name
FROM regions r
CROSS JOIN products p
LEFT JOIN sales s
    ON r.region_name = s.region_name
    AND p.product_name = s.product_name
WHERE s.amount IS NULL;
```

This finds region-product combinations with no sales data. The CROSS JOIN generates all possible combinations, and the LEFT JOIN identifies which ones are missing.

## DuckDB generate_series

DuckDB supports generate_series for both integers and dates:

```sql
-- Integer sequence
SELECT * FROM generate_series(1, 10);           -- 1 through 10
SELECT * FROM generate_series(1, 10, 2);        -- 1, 3, 5, 7, 9

-- Date sequence
SELECT * FROM generate_series(
    DATE '2024-01-01',
    DATE '2024-12-31',
    INTERVAL '1 day'
);

-- Timestamp sequence
SELECT * FROM generate_series(
    TIMESTAMP '2024-01-01 00:00:00',
    TIMESTAMP '2024-01-02 00:00:00',
    INTERVAL '1 hour'
);
```

## Dialect Notes

| Feature | DuckDB | Postgres | BigQuery | Snowflake |
|---|---|---|---|---|
| generate_series (integer) | Yes | Yes | No | No |
| generate_series (date) | Yes | Yes | No | No |
| Date array generation | N/A | N/A | GENERATE_DATE_ARRAY + UNNEST | GENERATOR + ROW_NUMBER |
| Range function | range() also available | N/A | N/A | N/A |

**BigQuery:**
```sql
SELECT d AS missing_date
FROM UNNEST(GENERATE_DATE_ARRAY('2024-01-01', '2024-01-07')) AS d
LEFT JOIN daily_partitions dp ON d = dp.partition_date
WHERE dp.partition_date IS NULL;
```

**Snowflake:**
```sql
SELECT DATEADD('day', seq4(), '2024-01-01')::DATE AS missing_date
FROM TABLE(GENERATOR(ROWCOUNT => 7))
-- Then LEFT JOIN...
```

## At Scale

Generating expected values is cheap. Date ranges are small (365 days/year, 8760 hours/year). Integer ranges can be large but are still sequential and memory-efficient.

The LEFT JOIN uses a hash-based anti-join. Build a hash set from the actual values (the potentially large table), probe with the expected values (the small generated set). Time is O(n + m) where n is the actual table size and m is the expected set size. Memory is O(n) for the hash set.

For continuous monitoring (checking every hour for the last 30 days), the expected set is 720 rows. The actual data table might have billions of rows, but only the distinct partition dates need to be loaded (a pre-aggregation or metadata query reduces this to hundreds of rows).

## Production Example: Pipeline Monitoring

```sql
-- Alert on missing daily partitions in the last 7 days
WITH expected AS (
    SELECT d::DATE AS partition_date
    FROM generate_series(
        CURRENT_DATE - INTERVAL '7 days',
        CURRENT_DATE - INTERVAL '1 day',
        INTERVAL '1 day'
    ) AS t(d)
),
actual AS (
    SELECT DISTINCT partition_date
    FROM pipeline_metadata
    WHERE table_name = 'fact_orders'
)
SELECT e.partition_date AS missing_date,
       CURRENT_DATE - e.partition_date AS days_missing
FROM expected e
LEFT JOIN actual a ON e.partition_date = a.partition_date
WHERE a.partition_date IS NULL
ORDER BY missing_date;
```

## Connection to Anti-Join Pattern

Gap detection is a specialized anti-join where the left table is generated rather than stored. The same three syntaxes apply (LEFT JOIN + IS NULL, NOT EXISTS, NOT IN) with the same NULL caveats. See the [Anti-Joins](../../02_joins/de_scenarios/anti_joins.md) scenario for the general pattern.

## Common Applications

- **Missing partition detection:** Expected daily/hourly partitions vs actual
- **SLA monitoring:** Expected file deliveries vs received files
- **Sequence gap analysis:** Missing IDs in auto-increment columns
- **Coverage analysis:** Expected dimension combinations vs actual fact records
- **Calendar fill:** Filling gaps with zeros for time-series visualization
