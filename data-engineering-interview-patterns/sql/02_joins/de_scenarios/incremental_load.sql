/*
Incremental Load Detection

Using joins to detect new, changed and deleted records between
a source snapshot and a target table.

This is the foundation of SQL-based Change Data Capture (CDC).
*/

-- Setup: source (latest snapshot) and target (current warehouse state)
CREATE TABLE source_customers (
    customer_id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(200),
    updated_at TIMESTAMP
);

CREATE TABLE target_customers (
    customer_id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(200),
    updated_at TIMESTAMP
);

-- Target: yesterday's state
INSERT INTO target_customers VALUES
    (1, 'Alice', 'alice@old.com', '2024-01-14 10:00:00'),
    (2, 'Bob', 'bob@example.com', '2024-01-14 10:00:00'),
    (3, 'Carol', 'carol@example.com', '2024-01-14 10:00:00'),
    (5, 'Eve', 'eve@example.com', '2024-01-14 10:00:00');

-- Source: today's snapshot
INSERT INTO source_customers VALUES
    (1, 'Alice', 'alice@new.com', '2024-01-15 09:00:00'),  -- changed email
    (2, 'Bob', 'bob@example.com', '2024-01-14 10:00:00'),  -- unchanged
    (3, 'Carol', 'carol@example.com', '2024-01-14 10:00:00'),  -- unchanged
    (4, 'Dave', 'dave@example.com', '2024-01-15 08:00:00');  -- new customer


-- Detect NEW records (in source but not in target)
SELECT s.*
FROM source_customers s
LEFT JOIN target_customers t ON s.customer_id = t.customer_id
WHERE t.customer_id IS NULL;

-- Detect CHANGED records (in both but different)
-- SELECT s.*
-- FROM source_customers s
-- INNER JOIN target_customers t ON s.customer_id = t.customer_id
-- WHERE s.updated_at > t.updated_at;

-- Detect DELETED records (in target but not in source)
-- SELECT t.*
-- FROM target_customers t
-- LEFT JOIN source_customers s ON t.customer_id = s.customer_id
-- WHERE s.customer_id IS NULL;
