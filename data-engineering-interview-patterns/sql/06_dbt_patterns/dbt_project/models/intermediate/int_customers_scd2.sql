-- Intermediate: SCD Type 2 dimension for customers
-- Tracks address changes over time with effective/expiry dates
-- Connection: sql/01_window_functions/de_scenarios/change_detection

with source as (
    select * from {{ ref('raw_customer_history') }}
),

with_row_number as (
    select
        *,
        row_number() over (
            partition by customer_id
            order by effective_date
        ) as version_number,
        lead(effective_date) over (
            partition by customer_id
            order by effective_date
        ) as next_effective_date
    from source
),

scd2 as (
    select
        customer_id,
        name as customer_name,
        email,
        city,
        state,
        effective_date,
        coalesce(
            next_effective_date - interval '1' day,
            cast('9999-12-31' as date)
        ) as expiry_date,
        case
            when next_effective_date is null then true
            else false
        end as is_current,
        version_number
    from with_row_number
)

select * from scd2
