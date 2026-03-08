# LATERAL JOIN

LATERAL allows a subquery on the right side of a join to reference columns
from the left side. This enables per-row subqueries, which is useful for
top-N-per-group and flattening nested data.

## How It Works

In a normal join, the right side cannot reference the left side. LATERAL
removes this restriction:

```sql
SELECT d.name, e.employee_name, e.salary
FROM departments d,
LATERAL (
    SELECT name AS employee_name, salary
    FROM employees
    WHERE department_id = d.id    -- references d from the left side
    ORDER BY salary DESC
    LIMIT 2
) e;
```

The subquery executes once per row from the left table. For each department,
it finds the top 2 employees by salary.

## Top-N Per Group

LATERAL is often the cleanest solution for top-N-per-group:

```sql
-- Top 3 orders per customer
SELECT c.name, o.order_id, o.amount
FROM customers c,
LATERAL (
    SELECT order_id, amount
    FROM orders
    WHERE customer_id = c.id
    ORDER BY amount DESC
    LIMIT 3
) o;
```

Compare with the window function approach:
```sql
SELECT name, order_id, amount FROM (
    SELECT c.name, o.order_id, o.amount,
           ROW_NUMBER() OVER (PARTITION BY c.id ORDER BY o.amount DESC) AS rn
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
) t WHERE rn <= 3;
```

LATERAL is more readable for simple cases. The window function approach is
more flexible (works in all engines) and faster for large datasets.

## Flattening Arrays

LATERAL is used to unnest array-like data:

**Postgres:**
```sql
SELECT id, elem
FROM documents,
LATERAL unnest(tags) AS elem;
```

**BigQuery (UNNEST alternative):**
```sql
SELECT id, tag
FROM documents, UNNEST(tags) AS tag;
```

**Spark SQL (explode alternative):**
```sql
SELECT id, explode(tags) AS tag
FROM documents;
```

## At Scale

LATERAL executes the subquery once per row from the left side. For a small
number of groups (thousands of departments), this is efficient. For millions
of groups (per-user queries on a large user table), the window function
approach is faster because it processes all groups in a single sort/hash pass.

**Rule of thumb:**
- Few groups (< 10K): LATERAL is fine and often cleaner
- Many groups (> 100K): prefer window functions for better parallelism

## Dialect Comparison

| Engine | LATERAL Support | Alternative |
|---|---|---|
| DuckDB | Yes | - |
| Postgres | Yes | - |
| Snowflake | Yes | FLATTEN for arrays |
| BigQuery | No | UNNEST for arrays, window functions for top-N |
| Spark SQL | No | explode() for arrays, window functions for top-N |

## Important Notes

- LATERAL implies CROSS JOIN semantics. If the subquery returns no rows for a
  left-side row, that row is excluded. Use `LEFT JOIN LATERAL ... ON true`
  to preserve all left-side rows.
- The comma syntax (`FROM a, LATERAL (...)`) is equivalent to
  `FROM a CROSS JOIN LATERAL (...)`.
