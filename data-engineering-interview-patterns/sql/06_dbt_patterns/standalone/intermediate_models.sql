/*
Intermediate layer models - plain DuckDB SQL equivalents of the dbt intermediate models.
These demonstrate the same patterns without Jinja/dbt dependencies.

Patterns demonstrated:
  - Sessionization via LAG + gap detection (sql/01_window_functions/de_scenarios/sessionization)
  - LEFT JOIN + GROUP BY aggregation (sql/02_joins + sql/03_aggregations)
  - SCD Type 2 via LEAD + ROW_NUMBER (sql/01_window_functions/de_scenarios/change_detection)
*/

-- ============================================================
-- Input tables (output from staging layer)
-- ============================================================

-- Staging events (post-dedup, output from stg_events)
CREATE TABLE stg_events (
    event_id INTEGER,
    user_id INTEGER,
    event_type VARCHAR(20),
    event_timestamp TIMESTAMP,
    page_url VARCHAR(200)
);

INSERT INTO stg_events VALUES
(1, 100, 'page_view', '2024-01-15 10:00:00', '/home'),
(2, 100, 'page_view', '2024-01-15 10:02:00', '/products'),
(3, 100, 'add_to_cart', '2024-01-15 10:05:00', '/products/10'),
(4, 100, 'page_view', '2024-01-15 10:30:00', '/checkout'),
(5, 100, 'purchase', '2024-01-15 10:32:00', '/checkout/confirm'),
(6, 101, 'page_view', '2024-01-15 11:00:00', '/home'),
(7, 101, 'page_view', '2024-01-15 11:01:00', '/products'),
(8, 100, 'page_view', '2024-01-15 14:00:00', '/home'),
(9, 100, 'page_view', '2024-01-15 14:05:00', '/account'),
(10, 101, 'page_view', '2024-01-15 14:30:00', '/home');

-- Staging customers (output from stg_customers)
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
(105, 'Frank White', 'frank@example.com', 'Denver', 'CO', '2024-02-01');

-- Staging orders (output from stg_orders, with line_total pre-computed)
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

-- Raw customer history (seed, for SCD Type 2)
CREATE TABLE raw_customer_history (
    customer_id INTEGER,
    name VARCHAR(100),
    email VARCHAR(100),
    city VARCHAR(50),
    state VARCHAR(2),
    effective_date DATE
);

INSERT INTO raw_customer_history VALUES
(100, 'Alice Smith', 'alice@example.com', 'Eugene', 'OR', '2023-06-01'),
(100, 'Alice Smith', 'alice@example.com', 'Portland', 'OR', '2023-09-15'),
(101, 'Bob Johnson', 'bob@example.com', 'Tacoma', 'WA', '2023-07-15'),
(101, 'Bob Johnson', 'bob@example.com', 'Seattle', 'WA', '2023-11-01'),
(102, 'Carol Williams', 'carol@example.com', 'Portland', 'OR', '2023-08-20'),
(103, 'Dave Brown', 'dave@example.com', 'San Francisco', 'CA', '2023-09-10'),
(104, 'Eve Davis', 'eve@example.com', 'Seattle', 'WA', '2024-01-05');


-- ============================================================
-- Intermediate: sessionization via gap detection
-- dbt model: int_deduped_events.sql
-- Connection: sql/01_window_functions/de_scenarios/sessionization
-- ============================================================
CREATE TABLE int_deduped_events AS
WITH with_prev_timestamp AS (
    SELECT
        *,
        LAG(event_timestamp) OVER (
            PARTITION BY user_id
            ORDER BY event_timestamp
        ) AS prev_event_timestamp
    FROM stg_events
),

with_session_boundary AS (
    SELECT
        *,
        CASE
            WHEN prev_event_timestamp IS NULL THEN 1
            WHEN EXTRACT(EPOCH FROM event_timestamp - prev_event_timestamp) > 1800 THEN 1
            ELSE 0
        END AS is_new_session
    FROM with_prev_timestamp
),

with_session_id AS (
    SELECT
        event_id,
        user_id,
        event_type,
        event_timestamp,
        page_url,
        SUM(is_new_session) OVER (
            PARTITION BY user_id
            ORDER BY event_timestamp
            ROWS UNBOUNDED PRECEDING
        ) AS session_number
    FROM with_session_boundary
)

SELECT
    *,
    user_id || '-' || session_number AS session_id
FROM with_session_id;


-- ============================================================
-- Intermediate: customer dimension with order aggregates
-- dbt model: int_customer_orders.sql
-- Connection: sql/02_joins (LEFT JOIN) + sql/03_aggregations (GROUP BY)
-- ============================================================
CREATE TABLE int_customer_orders AS
WITH order_summary AS (
    SELECT
        customer_id,
        COUNT(*) AS total_orders,
        COUNT(CASE WHEN status = 'completed' THEN 1 END) AS completed_orders,
        SUM(CASE WHEN status = 'completed' THEN line_total ELSE 0 END) AS total_revenue,
        MIN(order_date) AS first_order_date,
        MAX(order_date) AS last_order_date
    FROM stg_orders
    GROUP BY customer_id
)

SELECT
    c.customer_id,
    c.customer_name,
    c.email,
    c.city,
    c.state,
    c.signup_date,
    COALESCE(o.total_orders, 0) AS total_orders,
    COALESCE(o.completed_orders, 0) AS completed_orders,
    COALESCE(o.total_revenue, 0) AS total_revenue,
    o.first_order_date,
    o.last_order_date,
    CASE
        WHEN o.total_orders IS NULL THEN 'never_ordered'
        WHEN o.last_order_date >= current_date - INTERVAL '30' DAY THEN 'active'
        WHEN o.last_order_date >= current_date - INTERVAL '90' DAY THEN 'lapsing'
        ELSE 'churned'
    END AS customer_status
FROM stg_customers c
LEFT JOIN order_summary o ON c.customer_id = o.customer_id;


-- ============================================================
-- Intermediate: SCD Type 2 customer dimension
-- dbt model: int_customers_scd2.sql
-- Connection: sql/01_window_functions/de_scenarios/change_detection
-- ============================================================
CREATE TABLE int_customers_scd2 AS
WITH with_row_number AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY effective_date
        ) AS version_number,
        LEAD(effective_date) OVER (
            PARTITION BY customer_id
            ORDER BY effective_date
        ) AS next_effective_date
    FROM raw_customer_history
)

SELECT
    customer_id,
    name AS customer_name,
    email,
    city,
    state,
    effective_date,
    COALESCE(
        next_effective_date - INTERVAL '1' DAY,
        CAST('9999-12-31' AS DATE)
    ) AS expiry_date,
    CASE
        WHEN next_effective_date IS NULL THEN true
        ELSE false
    END AS is_current,
    version_number
FROM with_row_number;
