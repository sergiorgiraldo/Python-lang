-- Staging model: raw events -> typed, deduplicated
-- Uses ROW_NUMBER for dedup (the most common dbt staging pattern)
-- Connection: sql/01_window_functions/de_scenarios/dedup_with_row_number

with source as (
    select * from {{ ref('raw_events') }}
),

deduplicated as (
    select
        *,
        row_number() over (
            partition by event_id
            order by event_timestamp desc
        ) as _row_num
    from source
),

staged as (
    select
        cast(event_id as integer)       as event_id,
        cast(user_id as integer)        as user_id,
        lower(trim(event_type))         as event_type,
        cast(event_timestamp as timestamp) as event_timestamp,
        trim(page_url)                  as page_url
    from deduplicated
    where _row_num = 1
)

select * from staged
