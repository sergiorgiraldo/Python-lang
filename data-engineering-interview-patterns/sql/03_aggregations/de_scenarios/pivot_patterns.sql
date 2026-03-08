/*
Pivot Patterns

Transform row-based data into columnar format (pivot) and back (unpivot).

Scenario: transform event-per-row data into user-feature columns for ML
feature engineering.
*/

-- Setup: user events in row format
CREATE TABLE user_events (
    user_id INTEGER,
    event_type VARCHAR(50),
    event_count INTEGER
);

INSERT INTO user_events VALUES
    (1, 'page_view', 120),
    (1, 'click', 45),
    (1, 'purchase', 3),
    (2, 'page_view', 80),
    (2, 'click', 20),
    (3, 'page_view', 200),
    (3, 'click', 90),
    (3, 'purchase', 12);


-- Approach 1: Manual pivot using conditional aggregation (works everywhere)
SELECT
    user_id,
    SUM(CASE WHEN event_type = 'page_view' THEN event_count ELSE 0 END) AS page_views,
    SUM(CASE WHEN event_type = 'click' THEN event_count ELSE 0 END) AS clicks,
    SUM(CASE WHEN event_type = 'purchase' THEN event_count ELSE 0 END) AS purchases
FROM user_events
GROUP BY user_id
ORDER BY user_id;


-- Approach 2: DuckDB PIVOT syntax
-- PIVOT user_events
-- ON event_type
-- USING SUM(event_count)
-- GROUP BY user_id
-- ORDER BY user_id;


-- Unpivot: columnar back to rows
-- Setup for unpivot demo
CREATE TABLE user_features (
    user_id INTEGER,
    page_views INTEGER,
    clicks INTEGER,
    purchases INTEGER
);

INSERT INTO user_features VALUES
    (1, 120, 45, 3),
    (2, 80, 20, 0),
    (3, 200, 90, 12);


-- Approach 3: Manual unpivot using UNION ALL (works everywhere)
SELECT user_id, 'page_view' AS event_type, page_views AS event_count
FROM user_features
UNION ALL
SELECT user_id, 'click', clicks
FROM user_features
UNION ALL
SELECT user_id, 'purchase', purchases
FROM user_features
ORDER BY user_id, event_type;


-- Approach 4: DuckDB UNPIVOT syntax
-- UNPIVOT user_features
-- ON page_views, clicks, purchases
-- INTO NAME event_type VALUE event_count;
