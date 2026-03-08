# QUALIFY Clause

QUALIFY is to window functions what HAVING is to GROUP BY. It filters rows
after window function evaluation, eliminating the need for a wrapping subquery.

## SQL Clause Evaluation Order

```
FROM → WHERE → GROUP BY → HAVING → WINDOW → QUALIFY → ORDER BY → LIMIT
```

QUALIFY sits between WINDOW and ORDER BY. It can reference any window function
defined in the SELECT clause (or define one inline).

## Core Pattern

```sql
-- With QUALIFY (DuckDB, BigQuery, Snowflake, Databricks)
SELECT user_id, event_type, event_time
FROM events
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY user_id, event_type
    ORDER BY event_time DESC
) = 1;

-- Without QUALIFY (Postgres, MySQL, Spark SQL)
SELECT user_id, event_type, event_time
FROM (
    SELECT *, ROW_NUMBER() OVER (
        PARTITION BY user_id, event_type
        ORDER BY event_time DESC
    ) AS rn
    FROM events
) t
WHERE rn = 1;
```

Both produce the same result. QUALIFY saves one level of subquery nesting and
is more readable.

## Common Use Cases

### Dedup (keep latest per group)
```sql
SELECT * FROM raw_events
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY event_id ORDER BY received_at DESC
) = 1;
```

### Top-N per group
```sql
SELECT * FROM employees
QUALIFY RANK() OVER (
    PARTITION BY department_id ORDER BY salary DESC
) <= 3;
```

### Filter on cumulative total
```sql
SELECT * FROM transactions
QUALIFY SUM(amount) OVER (
    PARTITION BY account_id ORDER BY txn_date
    ROWS UNBOUNDED PRECEDING
) <= 10000;
```

## Dialect Notes

| Engine | QUALIFY Support |
|---|---|
| DuckDB | Yes |
| BigQuery | Yes |
| Snowflake | Yes |
| Databricks | Yes |
| Postgres | No - use subquery with WHERE |
| MySQL | No - use subquery with WHERE |
| Spark SQL (OSS) | No - use subquery with WHERE |

## Interview Tip

If the target company uses BigQuery or Snowflake, use QUALIFY in your SQL
answers. It shows you know the engine and write idiomatic queries. If the
company uses Postgres, use the subquery workaround and mention that you would
use QUALIFY if the engine supported it.

QUALIFY makes dedup, top-N-per-group and other window-filter patterns
significantly cleaner. In a whiteboard interview, less nesting means fewer
mistakes and faster writing.
