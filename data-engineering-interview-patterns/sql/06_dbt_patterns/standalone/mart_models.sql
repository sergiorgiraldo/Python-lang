/*
Mart layer models - plain DuckDB SQL equivalents of the dbt mart models.
These demonstrate the same patterns without Jinja/dbt dependencies.

Patterns demonstrated:
  - Fact table with dimensional join (star schema pattern)
  - Pre-aggregated daily report with cumulative window (sql/03_aggregations + sql/05_optimization)
  - Cohort analysis with conditional aggregation (sql/03_aggregations)
  - Incremental logic shown as comments (dbt handles this via Jinja)
*/

-- ============================================================
-- Input tables (output from staging and intermediate layers)
-- ============================================================

CREATE TABLE stg_orders (
    order_id INTEGER,
    customer_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    unit_price DECIMAL(10,2),
    order_date DATE,
    status VARCHAR(20),
    line_total DECIMAL(10,2)
);

INSERT INTO stg_orders VALUES
(1, 100, 10, 2, 25.00, '2024-01-15', 'completed', 50.00),
(2, 101, 11, 1, 50.00, '2024-01-15', 'completed', 50.00),
(3, 100, 12, 3, 15.00, '2024-01-16', 'completed', 45.00),
(4, 102, 10, 1, 25.00, '2024-01-17', 'pending', 25.00),
(5, 101, 13, 2, 30.00, '2024-01-18', 'completed', 60.00),
(6, 100, 11, 1, 50.00, '2024-01-19', 'cancelled', 50.00),
(7, 103, 10, 5, 25.00, '2024-01-20', 'completed', 125.00),
(8, 102, 12, 2, 15.00, '2024-01-20', 'completed', 30.00),
(9, 104, 14, 1, 100.00, '2024-01-21', 'completed', 100.00),
(10, 100, 10, 1, 25.00, '2024-01-22', 'completed', 25.00);

CREATE TABLE stg_customers (
    customer_id INTEGER,
    customer_name VARCHAR(100),
    email VARCHAR(100),
    city VARCHAR(50),
    state VARCHAR(2),
    signup_date DATE
);

INSERT INTO stg_customers VALUES
(100, 'Alice Smith', 'alice@example.com', 'Portland', 'OR', '2023-06-01'),
(101, 'Bob Johnson', 'bob@example.com', 'Seattle', 'WA', '2023-07-15'),
(102, 'Carol Williams', 'carol@example.com', 'Portland', 'OR', '2023-08-20'),
(103, 'Dave Brown', 'dave@example.com', 'San Francisco', 'CA', '2023-09-10'),
(104, 'Eve Davis', 'eve@example.com', 'Seattle', 'WA', '2024-01-05'),
(105, 'Frank White', 'frank@example.com', 'Denver', 'CO', '2024-01-15');

-- int_customer_orders (output from intermediate layer, for cohort analysis)
CREATE TABLE int_customer_orders (
    customer_id INTEGER,
    customer_name VARCHAR(100),
    email VARCHAR(100),
    city VARCHAR(50),
    state VARCHAR(2),
    signup_date DATE,
    total_orders INTEGER,
    completed_orders INTEGER,
    total_revenue DECIMAL(10,2),
    first_order_date DATE,
    last_order_date DATE,
    customer_status VARCHAR(20)
);

INSERT INTO int_customer_orders VALUES
(100, 'Alice Smith', 'alice@example.com', 'Portland', 'OR', '2023-06-01', 4, 3, 120.00, '2024-01-15', '2024-01-22', 'churned'),
(101, 'Bob Johnson', 'bob@example.com', 'Seattle', 'WA', '2023-06-15', 2, 2, 110.00, '2024-01-15', '2024-01-18', 'churned'),
(102, 'Carol Williams', 'carol@example.com', 'Portland', 'OR', '2023-08-20', 2, 1, 30.00, '2024-01-17', '2024-01-20', 'churned'),
(103, 'Dave Brown', 'dave@example.com', 'San Francisco', 'CA', '2023-09-10', 1, 1, 125.00, '2024-01-20', '2024-01-20', 'churned'),
(104, 'Eve Davis', 'eve@example.com', 'Seattle', 'WA', '2024-01-05', 1, 1, 100.00, '2024-01-21', '2024-01-21', 'churned'),
(105, 'Frank White', 'frank@example.com', 'Denver', 'CO', '2024-01-15', 0, 0, 0, NULL, NULL, 'never_ordered');


-- ============================================================
-- Mart: fct_orders (full refresh version)
-- dbt model: fct_orders.sql (incremental in dbt, full refresh here)
-- The dbt version uses is_incremental() to filter new rows only.
-- In full refresh mode the WHERE clause is omitted.
-- Connection: star schema pattern
-- ============================================================
CREATE TABLE fct_orders AS
SELECT
    o.order_id,
    o.customer_id,
    c.customer_name,
    c.city AS customer_city,
    c.state AS customer_state,
    o.product_id,
    o.quantity,
    o.unit_price,
    o.line_total,
    o.order_date,
    o.status,
    EXTRACT(YEAR FROM o.order_date) AS order_year,
    EXTRACT(MONTH FROM o.order_date) AS order_month,
    EXTRACT(DOW FROM o.order_date) AS order_day_of_week
FROM stg_orders o
LEFT JOIN stg_customers c ON o.customer_id = c.customer_id;


-- ============================================================
-- Mart: rpt_daily_revenue
-- dbt model: rpt_daily_revenue.sql
-- Connection: sql/03_aggregations + sql/05_optimization
-- ============================================================
CREATE TABLE rpt_daily_revenue AS
WITH orders AS (
    SELECT * FROM fct_orders
    WHERE status = 'completed'
),

daily_revenue AS (
    SELECT
        order_date,
        COUNT(*) AS order_count,
        COUNT(DISTINCT customer_id) AS unique_customers,
        SUM(line_total) AS total_revenue,
        AVG(line_total) AS avg_order_value,
        SUM(CASE WHEN customer_state = 'OR' THEN line_total ELSE 0 END) AS revenue_oregon,
        SUM(CASE WHEN customer_state = 'WA' THEN line_total ELSE 0 END) AS revenue_washington,
        SUM(CASE WHEN customer_state = 'CA' THEN line_total ELSE 0 END) AS revenue_california
    FROM orders
    GROUP BY order_date
)

SELECT
    *,
    SUM(total_revenue) OVER (
        ORDER BY order_date
        ROWS UNBOUNDED PRECEDING
    ) AS cumulative_revenue
FROM daily_revenue;


-- ============================================================
-- Mart: rpt_customer_cohorts
-- dbt model: rpt_customer_cohorts.sql
-- Connection: sql/03_aggregations (multi-level aggregation)
-- ============================================================
CREATE TABLE rpt_customer_cohorts AS
WITH cohorts AS (
    SELECT
        DATE_TRUNC('month', signup_date) AS cohort_month,
        COUNT(*) AS cohort_size,
        COUNT(CASE WHEN total_orders > 0 THEN 1 END) AS customers_with_orders,
        SUM(total_revenue) AS cohort_revenue,
        AVG(total_orders) AS avg_orders_per_customer,
        AVG(total_revenue) AS avg_revenue_per_customer
    FROM int_customer_orders
    GROUP BY DATE_TRUNC('month', signup_date)
)

SELECT
    *,
    ROUND(100.0 * customers_with_orders / cohort_size, 1) AS conversion_rate_pct
FROM cohorts;
