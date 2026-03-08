# SQL Performance Anti-Patterns

Common SQL patterns that cause performance problems in production. Each
anti-pattern includes the bad code, why it hurts, the fix and when the
"bad" pattern is acceptable.

---

## 1. SELECT * in Production Queries

**Bad:**
```sql
SELECT * FROM large_table WHERE date = '2024-01-01';
```

**Why it hurts:**
Reads all columns. In columnar storage (Parquet, BigQuery, Snowflake) the engine
only reads the columns you request. SELECT * forces it to read every column,
potentially 10-100x more data than needed. This directly increases cost in
pay-per-byte systems like BigQuery.

**Fix:**
```sql
SELECT id, name, amount FROM large_table WHERE date = '2024-01-01';
```

**Acceptable when:** exploring data interactively, tables with few columns,
debugging in development.

---

## 2. DISTINCT as a Band-Aid for Bad Joins

**Bad:**
```sql
SELECT DISTINCT a.id, a.name
FROM orders a
JOIN items b ON a.id = b.order_id;
```

**Why it hurts:**
The join fans out (one order has many items) producing duplicate order rows,
then DISTINCT collapses them back. This does unnecessary work: the join
materializes the expanded result set, then a hash or sort deduplicates it.

**Fix:**
Use EXISTS when you only need the parent rows:
```sql
SELECT id, name
FROM orders
WHERE EXISTS (
    SELECT 1 FROM items WHERE order_id = orders.id
);
```

This is a semi-join: it stops scanning items after finding the first match
per order. No fan-out, no dedup.

**Acceptable when:** you need columns from both sides of the join
and duplicates are an inherent part of the result.

---

## 3. Correlated Subquery That Should Be a Join

**Bad:**
```sql
SELECT *,
       (SELECT name FROM dept WHERE dept.id = emp.dept_id) AS dept_name
FROM emp;
```

**Why it hurts:**
Conceptually executes the subquery once per row in emp. Without optimizer
intervention this is O(n * m). Even with optimization, correlated scalar
subqueries add overhead.

**Fix:**
```sql
SELECT emp.*, dept.name AS dept_name
FROM emp
LEFT JOIN dept ON emp.dept_id = dept.id;
```

**Note:** modern optimizers (Postgres, DuckDB, BigQuery) often rewrite correlated
subqueries as joins internally. But not all engines do, and complex correlated
subqueries may not get rewritten. Write the join explicitly when possible.

**Acceptable when:** the subquery contains logic that is difficult to express
as a join (e.g., conditional aggregation with different filters per row).

---

## 4. ORDER BY in Subqueries

**Bad:**
```sql
SELECT * FROM (
    SELECT * FROM events ORDER BY created_at DESC
) sub
WHERE sub.type = 'click';
```

**Why it hurts:**
ORDER BY in a subquery has no guaranteed effect on the outer query's row order.
The SQL standard does not require subquery ordering to propagate. The optimizer
may discard the sort entirely. At best, it is wasted computation.

**Fix:**
Move ORDER BY to the outermost query:
```sql
SELECT * FROM events
WHERE type = 'click'
ORDER BY created_at DESC;
```

**Exception:** ORDER BY inside a subquery with LIMIT is meaningful and necessary:
```sql
SELECT * FROM (
    SELECT * FROM events ORDER BY created_at DESC LIMIT 100
) sub
WHERE sub.type = 'click';
```

---

## 5. NOT IN with Nullable Columns

**Bad:**
```sql
SELECT * FROM customers
WHERE id NOT IN (SELECT customer_id FROM orders);
```

**Why it hurts:**
If any `customer_id` in orders is NULL, the entire NOT IN returns no rows.
This is SQL's three-valued logic: `x NOT IN (1, 2, NULL)` evaluates to
`x != 1 AND x != 2 AND x != NULL`, and `x != NULL` is UNKNOWN, making the
whole expression UNKNOWN (treated as false).

This is a correctness bug, not just a performance issue.

**Fix:**
```sql
-- Option 1: LEFT JOIN + IS NULL
SELECT c.*
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
WHERE o.id IS NULL;

-- Option 2: NOT EXISTS (handles NULLs correctly)
SELECT * FROM customers c
WHERE NOT EXISTS (
    SELECT 1 FROM orders WHERE customer_id = c.id
);
```

**Acceptable when:** you are certain the subquery column has no NULLs (enforced
by a NOT NULL constraint). Even then, NOT EXISTS is clearer about intent.

---

## 6. Missing Partition Filter on Partitioned Tables

**Bad:**
```sql
-- Table is partitioned by date
SELECT * FROM events WHERE user_id = 123;
```

**Why it hurts:**
Scans ALL partitions. A table with 365 daily partitions stores data in 365
separate chunks. Without a date filter, the engine reads every chunk, scanning
365x more data than necessary.

In BigQuery, this means 365x the bytes billed. In Snowflake, it means scanning
all micro-partitions. In Spark, it means reading all Parquet files.

**Fix:**
```sql
SELECT * FROM events
WHERE date = '2024-01-15' AND user_id = 123;
```

Always filter on the partition key first. Even an overly broad date range is
better than no partition filter at all.

**Acceptable when:** you genuinely need data across all partitions (full table
aggregation). But if you do, consider whether a materialized summary exists.

---

## 7. Aggregating After Join (Count Inflation)

**Bad:**
```sql
SELECT o.id, COUNT(*) AS item_count, SUM(o.order_total) AS total
FROM orders o
JOIN items i ON o.id = i.order_id
GROUP BY o.id;
```

**Why it hurts:**
The join fans out rows (one order with 5 items becomes 5 rows). `COUNT(*)`
now counts items, not orders. `SUM(o.order_total)` sums the order total 5
times, inflating the result by 5x. This is the "fan-out then aggregate" trap.

**Fix:**
Aggregate before joining, or use DISTINCT:
```sql
-- Option 1: aggregate items first, then join
SELECT o.id, i.item_count, o.order_total
FROM orders o
JOIN (
    SELECT order_id, COUNT(*) AS item_count
    FROM items
    GROUP BY order_id
) i ON o.id = i.order_id;

-- Option 2: use COUNT(DISTINCT) if appropriate
SELECT o.id, COUNT(DISTINCT i.id) AS item_count
FROM orders o
JOIN items i ON o.id = i.order_id
GROUP BY o.id;
```

**Acceptable when:** you are aggregating columns from the many-side of the join
and the fan-out is intentional (e.g., counting items per order is correct if
you only aggregate item columns).

---

## 8. UNION When UNION ALL Suffices

**Bad:**
```sql
SELECT id FROM table_a
UNION
SELECT id FROM table_b;
```

**Why it hurts:**
UNION deduplicates the combined result, requiring a sort or hash operation.
UNION ALL simply concatenates the results with no dedup overhead.

**Fix:**
```sql
SELECT id FROM table_a
UNION ALL
SELECT id FROM table_b;
```

**Acceptable when:** you specifically need deduplication across the two result
sets. But ask yourself: are duplicates possible? If the tables have
disjoint IDs, UNION wastes effort.

---

## 9. Repeated Expensive Subqueries

**Bad:**
```sql
SELECT
    (SELECT AVG(salary) FROM emp WHERE dept_id = 1) AS avg_dept_1,
    (SELECT AVG(salary) FROM emp WHERE dept_id = 2) AS avg_dept_2,
    (SELECT AVG(salary) FROM emp WHERE dept_id = 1) -
    (SELECT AVG(salary) FROM emp WHERE dept_id = 2) AS diff;
```

**Why it hurts:**
The same subquery appears multiple times. Depending on the engine, it may be
evaluated separately each time.

**Fix:**
Use a CTE to compute once and reference multiple times:
```sql
WITH dept_avg AS (
    SELECT dept_id, AVG(salary) AS avg_salary
    FROM emp
    WHERE dept_id IN (1, 2)
    GROUP BY dept_id
)
SELECT
    MAX(CASE WHEN dept_id = 1 THEN avg_salary END) AS avg_dept_1,
    MAX(CASE WHEN dept_id = 2 THEN avg_salary END) AS avg_dept_2,
    MAX(CASE WHEN dept_id = 1 THEN avg_salary END) -
    MAX(CASE WHEN dept_id = 2 THEN avg_salary END) AS diff
FROM dept_avg;
```

**Note on CTE materialization:** behavior varies by engine.
- **Postgres (< 12)**: CTEs are always materialized (computed once, stored in memory)
- **Postgres (>= 12)**: CTEs may be inlined unless referenced multiple times or marked with MATERIALIZED
- **BigQuery**: CTEs may be inlined and computed multiple times
- **DuckDB**: CTEs may be inlined by the optimizer
- **Snowflake**: CTEs are typically materialized

Check your engine's behavior. If the CTE is inlined, you may not get the
deduplication benefit.

**Acceptable when:** the subquery is cheap (small table, indexed lookup) and
the readability of inline subqueries is preferred.

---

## 10. Functions on Indexed Columns in WHERE

**Bad:**
```sql
WHERE YEAR(created_at) = 2024
```

**Why it hurts:**
Applying a function to the column prevents index usage. The engine must evaluate
`YEAR()` on every row because it cannot know which index entries satisfy
`YEAR(value) = 2024` without computing the function. This is called breaking
**sargability** (Search ARGument ABLE).

**Fix:**
```sql
WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01'
```

This is a range predicate on the raw column, which can use an index or enable
partition pruning.

Other common sargability violations:
```sql
-- Bad: function on column
WHERE LOWER(email) = 'alice@example.com'
WHERE CAST(amount AS INTEGER) > 100
WHERE COALESCE(status, 'unknown') = 'active'

-- Good: adjust the comparison side instead
WHERE email = 'alice@example.com'  -- store normalized, compare directly
WHERE amount > 100                 -- keep native type
WHERE status = 'active'            -- handle NULLs separately
```

**Acceptable when:** the table is small enough that a full scan is negligible,
or you are using a computed/expression index that matches the function
(Postgres supports these).

---

## Summary Table

| # | Anti-Pattern | Core Issue | Key Fix |
|---|---|---|---|
| 1 | SELECT * | Reads unnecessary columns | List specific columns |
| 2 | DISTINCT after join | Fan-out then collapse | Use EXISTS / semi-join |
| 3 | Correlated subquery | Per-row execution | Rewrite as JOIN |
| 4 | ORDER BY in subquery | Wasted sort | Move to outermost query |
| 5 | NOT IN with NULLs | Correctness bug | Use NOT EXISTS or LEFT JOIN |
| 6 | Missing partition filter | Full table scan | Filter on partition key |
| 7 | Aggregate after join | Count/sum inflation | Aggregate before join |
| 8 | UNION vs UNION ALL | Unnecessary dedup | Use UNION ALL |
| 9 | Repeated subqueries | Redundant computation | Use CTEs |
| 10 | Functions on indexed columns | Breaks sargability | Use range predicates |
