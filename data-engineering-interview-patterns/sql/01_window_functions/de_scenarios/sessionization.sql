/*
Sessionization with Window Functions

Detect user sessions from clickstream data by identifying idle gaps.
A new session starts when the time gap between events exceeds a threshold.

Scenario: web clickstream events with a 30-minute idle timeout.
*/

-- Create sample data
CREATE TABLE clickstream (
    event_id INTEGER,
    user_id INTEGER,
    event_time TIMESTAMP,
    page VARCHAR(100)
);

INSERT INTO clickstream VALUES
    (1,  1, '2024-01-15 10:00:00', '/home'),
    (2,  1, '2024-01-15 10:05:00', '/products'),
    (3,  1, '2024-01-15 10:12:00', '/products/123'),
    (4,  1, '2024-01-15 10:15:00', '/cart'),
    -- 2 hour gap -> new session
    (5,  1, '2024-01-15 12:00:00', '/home'),
    (6,  1, '2024-01-15 12:10:00', '/account'),
    -- Different user
    (7,  2, '2024-01-15 09:00:00', '/home'),
    (8,  2, '2024-01-15 09:20:00', '/search'),
    -- 45 min gap -> new session
    (9,  2, '2024-01-15 10:05:00', '/home'),
    (10, 2, '2024-01-15 10:08:00', '/products');

-- Step 1: Compute time gap from previous event per user
-- Step 2: Flag new sessions when gap > 30 minutes
-- Step 3: Running sum of flags = session counter
WITH with_gaps AS (
    SELECT *,
           LAG(event_time) OVER (
               PARTITION BY user_id ORDER BY event_time
           ) AS prev_event_time,
           EXTRACT(EPOCH FROM (
               event_time - LAG(event_time) OVER (
                   PARTITION BY user_id ORDER BY event_time
               )
           )) / 60.0 AS gap_minutes
    FROM clickstream
),
with_flags AS (
    SELECT *,
           CASE
               WHEN gap_minutes IS NULL THEN 1  -- first event
               WHEN gap_minutes > 30 THEN 1     -- idle timeout
               ELSE 0
           END AS new_session_flag
    FROM with_gaps
)
SELECT
    user_id,
    event_time,
    page,
    ROUND(gap_minutes, 1) AS gap_minutes,
    new_session_flag,
    SUM(new_session_flag) OVER (
        PARTITION BY user_id ORDER BY event_time
    ) AS session_id
FROM with_flags
ORDER BY user_id, event_time;
