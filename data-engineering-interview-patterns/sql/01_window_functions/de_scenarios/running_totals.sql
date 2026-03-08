/*
Running Totals with Window Functions

Compute cumulative sums and running averages over ordered data.
Common in financial reporting, cumulative KPIs and running balances.

Scenario: daily revenue table where we need cumulative revenue
and running average revenue.
*/

-- Create sample data
CREATE TABLE daily_revenue (
    revenue_date DATE,
    revenue DECIMAL(10, 2)
);

INSERT INTO daily_revenue VALUES
    ('2024-01-01', 1000.00),
    ('2024-01-02', 1500.00),
    ('2024-01-03', 800.00),
    ('2024-01-04', 2200.00),
    ('2024-01-05', 1700.00),
    ('2024-01-06', 900.00),
    ('2024-01-07', 3100.00);

-- Running total and running average
SELECT
    revenue_date,
    revenue,
    SUM(revenue) OVER (
        ORDER BY revenue_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_revenue,
    ROUND(AVG(revenue) OVER (
        ORDER BY revenue_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ), 2) AS running_avg_revenue
FROM daily_revenue
ORDER BY revenue_date;
