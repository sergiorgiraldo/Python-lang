/*
Anti-Joins for Finding Gaps

Three syntaxes for the same logical operation: find rows in the left
table that have no matching row in the right table.

Scenario: find expected daily partitions that are missing from a table.
*/

-- Setup: expected dates and actual partitions
CREATE TABLE expected_dates (partition_date DATE);
CREATE TABLE actual_partitions (partition_date DATE, row_count INTEGER);

INSERT INTO expected_dates VALUES
    ('2024-01-01'), ('2024-01-02'), ('2024-01-03'),
    ('2024-01-04'), ('2024-01-05'), ('2024-01-06'), ('2024-01-07');

INSERT INTO actual_partitions VALUES
    ('2024-01-01', 1500), ('2024-01-02', 1420),
    ('2024-01-03', 1380), ('2024-01-05', 1510), ('2024-01-07', 1490);
-- Missing: 2024-01-04 and 2024-01-06


-- Approach 1: LEFT JOIN + IS NULL
SELECT e.partition_date AS missing_date
FROM expected_dates e
LEFT JOIN actual_partitions a ON e.partition_date = a.partition_date
WHERE a.partition_date IS NULL
ORDER BY missing_date;


-- Approach 2: NOT EXISTS
-- SELECT e.partition_date AS missing_date
-- FROM expected_dates e
-- WHERE NOT EXISTS (
--     SELECT 1 FROM actual_partitions a
--     WHERE a.partition_date = e.partition_date
-- )
-- ORDER BY missing_date;


-- Approach 3: NOT IN (use with caution - NULL trap)
-- SELECT partition_date AS missing_date
-- FROM expected_dates
-- WHERE partition_date NOT IN (
--     SELECT partition_date FROM actual_partitions
--     WHERE partition_date IS NOT NULL  -- guard against NULL
-- )
-- ORDER BY missing_date;
