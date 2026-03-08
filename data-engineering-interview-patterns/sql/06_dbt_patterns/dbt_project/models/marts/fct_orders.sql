-- Mart: fact table for orders
-- Grain: one row per order
-- Joins order data with customer and product dimensions
-- Connection: star schema pattern from system_design/patterns/data_modeling_patterns

{{
    config(
        materialized='incremental',
        unique_key='order_id'
    )
}}

with orders as (
    select * from {{ ref('stg_orders') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
)

select
    o.order_id,
    o.customer_id,
    c.customer_name,
    c.city as customer_city,
    c.state as customer_state,
    o.product_id,
    o.quantity,
    o.unit_price,
    o.line_total,
    o.order_date,
    o.status,
    -- Date dimension keys
    extract(year from o.order_date) as order_year,
    extract(month from o.order_date) as order_month,
    extract(dow from o.order_date) as order_day_of_week
from orders o
left join customers c on o.customer_id = c.customer_id

{% if is_incremental() %}
    where o.order_date > (select max(order_date) from {{ this }})
{% endif %}
