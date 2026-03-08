-- Mart: customer cohort analysis
-- Groups customers by signup month, tracks order behavior
-- Connection: sql/01_window_functions (MIN for first event)
-- Connection: sql/03_aggregations (multi-level aggregation)

with customers as (
    select * from {{ ref('int_customer_orders') }}
),

cohorts as (
    select
        date_trunc('month', signup_date) as cohort_month,
        count(*) as cohort_size,
        count(case when total_orders > 0 then 1 end) as customers_with_orders,
        sum(total_revenue) as cohort_revenue,
        avg(total_orders) as avg_orders_per_customer,
        avg(total_revenue) as avg_revenue_per_customer
    from customers
    group by date_trunc('month', signup_date)
)

select
    *,
    round(100.0 * customers_with_orders / cohort_size, 1) as conversion_rate_pct
from cohorts
