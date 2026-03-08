/*
Staging layer models - plain DuckDB SQL equivalents of the dbt staging models.
These demonstrate the same patterns without Jinja/dbt dependencies.

Patterns demonstrated:
  - Type casting and column renaming (basic SQL)
  - ROW_NUMBER dedup (sql/01_window_functions/de_scenarios/dedup_with_row_number)
  - Data cleaning (trim, lower, null filtering)
*/

-- Raw tables (simulating dbt seeds)
CREATE TABLE raw_orders (
    order_id INTEGER,
    customer_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    unit_price DECIMAL(10,2),
    order_date DATE,
    status VARCHAR(20)
);

CREATE TABLE raw_customers (
    customer_id INTEGER,
    name VARCHAR(100),
    email VARCHAR(100),
    city VARCHAR(50),
    state VARCHAR(2),
    signup_date DATE
);

CREATE TABLE raw_events (
    event_id INTEGER,
    user_id INTEGER,
    event_type VARCHAR(20),
    event_timestamp TIMESTAMP,
    page_url VARCHAR(200),
    session_id VARCHAR(50)
);

-- Staging: orders
CREATE TABLE stg_orders AS
SELECT
    order_id,
    customer_id,
    product_id,
    quantity,
    unit_price,
    order_date,
    lower(trim(status)) AS status,
    quantity * unit_price AS line_total
FROM raw_orders
WHERE order_id IS NOT NULL;

-- Staging: customers
CREATE TABLE stg_customers AS
SELECT
    customer_id,
    trim(name) AS customer_name,
    lower(trim(email)) AS email,
    trim(city) AS city,
    trim(state) AS state,
    signup_date
FROM raw_customers
WHERE customer_id IS NOT NULL;

-- Staging: events (with dedup)
CREATE TABLE stg_events AS
WITH deduplicated AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY event_id
            ORDER BY event_timestamp DESC
        ) AS _row_num
    FROM raw_events
)
SELECT
    event_id,
    user_id,
    lower(trim(event_type)) AS event_type,
    event_timestamp,
    trim(page_url) AS page_url
FROM deduplicated
WHERE _row_num = 1;
