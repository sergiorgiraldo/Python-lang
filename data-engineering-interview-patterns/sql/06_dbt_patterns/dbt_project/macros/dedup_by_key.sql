-- Generic dedup macro using ROW_NUMBER
-- Usage: {{ dedup_by_key(ref('raw_events'), 'event_id', 'event_timestamp desc') }}
-- Connection: sql/01_window_functions/de_scenarios/dedup_with_row_number

{% macro dedup_by_key(source_table, partition_key, order_by_clause) %}

with ranked as (
    select
        *,
        row_number() over (
            partition by {{ partition_key }}
            order by {{ order_by_clause }}
        ) as _dedup_rank
    from {{ source_table }}
)
select * from ranked where _dedup_rank = 1

{% endmacro %}
