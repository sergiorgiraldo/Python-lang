/*
Moving Averages with Window Functions

Compute rolling/moving averages to smooth noisy metrics.
Shows both ROWS and RANGE frame types and when each is appropriate.

Scenario: daily metric values where we want a 7-day moving average.
*/

-- Create sample data with some date gaps
CREATE TABLE daily_metrics (
    metric_date DATE,
    value DECIMAL(10, 2)
);

INSERT INTO daily_metrics VALUES
    ('2024-01-01', 100),
    ('2024-01-02', 120),
    ('2024-01-03', 95),
    ('2024-01-04', 140),
    ('2024-01-05', 110),
    ('2024-01-06', 130),
    ('2024-01-07', 125),
    ('2024-01-08', 150),
    ('2024-01-09', 135),
    ('2024-01-10', 160),
    -- Gap: Jan 11-12 missing
    ('2024-01-13', 170),
    ('2024-01-14', 145);

-- ROWS-based: always looks back exactly 6 physical rows
-- This counts rows regardless of date gaps
SELECT
    metric_date,
    value,
    ROUND(AVG(value) OVER (
        ORDER BY metric_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 2) AS moving_avg_rows
FROM daily_metrics
ORDER BY metric_date;

-- RANGE-based: looks back by logical date value
-- This only includes rows within the date range (handles gaps correctly)
SELECT
    metric_date,
    value,
    ROUND(AVG(value) OVER (
        ORDER BY metric_date
        RANGE BETWEEN INTERVAL '6 days' PRECEDING AND CURRENT ROW
    ), 2) AS moving_avg_range
FROM daily_metrics
ORDER BY metric_date;
