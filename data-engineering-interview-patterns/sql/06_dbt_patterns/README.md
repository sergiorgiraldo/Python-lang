# 06 - dbt Patterns

## What This Section Is

A mini dbt project showing how SQL interview patterns translate to production
transformation code. This is not a dbt tutorial (plenty of those exist). The
focus is on the patterns from sql/01-05 implemented as dbt models with proper
layering.

## Why dbt Knowledge Matters in DE Interviews

- Many companies use dbt as their transformation layer
- Interview questions often ask: "How would you build this in production?"
  The answer involves layering, testing and incremental strategies
- Knowing dbt conventions signals production experience, not just SQL
  puzzle-solving ability

## Structure

| Directory | Purpose | Maps to |
|---|---|---|
| dbt_project/models/staging/ | Raw to cleaned, typed, renamed | SQL basics, type casting |
| dbt_project/models/intermediate/ | Business logic, joins, dedup | sql/01 window functions, sql/02 joins |
| dbt_project/models/marts/ | Final analytics tables | sql/03 aggregations, sql/05 optimization |
| dbt_project/macros/ | Reusable SQL patterns | Common DE patterns |
| standalone/ | Same SQL logic, testable without dbt | CI-friendly versions |

## The Medallion Pattern in dbt Terms

```
Bronze = staging/      -> 1:1 with source tables, minimal transformation
Silver = intermediate/ -> business logic, joins, dedup, type 2 dimensions
Gold   = marts/        -> aggregated, consumer-ready, optimized for queries
```

## How to Read This Section

1. Look at the dbt_project/ for authentic structure and conventions
2. Look at standalone/ for the pure SQL logic (testable, no Jinja)
3. Read patterns_mapping.md to see how each model connects to earlier SQL patterns
4. Read interview_guide.md for dbt-specific interview questions

## Connection to Other Sections

Every model maps to a specific pattern from sql/01-05:

- The dedup model uses ROW_NUMBER from sql/01_window_functions
- The SCD Type 2 model uses LAG from sql/01_window_functions change detection scenario
- The incremental model uses the MERGE pattern from sql/02_joins
- The aggregation marts use patterns from sql/03_aggregations
