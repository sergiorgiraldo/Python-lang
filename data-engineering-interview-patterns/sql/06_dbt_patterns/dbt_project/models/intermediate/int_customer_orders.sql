-- Intermediate: customer order summary
-- Joins customers with their order aggregates
-- Connection: sql/02_joins (LEFT JOIN) + sql/03_aggregations (GROUP BY)

with customers as (
    select * from {{ ref('stg_customers') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

order_summary as (
    select
        customer_id,
        count(*) as total_orders,
        count(case when status = 'completed' then 1 end) as completed_orders,
        sum(case when status = 'completed' then line_total else 0 end) as total_revenue,
        min(order_date) as first_order_date,
        max(order_date) as last_order_date
    from orders
    group by customer_id
)

select
    c.customer_id,
    c.customer_name,
    c.email,
    c.city,
    c.state,
    c.signup_date,
    coalesce(o.total_orders, 0) as total_orders,
    coalesce(o.completed_orders, 0) as completed_orders,
    coalesce(o.total_revenue, 0) as total_revenue,
    o.first_order_date,
    o.last_order_date,
    case
        when o.total_orders is null then 'never_ordered'
        when o.last_order_date >= current_date - interval '30' day then 'active'
        when o.last_order_date >= current_date - interval '90' day then 'lapsing'
        else 'churned'
    end as customer_status
from customers c
left join order_summary o on c.customer_id = o.customer_id
