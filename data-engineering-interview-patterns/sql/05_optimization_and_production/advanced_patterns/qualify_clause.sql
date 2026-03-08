/*
QUALIFY: filter rows after window function evaluation.
Avoids the subquery wrapper needed in Postgres/MySQL.

Supported in: DuckDB, BigQuery, Snowflake, Databricks
Not supported in: Postgres, MySQL
*/

CREATE TABLE events (
    user_id INTEGER,
    event_type VARCHAR(20),
    event_time TIMESTAMP
);

INSERT INTO events VALUES
    (1, 'login', '2024-01-01 10:00:00'),
    (1, 'login', '2024-01-02 10:00:00'),
    (1, 'purchase', '2024-01-01 11:00:00'),
    (2, 'login', '2024-01-01 09:00:00'),
    (2, 'login', '2024-01-03 09:00:00');

-- Dedup: keep latest event per (user_id, event_type) using QUALIFY
SELECT user_id, event_type, event_time
FROM events
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY user_id, event_type
    ORDER BY event_time DESC
) = 1
ORDER BY user_id, event_type;

-- Without QUALIFY (needed in Postgres/MySQL):
-- SELECT user_id, event_type, event_time FROM (
--     SELECT *, ROW_NUMBER() OVER (
--         PARTITION BY user_id, event_type
--         ORDER BY event_time DESC
--     ) AS rn
--     FROM events
-- ) t WHERE rn = 1;
