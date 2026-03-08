# Query Optimization Walkthrough

Step-by-step optimization of a query with multiple anti-patterns.

## The Slow Query

```sql
SELECT DISTINCT o.*
FROM (
    SELECT * FROM orders_opt
    ORDER BY order_date DESC
) o
JOIN order_items_opt i ON o.order_id = i.order_id
WHERE YEAR(o.order_date) = 2023
  AND o.status = 'completed'
  AND o.region = 'East';
```

This query has five anti-patterns stacked together.

## Step 1: Identify Anti-Patterns

Run `EXPLAIN ANALYZE` on the slow query and examine the plan:

| Anti-Pattern | Impact |
|---|---|
| `SELECT *` | Reads all columns, wasting I/O in columnar storage |
| `DISTINCT` after JOIN | Fan-out from join then collapse. Double the work. |
| `YEAR(order_date) = 2023` | Function on column prevents index/partition pruning |
| No partition filter | Full scan on date-partitioned tables |
| `ORDER BY` in subquery | Wasted sort that the outer query may discard |

## Step 2: Fix One at a Time

### Fix 1: Remove SELECT *

Replace `SELECT *` with only the columns needed:

```sql
SELECT DISTINCT o.order_id, o.customer_id, o.order_date, o.total_amount
```

**Impact**: in columnar storage, reading 4 columns instead of 6 can reduce
I/O by ~33%.

### Fix 2: Replace JOIN + DISTINCT with EXISTS

The join to order_items fans out rows (3 items per order = 3x duplication),
then DISTINCT collapses them back. EXISTS stops after finding the first match:

```sql
WHERE EXISTS (SELECT 1 FROM order_items_opt i WHERE i.order_id = o.order_id)
```

**Impact**: eliminates the fan-out and the dedup sort/hash. Reduces intermediate
result set by ~3x.

### Fix 3: Replace YEAR() with Range Predicate

```sql
-- Before (not sargable)
WHERE YEAR(o.order_date) = 2023

-- After (sargable)
WHERE o.order_date >= '2023-01-01' AND o.order_date < '2024-01-01'
```

**Impact**: enables index usage and partition pruning. On a date-partitioned
table, this is the difference between scanning all partitions and scanning one
year of partitions.

### Fix 4: Remove ORDER BY from Subquery

The ORDER BY inside the subquery has no guaranteed effect on the outer query's
ordering. Move it to the outermost query:

```sql
SELECT ... FROM orders_opt o WHERE ... ORDER BY o.order_date DESC;
```

**Impact**: eliminates a wasted sort of 100K rows.

## Step 3: Final Optimized Query

```sql
SELECT o.order_id, o.customer_id, o.order_date, o.total_amount
FROM orders_opt o
WHERE o.order_date >= '2023-01-01'
  AND o.order_date < '2024-01-01'
  AND o.status = 'completed'
  AND o.region = 'East'
  AND EXISTS (
      SELECT 1 FROM order_items_opt i
      WHERE i.order_id = o.order_id
  )
ORDER BY o.order_date DESC;
```

## Step 4: Compare Plans

Run EXPLAIN ANALYZE on both and compare:

**Bad query plan** (typical):
- Sequential scan on orders (100K rows)
- Subquery sort (wasted)
- Hash join with order_items (fans out to ~300K intermediate rows)
- Hash aggregate for DISTINCT (collapse back)
- Final projection

**Optimized query plan** (typical):
- Sequential scan on orders with pushdown filters (reads ~6.25K matching rows)
- Semi-join (EXISTS) with order_items (no fan-out)
- Sort for ORDER BY (only on ~6.25K rows)

## Measuring Improvement

In DuckDB with 100K orders and 300K items:
- Bad query processes significantly more intermediate rows due to the join fan-out
- Optimized query filters early and avoids the fan-out entirely
- The sort operates on ~6.25K rows instead of 100K

At production scale (billions of rows), these differences compound:
- Column pruning saves terabytes of I/O
- EXISTS vs JOIN+DISTINCT avoids materializing billions of intermediate rows
- Sargable predicates enable partition pruning, reducing scan from years to days

## Interview Approach

When asked to optimize a query:
1. **Run EXPLAIN ANALYZE** to see what the engine does
2. **Read bottom-up**: identify the most expensive operator
3. **Fix one thing at a time**, re-running EXPLAIN after each change
4. **Measure improvement**: compare row counts and timing at each step
5. **Explain your reasoning**: "I replaced JOIN+DISTINCT with EXISTS because
   the join fans out rows that DISTINCT then collapses. EXISTS short-circuits."
