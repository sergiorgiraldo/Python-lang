# Aggregations

Aggregation functions collapse multiple rows into summary values. Combined with GROUP BY, they compute metrics per group: totals, averages, counts, extremes. Every analytics query, every dashboard metric and every data quality check uses aggregation.

## Core Aggregation Functions

| Function | Returns | NULL Handling |
|---|---|---|
| COUNT(*) | Number of rows | Counts all rows including NULLs |
| COUNT(column) | Number of non-NULL values | Skips NULLs |
| COUNT(DISTINCT column) | Number of unique non-NULL values | Skips NULLs |
| SUM(column) | Total of values | Skips NULLs; returns NULL for empty set |
| AVG(column) | Mean of values | Skips NULLs (does not treat as 0) |
| MIN(column) | Smallest value | Skips NULLs |
| MAX(column) | Largest value | Skips NULLs |

### COUNT(*) vs COUNT(column) vs COUNT(DISTINCT column)

This distinction is the most commonly tested aggregation concept:

```sql
-- Table: orders (5 rows, customer_id has one NULL)
-- customer_id: 1, 1, 2, 3, NULL

SELECT
    COUNT(*)                    AS total_rows,       -- 5
    COUNT(customer_id)          AS non_null_customers, -- 4
    COUNT(DISTINCT customer_id) AS unique_customers    -- 3
FROM orders;
```

- `COUNT(*)` counts rows, never skips anything
- `COUNT(column)` counts non-NULL values
- `COUNT(DISTINCT column)` counts unique non-NULL values

**Critical with LEFT JOIN:** `COUNT(*)` on the left side of a LEFT JOIN counts 1 for groups with no match (the NULL-filled row). Use `COUNT(right_table.column)` to count 0 for unmatched groups.

## GROUP BY Semantics

Every non-aggregated column in SELECT must appear in GROUP BY. This is an SQL standard rule enforced by most engines.

```sql
-- Correct: department_id is in GROUP BY
SELECT department_id, AVG(salary)
FROM employees
GROUP BY department_id;

-- Error: department_name is not in GROUP BY and not aggregated
SELECT department_id, department_name, AVG(salary)
FROM employees
GROUP BY department_id;
```

**MySQL exception:** MySQL's ONLY_FULL_GROUP_BY mode (off by default in older versions) allows non-grouped columns, returning an arbitrary value. This is a source of subtle bugs.

## HAVING vs WHERE

| Clause | Filters | Timing | Can Reference |
|---|---|---|---|
| WHERE | Individual rows | Before aggregation | Columns only |
| HAVING | Groups | After aggregation | Columns and aggregates |

```sql
-- WHERE: filter rows before grouping
SELECT department_id, AVG(salary)
FROM employees
WHERE hire_date > '2020-01-01'   -- filters individual rows
GROUP BY department_id;

-- HAVING: filter groups after aggregation
SELECT department_id, AVG(salary)
FROM employees
GROUP BY department_id
HAVING AVG(salary) > 75000;      -- filters groups
```

Using WHERE instead of HAVING for an aggregate condition is a syntax error. Using HAVING for a row-level condition works but is less efficient (processes all rows before filtering).

## Conditional Aggregation

Embed CASE expressions inside aggregate functions to compute multiple filtered metrics in one scan:

```sql
SELECT
    DATE_TRUNC('month', order_date) AS month,
    SUM(CASE WHEN status = 'completed' THEN amount ELSE 0 END) AS revenue,
    SUM(CASE WHEN status = 'refunded' THEN amount ELSE 0 END) AS refunds,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) AS order_count
FROM orders
GROUP BY DATE_TRUNC('month', order_date);
```

**FILTER clause (DuckDB/Postgres):** `SUM(amount) FILTER (WHERE status = 'completed')` is syntactic sugar for the CASE pattern. More readable but not portable to BigQuery, Snowflake or MySQL.

## Multi-Level Aggregation

When you need to compare segment metrics to overall metrics:

```sql
-- Department average vs company average
WITH dept_avg AS (
    SELECT departmentId, AVG(salary) AS dept_salary
    FROM employees GROUP BY departmentId
),
company_avg AS (
    SELECT AVG(salary) AS company_salary FROM employees
)
SELECT d.departmentId,
       CASE WHEN d.dept_salary > c.company_salary THEN 'above' ELSE 'below' END
FROM dept_avg d CROSS JOIN company_avg c;
```

The CTE structure separates aggregation levels cleanly. This is the template for any benchmark comparison.

## Approximate Aggregation

For high-cardinality columns, exact aggregation can be expensive:

| Function | Exact Alternative | Memory | Error |
|---|---|---|---|
| APPROX_COUNT_DISTINCT | COUNT(DISTINCT) | O(1) vs O(n) | ~2% |
| APPROX_QUANTILE | PERCENTILE_CONT | O(log n) vs O(n) | Varies |

Use approximate functions for dashboards and monitoring. Use exact functions for billing and compliance.

## Common Mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| COUNT(*) with LEFT JOIN | Counts 1 for unmatched groups | Use COUNT(right_table.column) |
| Forgetting GROUP BY columns | Syntax error (or wrong result in MySQL) | Include all non-aggregated SELECT columns |
| Aggregating before joining | Inflated counts from join fan-out | Join first with dedup, or aggregate in a subquery |
| WHERE with aggregate condition | Syntax error | Use HAVING |
| AVG treating NULLs as 0 | Incorrect average | AVG already skips NULLs; use COALESCE if you want 0s |
| COUNT(DISTINCT) on nullable column | Missing NULL count | NULLs are excluded; add separate NULL check if needed |

### Aggregating Before vs After Joining

This is the most dangerous aggregation mistake in production:

```sql
-- WRONG: join creates fan-out, inflating SUM
SELECT c.name, SUM(o.amount)
FROM customers c
JOIN orders o ON c.id = o.customer_id
JOIN order_items oi ON o.id = oi.order_id
GROUP BY c.name;
-- If an order has 3 items, the order amount is summed 3 times

-- CORRECT: aggregate in a subquery before joining
SELECT c.name, totals.total_amount
FROM customers c
JOIN (
    SELECT customer_id, SUM(amount) AS total_amount
    FROM orders
    GROUP BY customer_id
) totals ON c.id = totals.customer_id;
```

## Performance: Hash vs Sort Aggregation

### Hash Aggregation

```
For each row:
    hash(group_key) -> bucket
    update aggregate in bucket
```

- **Time:** O(n)
- **Memory:** O(distinct groups)
- **When chosen:** Default for GROUP BY in most engines

### Sort Aggregation

```
Sort all rows by group_key
Walk sorted rows, accumulating aggregates per group
```

- **Time:** O(n log n) for sort, O(n) for accumulation
- **Memory:** O(1) after sorting (streaming)
- **When chosen:** Data already sorted, or memory pressure forces spill

### Memory Requirements

| Rows | Distinct Groups | Hash Table Size | Sort Temp Space |
|---|---|---|---|
| 10M | 1K | ~100KB | ~400MB (full sort) |
| 100M | 1M | ~100MB | ~4GB |
| 1B | 100M | ~10GB (may spill) | ~40GB |

When the hash table exceeds available memory, engines switch to sort-based aggregation with disk spilling. DuckDB and Spark both handle this automatically.

## At Scale

**Partial aggregation:** In distributed engines, each node computes local aggregates before shuffling. For 10 nodes processing 1B rows, each node aggregates 100M rows locally, producing at most O(distinct_groups) rows. Only these summary rows are shuffled, reducing network traffic by orders of magnitude.

**Pre-aggregation:** For frequently queried aggregations (daily revenue, hourly user counts), materialize the results in summary tables. This trades storage for query speed and is the foundation of OLAP cube design.

**Approximate aggregation:** When exact counts are not required, HyperLogLog for cardinality and t-digest for quantiles reduce memory from O(n) to O(1).

## Connection to Algorithmic Patterns

- **Hash Map (Pattern 01):** GROUP BY is a hash map of group keys to aggregate accumulators. The hash aggregation algorithm is identical to building a Counter/defaultdict in Python.
- **Probabilistic Data Structures (Pattern 11):** APPROX_COUNT_DISTINCT uses HyperLogLog. APPROX_QUANTILE uses t-digest. These trade accuracy for massive memory savings.
- **Sorting (Pattern 05):** Sort-based aggregation and ORDER BY after GROUP BY both rely on efficient sorting algorithms.

## Problems

| # | Problem | Key Concept | Difficulty |
|---|---|---|---|
| [182](https://leetcode.com/problems/duplicate-emails/) | Duplicate Emails | GROUP BY + HAVING COUNT > 1 | Easy |
| [511](https://leetcode.com/problems/game-play-analysis-i/) | Game Play Analysis I | GROUP BY + MIN | Easy |
| [574](https://leetcode.com/problems/winning-candidate/) | Winning Candidate | JOIN + GROUP BY + ORDER BY + LIMIT | Medium |
| [585](https://leetcode.com/problems/investments-in-2016/) | Investments in 2016 | Subquery with GROUP BY + HAVING for set membership | Medium |
| [615](https://leetcode.com/problems/average-salary-departments-vs-company/) | Average Salary: Depts vs Company | Multi-level aggregation with CTE + CASE | Hard |

## DE Scenarios

| Scenario | Pattern | Production Use |
|---|---|---|
| Conditional Aggregation | SUM/COUNT with CASE, FILTER clause | Multi-metric dashboards in single scan |
| Pivot Patterns | Manual pivot, PIVOT/UNPIVOT syntax | ML feature engineering, report reshaping |
| Gap Detection | generate_series + LEFT JOIN | Missing partition detection, SLA monitoring |
| Approximate Counting | COUNT(DISTINCT) vs APPROX_COUNT_DISTINCT | Dashboard metrics, cardinality monitoring |
