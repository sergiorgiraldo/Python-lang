/*
Materialized Views vs Scheduled Queries

DuckDB does not have native materialized views. We simulate the pattern
by creating a regular table from a query (materialization) and comparing
performance of querying the materialized table vs computing on the fly.
*/

-- Base table: raw event data (200K rows)
CREATE TABLE raw_page_events (
    event_id INTEGER,
    user_id INTEGER,
    event_date DATE,
    event_type VARCHAR(20),
    page_url VARCHAR(200),
    duration_ms INTEGER
);

INSERT INTO raw_page_events
SELECT
    i AS event_id,
    (i % 10000) + 1 AS user_id,
    DATE '2023-01-01' + CAST(i % 365 AS INTEGER) AS event_date,
    CASE i % 3
        WHEN 0 THEN 'pageview'
        WHEN 1 THEN 'click'
        ELSE 'scroll'
    END AS event_type,
    '/page/' || (i % 100) AS page_url,
    (i % 5000) + 100 AS duration_ms
FROM generate_series(1, 200000) AS t(i);

-- ============================================================
-- Approach 1: Compute on the fly (expensive for dashboards)
-- ============================================================
EXPLAIN ANALYZE
SELECT
    event_date,
    event_type,
    COUNT(*) AS event_count,
    COUNT(DISTINCT user_id) AS unique_users,
    AVG(duration_ms) AS avg_duration_ms
FROM raw_page_events
WHERE event_date >= DATE '2023-06-01'
  AND event_date < DATE '2023-07-01'
GROUP BY event_date, event_type
ORDER BY event_date, event_type;

-- ============================================================
-- Approach 2: Materialize the aggregation as a table
-- ============================================================

-- "Refresh" the materialized view: full rebuild
CREATE OR REPLACE TABLE daily_event_summary AS
SELECT
    event_date,
    event_type,
    COUNT(*) AS event_count,
    COUNT(DISTINCT user_id) AS unique_users,
    ROUND(AVG(duration_ms), 2) AS avg_duration_ms
FROM raw_page_events
GROUP BY event_date, event_type;

-- Query the materialized table (fast: reads pre-computed aggregates)
EXPLAIN ANALYZE
SELECT *
FROM daily_event_summary
WHERE event_date >= DATE '2023-06-01'
  AND event_date < DATE '2023-07-01'
ORDER BY event_date, event_type;

-- ============================================================
-- Approach 3: Incremental refresh (append only new data)
-- ============================================================

-- Simulate new data arriving for a specific date
INSERT INTO raw_page_events
SELECT
    200000 + i AS event_id,
    (i % 500) + 1 AS user_id,
    DATE '2024-01-15' AS event_date,
    CASE i % 3
        WHEN 0 THEN 'pageview'
        WHEN 1 THEN 'click'
        ELSE 'scroll'
    END AS event_type,
    '/page/' || (i % 20) AS page_url,
    (i % 3000) + 200 AS duration_ms
FROM generate_series(1, 1000) AS t(i);

-- Incremental refresh: only recompute the new date
DELETE FROM daily_event_summary WHERE event_date = DATE '2024-01-15';

INSERT INTO daily_event_summary
SELECT
    event_date,
    event_type,
    COUNT(*) AS event_count,
    COUNT(DISTINCT user_id) AS unique_users,
    ROUND(AVG(duration_ms), 2) AS avg_duration_ms
FROM raw_page_events
WHERE event_date = DATE '2024-01-15'
GROUP BY event_date, event_type;
