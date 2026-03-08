/*
Partition Strategy

Demonstrates the impact of partition-like filtering on query performance.
DuckDB does not have explicit partitioning syntax like BigQuery or Snowflake,
but filtering on a date column simulates the effect of partition pruning.
*/

-- Create a table with a date column as the logical partition key
CREATE TABLE web_events (
    event_id INTEGER,
    user_id INTEGER,
    event_date DATE,
    event_type VARCHAR(20),
    page_url VARCHAR(200),
    session_id VARCHAR(50)
);

-- Generate 365 days of data, ~300 events per day = ~109K events
INSERT INTO web_events
SELECT
    i AS event_id,
    (i % 5000) + 1 AS user_id,
    DATE '2023-01-01' + CAST(i % 365 AS INTEGER) AS event_date,
    CASE i % 4
        WHEN 0 THEN 'pageview'
        WHEN 1 THEN 'click'
        WHEN 2 THEN 'scroll'
        ELSE 'submit'
    END AS event_type,
    '/page/' || (i % 50) AS page_url,
    'session_' || (i % 10000) AS session_id
FROM generate_series(1, 109500) AS t(i);

-- Query WITHOUT partition filter: scans entire table
EXPLAIN ANALYZE
SELECT event_type, COUNT(*) AS cnt
FROM web_events
WHERE user_id = 42
GROUP BY event_type
ORDER BY cnt DESC;

-- Query WITH partition filter: scans only matching date range
EXPLAIN ANALYZE
SELECT event_type, COUNT(*) AS cnt
FROM web_events
WHERE event_date = DATE '2023-06-15'
  AND user_id = 42
GROUP BY event_type
ORDER BY cnt DESC;

-- Query with broader date range (still benefits from pruning)
EXPLAIN ANALYZE
SELECT event_date, event_type, COUNT(*) AS cnt
FROM web_events
WHERE event_date >= DATE '2023-06-01'
  AND event_date < DATE '2023-07-01'
GROUP BY event_date, event_type
ORDER BY event_date, cnt DESC;
