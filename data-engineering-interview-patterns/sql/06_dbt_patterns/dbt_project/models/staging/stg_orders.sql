-- Staging model: raw orders -> typed, renamed, filtered
-- Materialized as: view (lightweight, always current)
-- Maps to: basic SQL type casting and column selection
-- Connection: sql/05_optimization_and_production anti-pattern #1 (avoid SELECT *)

with source as (
    select * from {{ ref('raw_orders') }}
),

staged as (
    select
        cast(order_id as integer)       as order_id,
        cast(customer_id as integer)    as customer_id,
        cast(product_id as integer)     as product_id,
        cast(quantity as integer)       as quantity,
        cast(unit_price as decimal(10,2)) as unit_price,
        cast(order_date as date)        as order_date,
        lower(trim(status))             as status,

        -- Derived columns
        cast(quantity as decimal(10,2)) * cast(unit_price as decimal(10,2)) as line_total
    from source
    where order_id is not null
)

select * from staged
