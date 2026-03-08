/*
Deduplication with ROW_NUMBER

The most common window function pattern in production DE.
Given records with potential duplicates, keep only the latest
version of each logical entity.

Scenario: events table with duplicate records from at-least-once delivery.
Keep the most recent event per (user_id, event_type).
*/

-- Create sample data
CREATE TABLE raw_events (
    event_id INTEGER,
    user_id INTEGER,
    event_type VARCHAR(50),
    event_data VARCHAR(200),
    received_at TIMESTAMP
);

INSERT INTO raw_events VALUES
    (1, 100, 'purchase', '{"amount": 50}', '2024-01-15 10:00:00'),
    (2, 100, 'purchase', '{"amount": 50}', '2024-01-15 10:00:01'),  -- duplicate
    (3, 100, 'purchase', '{"amount": 50}', '2024-01-15 10:00:02'),  -- duplicate
    (4, 100, 'login', '{"device": "mobile"}', '2024-01-15 09:00:00'),
    (5, 200, 'purchase', '{"amount": 75}', '2024-01-15 11:00:00'),
    (6, 200, 'purchase', '{"amount": 75}', '2024-01-15 11:00:01');  -- duplicate

-- Deduplicated output
SELECT *
FROM (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY user_id, event_type
               ORDER BY received_at DESC
           ) AS rn
    FROM raw_events
) ranked
WHERE rn = 1
ORDER BY user_id, event_type;
