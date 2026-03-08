-- Mart: daily revenue report
-- Pre-aggregated for dashboard performance
-- Connection: sql/03_aggregations (GROUP BY + conditional aggregation)
-- Connection: sql/05_optimization materialized views pattern

with orders as (
    select * from {{ ref('fct_orders') }}
    where status = 'completed'
),

daily_revenue as (
    select
        order_date,
        count(*) as order_count,
        count(distinct customer_id) as unique_customers,
        sum(line_total) as total_revenue,
        avg(line_total) as avg_order_value,
        sum(case when customer_state = 'OR' then line_total else 0 end) as revenue_oregon,
        sum(case when customer_state = 'WA' then line_total else 0 end) as revenue_washington,
        sum(case when customer_state = 'CA' then line_total else 0 end) as revenue_california
    from orders
    group by order_date
)

select
    *,
    sum(total_revenue) over (
        order by order_date
        rows unbounded preceding
    ) as cumulative_revenue
from daily_revenue
