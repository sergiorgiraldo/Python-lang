-- Staging model: raw customers -> typed, renamed
-- Connection: basic data cleaning, no complex patterns

with source as (
    select * from {{ ref('raw_customers') }}
),

staged as (
    select
        cast(customer_id as integer)    as customer_id,
        trim(name)                       as customer_name,
        lower(trim(email))              as email,
        trim(city)                       as city,
        trim(state)                      as state,
        cast(signup_date as date)       as signup_date
    from source
    where customer_id is not null
)

select * from staged
