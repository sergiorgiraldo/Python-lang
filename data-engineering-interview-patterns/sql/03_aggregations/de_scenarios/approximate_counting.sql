/*
Approximate Counting

Compare exact COUNT(DISTINCT) vs APPROX_COUNT_DISTINCT on a generated
dataset to show timing and accuracy trade-offs.

Uses DuckDB's generate_series to create a large dataset.
*/

-- Generate a dataset: 1M rows with ~100K distinct user_ids
CREATE TABLE page_views AS
SELECT
    (random() * 100000)::INTEGER AS user_id,
    DATE '2024-01-01' + INTERVAL (floor(random() * 365)::INTEGER) DAY AS view_date,
    CASE floor(random() * 5)::INTEGER
        WHEN 0 THEN 'home'
        WHEN 1 THEN 'product'
        WHEN 2 THEN 'cart'
        WHEN 3 THEN 'checkout'
        ELSE 'search'
    END AS page
FROM generate_series(1, 1000000) AS t(i);


-- Exact count
SELECT COUNT(DISTINCT user_id) AS exact_count
FROM page_views;


-- Approximate count using HyperLogLog
-- SELECT APPROX_COUNT_DISTINCT(user_id) AS approx_count
-- FROM page_views;


-- Compare both side by side
-- SELECT
--     COUNT(DISTINCT user_id) AS exact_count,
--     APPROX_COUNT_DISTINCT(user_id) AS approx_count,
--     ABS(COUNT(DISTINCT user_id) - APPROX_COUNT_DISTINCT(user_id)) AS absolute_error,
--     ROUND(
--         100.0 * ABS(COUNT(DISTINCT user_id) - APPROX_COUNT_DISTINCT(user_id))
--         / COUNT(DISTINCT user_id),
--         2
--     ) AS error_pct
-- FROM page_views;


-- Per-page comparison: approximate cardinality per group
-- SELECT
--     page,
--     COUNT(DISTINCT user_id) AS exact_unique_users,
--     APPROX_COUNT_DISTINCT(user_id) AS approx_unique_users
-- FROM page_views
-- GROUP BY page
-- ORDER BY page;
