# dbt Interview Guide

dbt questions appear in two contexts: dedicated "dbt round" interviews at companies that use it, and as part of broader "how would you build this?" system design discussions. This guide covers both.

## Section 1: Questions About dbt Fundamentals

### Q: "What is dbt and why would you use it?"

dbt is a SQL-first transformation tool that applies software engineering practices (version control, testing, documentation, CI/CD) to data transformations. You'd use it when your transformation logic is SQL-based and you want a structured framework for managing models, tests and documentation. It replaces ad-hoc SQL scripts and stored procedures with a maintainable, testable project.

Key point: dbt is the T in ELT. It does not extract or load data. It transforms data that is already in your warehouse.

### Q: "Explain dbt's materializations and when to use each."

- **view**: SQL is re-executed on every query. Use for lightweight transformations, staging models or when you always want current data. No storage cost but slower reads.
- **table**: SQL is executed once and results stored. Use for complex transformations or frequently queried models. Faster reads but stale between runs.
- **incremental**: Only new/changed rows are processed. Use for large fact tables where full refresh is too expensive. Requires a unique_key and a filter condition (usually timestamp-based).
- **ephemeral**: CTE injected into downstream models, never materialized. Use for simple helper transformations reused by multiple models.

Decision framework: staging = view (cheap, always current). Intermediate = table (complex, queried by multiple marts). Marts = table or incremental (consumer-facing, needs to be fast).

See `dbt_project/dbt_project.yml` for how these are configured at the directory level.

### Q: "How does dbt handle incremental models?"

On the first run, dbt builds the full table. On subsequent runs, the `is_incremental()` flag is true, and dbt only processes rows matching the incremental filter (e.g., `WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})`). The merge strategy determines how new rows are combined with existing ones: merge (upsert), append (insert only) or delete+insert (replace matching keys).

See `dbt_project/models/marts/fct_orders.sql` for an example of an incremental fact table.

### Q: "What testing strategies do you use in dbt?"

Layered approach matching the data quality dimensions:

- **Schema tests**: unique, not_null, accepted_values, relationships (on every model). See `dbt_project/models/staging/schema.yml` for examples.
- **Custom data tests**: SQL queries that should return zero rows (e.g., "orders with negative amounts"). Live in the `tests/` directory.
- **Source freshness tests**: assert that source data was updated recently.
- **dbt_expectations package**: statistical tests, row count bounds, column value ranges.

---

## Section 2: Questions About dbt Project Structure

### Q: "How do you organize a dbt project?"

Three layers matching the medallion architecture:

- **staging/**: one model per source table, 1:1 mapping, minimal transformation (cast, rename, filter nulls). Materialized as views.
- **intermediate/**: business logic, joins, dedup, enrichment. Models can reference other intermediate models. Materialized as tables.
- **marts/**: consumer-ready tables organized by business domain (finance, marketing, product). Optimized for query patterns. Materialized as tables or incremental.

Naming conventions: `stg_[source]_[entity]`, `int_[entity]_[verb]`, `fct_[entity]` or `dim_[entity]` for marts.

This is exactly the structure used in `dbt_project/models/`.

### Q: "How do you handle slowly changing dimensions in dbt?"

Depends on the type:

- **Type 1 (overwrite)**: standard incremental model with merge strategy. The new row simply replaces the old one.
- **Type 2 (history)**: use dbt snapshots or build a custom model with effective_date/expiry_date/is_current columns. The model tracks each version as a separate row with the valid date range.

Decision: use Type 2 when you need to answer "what did this customer's address look like on January 15th?" Use Type 1 when you only need the current value.

See `dbt_project/models/intermediate/int_customers_scd2.sql` for a Type 2 implementation.

### Q: "What's the difference between sources and refs?"

`{{ source('schema', 'table') }}` references raw tables owned by other systems (your databases, API exports). dbt does not manage these tables. `{{ ref('model_name') }}` references other dbt models. dbt uses refs to build the dependency graph and determine execution order. Always use sources for external data and refs for internal models. This distinction lets dbt detect when source schemas change and alert you.

---

## Section 3: Questions About Production dbt

### Q: "How do you handle data quality in a dbt pipeline?"

Three levels:

1. **Source quality**: freshness tests + schema expectations on raw data
2. **Transformation quality**: schema tests (unique, not_null) + custom data tests on every model
3. **Output quality**: row count checks, cross-model reconciliation (sum of detail = header total)

Severity levels: warn (log but continue) for non-critical tests, error (halt pipeline) for critical tests. Run `dbt test` after `dbt run` in the CI pipeline.

### Q: "How do you debug a dbt model that's producing wrong results?"

Work backward from the mart to staging:

1. Query the mart to confirm the wrong output
2. Query the intermediate model to see if the error is in the mart logic or upstream
3. Query the staging model to check if raw data is correct
4. If all upstream models are correct, the bug is in the current model's SQL

This is why the layered architecture matters: each layer is independently queryable and testable. The CTE structure within each model helps too. You can query individual CTEs to isolate the issue.

### Q: "How would you migrate from stored procedures to dbt?"

1. Map each stored procedure to a dbt model (usually intermediate or mart)
2. Start with staging models that replicate the current source tables
3. Rebuild the SP logic as SQL SELECTs (no INSERT/UPDATE/DELETE since dbt handles materialization)
4. Add tests that verify output matches the stored procedure's output
5. Run in parallel: both the SP and dbt produce output, compare daily
6. Cut over when confident

---

## Section 4: Common Mistakes in dbt Interviews

- Saying "dbt is an ETL tool" (it is the T only, not E or L)
- Not knowing the difference between materializations
- Not mentioning testing as a core feature
- Describing dbt models with INSERT statements (dbt generates the DDL/DML)
- Not knowing about incremental strategies
- Not connecting dbt to the broader data stack (orchestration, ingestion, BI)

---

## How to Practice

1. Walk through the models in `dbt_project/` and explain each layer out loud
2. For each model, explain: why this materialization? What tests would you add? What happens at scale?
3. Open `standalone/` and trace the SQL pattern back to the source in sql/01-05
4. Read `patterns_mapping.md` to rehearse the "whiteboard to production" narrative
5. Practice the "how would you build this?" answer: staging -> intermediate -> mart -> incremental
