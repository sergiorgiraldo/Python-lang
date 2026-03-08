-- Intermediate: deduplicated events with session assignment
-- Builds on stg_events (already deduped by event_id)
-- Adds session boundaries using gap detection
-- Connection: sql/01_window_functions/de_scenarios/sessionization

with events as (
    select * from {{ ref('stg_events') }}
),

with_prev_timestamp as (
    select
        *,
        lag(event_timestamp) over (
            partition by user_id
            order by event_timestamp
        ) as prev_event_timestamp
    from events
),

with_session_boundary as (
    select
        *,
        case
            when prev_event_timestamp is null then 1
            when extract(epoch from event_timestamp - prev_event_timestamp) > 1800 then 1
            else 0
        end as is_new_session
    from with_prev_timestamp
),

with_session_id as (
    select
        event_id,
        user_id,
        event_type,
        event_timestamp,
        page_url,
        sum(is_new_session) over (
            partition by user_id
            order by event_timestamp
            rows unbounded preceding
        ) as session_number
    from with_session_boundary
)

select
    *,
    user_id || '-' || session_number as session_id
from with_session_id
