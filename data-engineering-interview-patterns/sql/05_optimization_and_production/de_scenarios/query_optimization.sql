/*
Query Optimization Walkthrough

Demonstrates optimizing a query step by step using EXPLAIN ANALYZE.
We create a reasonably sized dataset, write a bad query with multiple
anti-patterns, then fix them one at a time.
*/

-- Generate a dataset: 100K orders with line items
CREATE TABLE orders_opt (
    order_id INTEGER,
    customer_id INTEGER,
    order_date DATE,
    status VARCHAR(20),
    region VARCHAR(20),
    total_amount DECIMAL(10,2)
);

CREATE TABLE order_items_opt (
    item_id INTEGER,
    order_id INTEGER,
    product_name VARCHAR(50),
    quantity INTEGER,
    unit_price DECIMAL(10,2)
);

-- 100K orders across 4 regions, 10K customers, 1 year of dates
INSERT INTO orders_opt
SELECT
    i AS order_id,
    (i % 10000) + 1 AS customer_id,
    DATE '2023-01-01' + CAST(i % 365 AS INTEGER) AS order_date,
    CASE i % 4
        WHEN 0 THEN 'completed'
        WHEN 1 THEN 'pending'
        WHEN 2 THEN 'shipped'
        ELSE 'cancelled'
    END AS status,
    CASE i % 4
        WHEN 0 THEN 'East'
        WHEN 1 THEN 'West'
        WHEN 2 THEN 'North'
        ELSE 'South'
    END AS region,
    ROUND((i % 500) + 10.0, 2) AS total_amount
FROM generate_series(1, 100000) AS t(i);

-- ~3 items per order = 300K items
INSERT INTO order_items_opt
SELECT
    ROW_NUMBER() OVER () AS item_id,
    o.order_id,
    CASE (o.order_id + s.n) % 5
        WHEN 0 THEN 'Widget'
        WHEN 1 THEN 'Gadget'
        WHEN 2 THEN 'Sprocket'
        WHEN 3 THEN 'Bolt'
        ELSE 'Nut'
    END AS product_name,
    ((o.order_id + s.n) % 10) + 1 AS quantity,
    ROUND(((o.order_id + s.n) % 50) + 5.0, 2) AS unit_price
FROM orders_opt o
CROSS JOIN (SELECT unnest(generate_series(1, 3)) AS n) s;

-- ============================================================
-- BAD QUERY: multiple anti-patterns combined
-- Anti-patterns:
--   1. SELECT * (reads all columns)
--   2. DISTINCT to hide join fan-out
--   3. Function on column in WHERE (YEAR())
--   4. No partition filter
--   5. ORDER BY in subquery
-- ============================================================

EXPLAIN ANALYZE
SELECT DISTINCT o.*
FROM (
    SELECT * FROM orders_opt
    ORDER BY order_date DESC
) o
JOIN order_items_opt i ON o.order_id = i.order_id
WHERE YEAR(o.order_date) = 2023
  AND o.status = 'completed'
  AND o.region = 'East';

-- ============================================================
-- OPTIMIZED QUERY: fix all anti-patterns
-- Fixes:
--   1. Select only needed columns
--   2. Remove DISTINCT (use EXISTS instead of JOIN)
--   3. Use range predicate instead of YEAR()
--   4. Filter early
--   5. Remove ORDER BY from subquery, apply at end
-- ============================================================

EXPLAIN ANALYZE
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
