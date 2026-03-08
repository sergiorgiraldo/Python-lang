# Patterns Mapping

Every model in this dbt project implements a pattern from the SQL section. This mapping shows the connection so you can study the raw SQL pattern first, then see how it looks in production dbt code.

## Model-to-Pattern Mapping

| dbt Model | Layer | SQL Pattern | Source |
|---|---|---|---|
| stg_orders | staging | Type casting, column selection, SELECT * avoidance | sql/05 anti_patterns |
| stg_customers | staging | Data cleaning (trim, lower) | Basic SQL |
| stg_events | staging | ROW_NUMBER dedup | sql/01 dedup DE scenario |
| int_deduped_events | intermediate | LAG + gap detection for sessionization | sql/01 sessionization DE scenario |
| int_customer_orders | intermediate | LEFT JOIN + conditional aggregation | sql/02 joins + sql/03 aggregations |
| int_customers_scd2 | intermediate | LEAD + ROW_NUMBER for SCD Type 2 | sql/01 change detection DE scenario |
| fct_orders | mart | Star schema fact table, incremental merge | sql/02 merge_upsert DE scenario |
| rpt_daily_revenue | mart | GROUP BY + conditional agg + running total | sql/03 conditional_aggregation + sql/01 running_totals |
| rpt_customer_cohorts | mart | DATE_TRUNC + multi-level aggregation | sql/03 aggregations |

## Macro-to-Pattern Mapping

| Macro | Pattern | Source |
|---|---|---|
| dedup_by_key | Generic ROW_NUMBER dedup | sql/01 dedup DE scenario |
| generate_surrogate_key | Deterministic key generation (MD5 hash) | Common DE pattern |
| incremental_merge | MERGE/upsert for incremental loads | sql/02 merge_upsert DE scenario |

## What This Demonstrates in an Interview

When asked "how would you build this in production?", you can walk from the SQL pattern (which you've just solved on the whiteboard) to the dbt implementation:

1. "I'd structure this as a staging model that cleans the raw data"
2. "Then an intermediate model that applies the business logic we just discussed"
3. "The mart is a pre-aggregated table optimized for the dashboard query pattern"
4. "For incremental loads, I'd use dbt's merge strategy with a watermark on the date column"

This progression shows you can go from algorithm to architecture.

## File Locations

For each model, the dbt version uses Jinja `{{ ref() }}` syntax and lives in `dbt_project/models/`. The testable plain-SQL version lives in `standalone/`:

| Layer | dbt Version | Standalone Version | Test File |
|---|---|---|---|
| staging | `dbt_project/models/staging/` | `standalone/staging_models.sql` | `standalone/staging_models_test.py` |
| intermediate | `dbt_project/models/intermediate/` | `standalone/intermediate_models.sql` | `standalone/intermediate_models_test.py` |
| marts | `dbt_project/models/marts/` | `standalone/mart_models.sql` | `standalone/mart_models_test.py` |
