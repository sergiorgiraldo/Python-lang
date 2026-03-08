-- Helper for incremental merge logic
-- Documents the pattern even though dbt handles this internally
-- Connection: sql/02_joins/de_scenarios/merge_upsert

{#
This macro is primarily for documentation purposes.
dbt handles incremental merge logic when you set:
  materialized='incremental'
  unique_key='your_key'
  incremental_strategy='merge'

Under the hood, dbt generates:
  MERGE INTO target USING (new_data) ON target.key = new_data.key
  WHEN MATCHED THEN UPDATE SET ...
  WHEN NOT MATCHED THEN INSERT ...

The key decisions for incremental models:
  1. unique_key: what makes a row unique (used for MERGE ON clause)
  2. incremental_strategy: 'merge' (upsert), 'append' (insert only),
     'delete+insert' (replace matching keys)
  3. The is_incremental() filter: what data to process on incremental runs
     (typically: WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }}))
#}

{% macro document_incremental_strategies() %}
{# This macro is documentation-only, not executable #}
{% endmacro %}
