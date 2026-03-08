/*
Change Detection with Window Functions

Use LAG to compare each row with the previous and detect value changes.
Core technique for SCD Type 2 detection, audit trails and state transitions.

Scenario: user status history where we want to detect status transitions.
*/

-- Create sample data
CREATE TABLE user_status_log (
    log_id INTEGER,
    user_id INTEGER,
    status VARCHAR(20),
    recorded_at TIMESTAMP
);

INSERT INTO user_status_log VALUES
    (1, 100, 'active',   '2024-01-01 00:00:00'),
    (2, 100, 'active',   '2024-02-01 00:00:00'),  -- no change
    (3, 100, 'inactive', '2024-03-01 00:00:00'),  -- changed
    (4, 100, 'inactive', '2024-04-01 00:00:00'),  -- no change
    (5, 100, 'churned',  '2024-05-01 00:00:00'),  -- changed
    (6, 200, 'active',   '2024-01-01 00:00:00'),
    (7, 200, 'active',   '2024-02-01 00:00:00'),  -- no change
    (8, 200, 'churned',  '2024-03-01 00:00:00');  -- changed

-- Detect changes: flag rows where status differs from previous
WITH with_prev AS (
    SELECT *,
           LAG(status) OVER (
               PARTITION BY user_id ORDER BY recorded_at
           ) AS prev_status
    FROM user_status_log
)
SELECT
    log_id,
    user_id,
    prev_status,
    status AS new_status,
    recorded_at,
    CASE
        WHEN prev_status IS NULL THEN 'initial'
        WHEN prev_status != status THEN 'changed'
        ELSE 'unchanged'
    END AS change_type
FROM with_prev
ORDER BY user_id, recorded_at;

-- SCD Type 2 style: create validity ranges for each status period
-- Each row gets a valid_from and valid_to range
WITH with_prev AS (
    SELECT *,
           LAG(status) OVER (
               PARTITION BY user_id ORDER BY recorded_at
           ) AS prev_status
    FROM user_status_log
),
changes_only AS (
    SELECT user_id, status, recorded_at
    FROM with_prev
    WHERE prev_status IS NULL OR prev_status != status
)
SELECT
    user_id,
    status,
    recorded_at AS valid_from,
    LEAD(recorded_at) OVER (
        PARTITION BY user_id ORDER BY recorded_at
    ) AS valid_to  -- NULL means current
FROM changes_only
ORDER BY user_id, valid_from;
