/*
Conditional Aggregation with CASE

Compute multiple filtered aggregates in a single table scan by
embedding CASE expressions inside aggregate functions.

Scenario: monthly revenue breakdown by product category from an orders table.
*/

-- Setup
CREATE TABLE orders (
    id INTEGER,
    order_date DATE,
    category VARCHAR(50),
    amount DECIMAL(10, 2),
    status VARCHAR(20)
);

INSERT INTO orders VALUES
    (1, '2024-01-05', 'electronics', 299.99, 'completed'),
    (2, '2024-01-10', 'clothing', 49.99, 'completed'),
    (3, '2024-01-15', 'electronics', 199.99, 'completed'),
    (4, '2024-01-20', 'food', 25.00, 'cancelled'),
    (5, '2024-02-01', 'electronics', 499.99, 'completed'),
    (6, '2024-02-05', 'clothing', 79.99, 'completed'),
    (7, '2024-02-10', 'food', 35.00, 'completed'),
    (8, '2024-02-15', 'electronics', 149.99, 'refunded');


-- Approach 1: SUM(CASE WHEN ...) for filtered sums
SELECT
    DATE_TRUNC('month', order_date) AS month,
    SUM(CASE WHEN category = 'electronics' THEN amount ELSE 0 END) AS electronics_revenue,
    SUM(CASE WHEN category = 'clothing' THEN amount ELSE 0 END) AS clothing_revenue,
    SUM(CASE WHEN category = 'food' THEN amount ELSE 0 END) AS food_revenue,
    SUM(amount) AS total_revenue
FROM orders
WHERE status = 'completed'
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month;


-- Approach 2: COUNT(CASE WHEN ...) for filtered counts
-- SELECT
--     DATE_TRUNC('month', order_date) AS month,
--     COUNT(CASE WHEN status = 'completed' THEN 1 END) AS completed,
--     COUNT(CASE WHEN status = 'cancelled' THEN 1 END) AS cancelled,
--     COUNT(CASE WHEN status = 'refunded' THEN 1 END) AS refunded,
--     COUNT(*) AS total
-- FROM orders
-- GROUP BY DATE_TRUNC('month', order_date)
-- ORDER BY month;


-- Approach 3: FILTER clause (DuckDB/Postgres only)
-- SELECT
--     DATE_TRUNC('month', order_date) AS month,
--     SUM(amount) FILTER (WHERE category = 'electronics') AS electronics_revenue,
--     SUM(amount) FILTER (WHERE category = 'clothing') AS clothing_revenue,
--     SUM(amount) FILTER (WHERE category = 'food') AS food_revenue,
--     SUM(amount) AS total_revenue
-- FROM orders
-- WHERE status = 'completed'
-- GROUP BY DATE_TRUNC('month', order_date)
-- ORDER BY month;
