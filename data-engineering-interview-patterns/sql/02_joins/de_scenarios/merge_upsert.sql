/*
MERGE / Upsert Patterns

DuckDB does not support the full MERGE syntax, but supports
INSERT ... ON CONFLICT for upsert behavior.

This scenario shows the conceptual MERGE pattern and the
DuckDB-compatible equivalent.
*/

-- Setup
CREATE TABLE dim_customer (
    customer_id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(200),
    status VARCHAR(20) DEFAULT 'active',
    updated_at TIMESTAMP
);

CREATE TABLE staging_customer (
    customer_id INTEGER,
    name VARCHAR(100),
    email VARCHAR(200),
    updated_at TIMESTAMP
);

-- Existing dimension data
INSERT INTO dim_customer VALUES
    (1, 'Alice', 'alice@old.com', 'active', '2024-01-14 10:00:00'),
    (2, 'Bob', 'bob@example.com', 'active', '2024-01-14 10:00:00'),
    (3, 'Carol', 'carol@example.com', 'active', '2024-01-14 10:00:00');

-- Incoming staging data
INSERT INTO staging_customer VALUES
    (1, 'Alice', 'alice@new.com', '2024-01-15 09:00:00'),     -- changed
    (2, 'Bob', 'bob@example.com', '2024-01-14 10:00:00'),     -- unchanged
    (4, 'Dave', 'dave@example.com', '2024-01-15 08:00:00');    -- new


-- DuckDB upsert: INSERT ... ON CONFLICT
INSERT INTO dim_customer (customer_id, name, email, updated_at)
SELECT customer_id, name, email, updated_at
FROM staging_customer
ON CONFLICT (customer_id) DO UPDATE SET
    name = EXCLUDED.name,
    email = EXCLUDED.email,
    updated_at = EXCLUDED.updated_at;


-- Verify result
-- SELECT * FROM dim_customer ORDER BY customer_id;
