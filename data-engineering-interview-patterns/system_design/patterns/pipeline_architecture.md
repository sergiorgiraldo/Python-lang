# Pipeline Architecture

A data pipeline is more than ETL. It is a system that must handle failure,
scale with demand and maintain data quality over time. The architecture
patterns in this document cover orchestration, failure handling, backfill
strategies and testing. These are the operational concerns that separate a
prototype pipeline from a production one.

## Orchestration Patterns

### DAG-Based Orchestration

Define pipeline tasks and their dependencies as a directed acyclic graph
(DAG). The scheduler resolves execution order using topological sort and
runs tasks as their dependencies complete.

```
extract_users --+--> transform_users --+--> load_dim_users
                |                      |
extract_orders -+--> transform_orders -+--> load_fact_orders
                                       |
                                       +--> run_quality_checks
```

**Technologies:** Airflow, Dagster, Prefect.

**When to use:** Complex dependency chains, regular schedules (hourly, daily),
pipelines with 10-100+ tasks that need coordinated execution.

**Connection:** Airflow's scheduler uses topological sort internally to
determine execution order. The same algorithm appears in
[`patterns/06_graph_topological_sort/`](../../patterns/06_graph_topological_sort/README.md) for dependency resolution problems.

### Event-Driven Orchestration

Tasks trigger on events rather than schedules. A new file in S3 triggers a
Lambda function. A message in a queue triggers a processing step. No
scheduler, no DAG definition.

**Technologies:** AWS Lambda + Step Functions, GCP Cloud Functions +
Workflows, Azure Functions + Durable Functions.

**When to use:** Reactive pipelines where the trigger is an external event
(file arrival, webhook, message). Low-latency requirements where waiting
for the next scheduled run adds unacceptable delay.

**Tradeoff:** Simpler for linear workflows but harder to manage complex
dependencies. No built-in retry history, backfill support or cross-task
dependency resolution without additional tooling.

### Hybrid Orchestration

Scheduled orchestration triggers event-driven sub-pipelines. Airflow kicks
off a DAG on schedule. One task publishes a message that triggers a Lambda
chain. The DAG waits for a completion signal before continuing.

This combines the dependency management of DAG-based orchestration with the
reactivity of event-driven processing. Common in architectures that mix
batch and streaming components.

## Retry and Failure Handling

### Idempotency

Every task must be safe to re-run without duplicating data. This is the
single most important property of a production pipeline. If a task fails
halfway and restarts, the output should be identical to a clean run.

**Pattern: Staging and atomic swap.** Write results to a staging table or
temporary partition. After successful completion, swap the staging data
into the production table using MERGE or partition rename.

**Pattern: INSERT OVERWRITE.** Write to a partitioned table using INSERT
OVERWRITE for the target partition. Re-running the task overwrites the
same partition rather than appending duplicates.

**Pattern: Deduplication keys.** Every output row includes a deterministic
key (hash of business key + event timestamp). Downstream MERGE operations
use this key to upsert, making repeated writes safe.

### Retry Strategies

| Failure Type | Strategy | Example |
|---|---|---|
| Transient (network blip) | Immediate retry, 3 attempts | API timeout |
| Rate limit | Exponential backoff (1s, 2s, 4s, 8s) | 429 response |
| Persistent (bad data) | Dead letter queue, alert | Malformed record |
| Source down | Circuit breaker, alert, manual retry | Database offline |

### Partial Failure

When task 5 of 10 fails in a DAG:

- Tasks 1-4 completed successfully. If they are idempotent (and they should
  be), their outputs are valid and do not need re-running.
- Task 5 re-runs from scratch. Idempotency guarantees the re-run produces
  correct output.
- Tasks 6-10 run after task 5 succeeds.

Airflow handles this natively: failed tasks are retried and downstream tasks
wait. The key requirement is that every task is idempotent so partial re-runs
are safe.

### Circuit Breaker

If a source is consistently failing (5 consecutive failures, error rate above
50%), stop retrying and alert the on-call engineer. Continuing to pound a
failing source wastes resources and may worsen the upstream issue.

Implement with: retry count thresholds in Airflow, custom health-check tasks
that gate downstream execution, alerting on consecutive failure patterns.

## Backfill Patterns

Backfilling re-runs a pipeline for a historical date range. It is one of the
most common operational tasks and one of the easiest to get wrong.

### Requirements for Backfill

**Parameterized pipelines:** Every task accepts a date parameter (or date
range). No hardcoded `CURRENT_DATE - 1` or "yesterday" logic.

**Idempotent writes:** Backfilling a date range must overwrite existing data
for those dates cleanly, not append duplicates.

**Partition-aware storage:** Data partitioned by date means backfilling
January only touches January's partitions. Without date partitioning,
backfilling requires reprocessing the entire table.

### Backfill Anti-Patterns

**Hardcoded dates:** A pipeline with `WHERE date = CURRENT_DATE - 1` cannot
backfill last month without modifying the code. Use parameterized templates.

**No idempotency:** Backfilling a week inserts 7 days of duplicate data
because the pipeline appends rather than overwrites.

**Ignoring rate limits:** Backfilling 90 days of API data at full speed
exhausts the rate limit and blocks production ingestion. Throttle backfills
or run them during off-peak hours.

### Backfill Gotchas

**Schema changes:** Historical data may have a different schema than current
data. A column added last month does not exist in last year's data.

**SCD dimensions:** Backfilling facts from 6 months ago against current
dimension values gives incorrect results. Use point-in-time dimension
lookups (SCD Type 2 with effective dates). See
[`system_design/patterns/data_modeling_patterns.md`](data_modeling_patterns.md) for SCD patterns.

**Source availability:** The source API may not have historical data, or the
database may have purged old records. Verify data availability before
starting a large backfill.

## Testing Patterns

### Unit Tests

Test individual transformations in isolation. Given input rows, assert
expected output rows. Works for both Python functions and SQL transforms.

**Python:** pytest with fixtures providing sample DataFrames. Test edge cases:
NULLs, empty inputs, boundary values. See [`patterns/`](../../patterns/) for examples of
thorough test coverage on algorithmic problems.

**SQL (dbt):** dbt tests assert properties of model outputs. Built-in tests
for uniqueness, not-null, accepted values and relationships. Custom tests
for business logic.

### Integration Tests

Test the pipeline end-to-end on sample data. Load a small test dataset,
run the full pipeline and assert properties of the final output.

**Tradeoff:** Slower than unit tests (minutes vs seconds) but catches issues
that unit tests miss: task ordering, partition handling, cross-task data
flow.

### Data Tests (Post-Deployment)

Assert properties of production output data after each pipeline run.

- **Row count:** within expected range (yesterday +/- 20%)
- **NULL rates:** per column, within threshold
- **Uniqueness:** primary key columns have no duplicates
- **Referential integrity:** every foreign key has a matching parent
- **Freshness:** data is not stale (max timestamp within SLA)

These are not tests you run before deployment. They run after every pipeline
execution as quality gates. See [`system_design/patterns/data_quality_patterns.md`](data_quality_patterns.md)
for the full data quality framework.

### Contract Tests

Assert that upstream data meets expected schema and quality before your
pipeline processes it. If the source changes a column name or type, the
contract test catches it before bad data enters your system.

Implement with: schema validation at ingestion (Avro schema registry, JSON
schema, custom assertions), column presence and type checks, sample data
validation.

## Monitoring and Alerting

### Pipeline Health

- **Did the DAG run successfully?** Binary pass/fail with alerting on failure.
- **How long did it take?** Track duration trends. A task that normally takes
  5 minutes but took 45 minutes signals a problem even if it succeeded.
- **Are tasks stuck?** Running tasks that exceed 2x their typical duration
  warrant investigation.

### Data Health

- **Row count trends:** Plot daily row counts. A sudden drop from 10M to 1M
  rows suggests a partial load, not a real decrease in activity.
- **NULL rate trends:** Track NULL percentage per column over time. A column
  that is normally 2% NULL jumping to 40% NULL signals a source issue.
- **Value distribution:** Monitor means, medians and percentiles for numeric
  columns. Drift beyond expected bounds triggers alerts.

### Freshness Monitoring

- **When was the last successful update?** The most critical metric for
  downstream consumers.
- **Is the data stale?** Compare the latest data timestamp to the current
  time. Alert if the gap exceeds the SLA.
- **SLA tracking:** "table X is updated by 6 AM" is a measurable SLA.
  Track compliance percentage over time (target: 99.5%+).

### Key Metrics Dashboard

| Metric | What It Tells You |
|---|---|
| Pipeline duration trend | Performance degradation |
| Row count trend | Partial loads or source changes |
| Failure rate (7-day rolling) | Pipeline reliability |
| Data delay (freshness) | SLA compliance |
| Task retry count | Transient vs persistent issues |

## Connection to Interview

When designing a pipeline in an interview, do not stop at "Airflow runs the
DAG." Address the operational concerns:

- "Each task is idempotent so retries are safe."
- "We partition by date for efficient backfills."
- "Data quality checks run after each stage."
- "We monitor pipeline duration, row counts and freshness."

These statements signal that you have operated pipelines in production, not
just built prototypes. Use the capacity estimation framework from
`foundations/capacity_estimation.md` to size the pipeline components and the
tradeoff framework from `foundations/tradeoff_framework.md` to justify your
orchestration choices.

Quantify your monitoring thresholds (e.g. "alert if duration exceeds 2x the
7-day average") and backfill capabilities (e.g. "we can reprocess 30 days
of data in under 2 hours using parameterized Airflow backfills"). Concrete
numbers distinguish a practiced engineer from someone reciting theory.
