/*
Gap Detection

Find missing values in sequences using generate_series + LEFT JOIN.

Scenario: detect missing daily partitions in a data pipeline.
*/

-- Setup: a table with some daily partitions (gaps on Jan 4 and Jan 6)
CREATE TABLE daily_partitions (
    partition_date DATE,
    row_count INTEGER
);

INSERT INTO daily_partitions VALUES
    ('2024-01-01', 1500),
    ('2024-01-02', 1420),
    ('2024-01-03', 1380),
    ('2024-01-05', 1510),
    ('2024-01-07', 1490);


-- Approach 1: Missing dates using generate_series + LEFT JOIN
SELECT expected.d AS missing_date
FROM generate_series(
    DATE '2024-01-01',
    DATE '2024-01-07',
    INTERVAL '1 day'
) AS expected(d)
LEFT JOIN daily_partitions dp ON expected.d = dp.partition_date
WHERE dp.partition_date IS NULL
ORDER BY missing_date;


-- Approach 2: Gaps in sequential IDs
-- CREATE TABLE events (id INTEGER);
-- INSERT INTO events VALUES (1), (2), (3), (5), (8), (9), (10);
--
-- SELECT gs.id AS missing_id
-- FROM generate_series(1, 10) AS gs(id)
-- LEFT JOIN events e ON gs.id = e.id
-- WHERE e.id IS NULL
-- ORDER BY missing_id;


-- Approach 3: Missing values from an expected set (CROSS JOIN approach)
-- CREATE TABLE regions (region_name VARCHAR);
-- CREATE TABLE products (product_name VARCHAR);
-- CREATE TABLE sales (region_name VARCHAR, product_name VARCHAR, amount DECIMAL);
--
-- INSERT INTO regions VALUES ('North'), ('South'), ('East'), ('West');
-- INSERT INTO products VALUES ('Widget'), ('Gadget');
-- INSERT INTO sales VALUES ('North', 'Widget', 100), ('South', 'Gadget', 200),
--                           ('East', 'Widget', 150), ('East', 'Gadget', 80);
--
-- -- Find region-product combinations with no sales
-- SELECT r.region_name, p.product_name
-- FROM regions r
-- CROSS JOIN products p
-- LEFT JOIN sales s ON r.region_name = s.region_name AND p.product_name = s.product_name
-- WHERE s.amount IS NULL
-- ORDER BY r.region_name, p.product_name;
