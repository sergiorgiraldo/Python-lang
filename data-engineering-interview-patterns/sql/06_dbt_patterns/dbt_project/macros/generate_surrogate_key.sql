-- Generate a deterministic surrogate key from one or more columns
-- Usage: {{ generate_surrogate_key(['customer_id', 'effective_date']) }}
-- In production, use dbt_utils.generate_surrogate_key instead

{% macro generate_surrogate_key(columns) %}
    md5(concat_ws('|', {% for col in columns %}cast({{ col }} as varchar){% if not loop.last %}, {% endif %}{% endfor %}))
{% endmacro %}
