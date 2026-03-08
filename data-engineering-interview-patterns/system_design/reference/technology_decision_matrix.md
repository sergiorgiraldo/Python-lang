# Technology Decision Matrix

These matrices help you quickly justify technology choices in an interview.
Do not memorize specific entries. Understand the criteria so you can reason
about any technology comparison. The goal is to say "I chose X because of
[criterion]" not "I read that X is the best."

## Matrix 1: Message Broker Selection

| Criterion | Kafka | Kinesis | Pub/Sub | SQS |
|---|---|---|---|---|
| Throughput | Very high (1M/sec/partition) | Moderate (1K/sec/shard) | High (auto-scales) | High (batched) |
| Latency | Low (2-10ms) | Moderate (200ms+) | Low (10-100ms) | Low-moderate |
| Ordering | Per partition | Per shard | Per ordering key | FIFO queues |
| Replay | Yes (configurable retention) | Yes (24h-7d) | Yes (7d+) | No |
| Ops overhead | High (manage clusters) | Low (serverless) | Low (serverless) | Very low |
| Cost model | Broker instances | Per shard-hour | Per message | Per message |
| Multi-consumer | Yes (consumer groups) | Yes (fan-out) | Yes (subscriptions) | No (single consumer) |
| Best for | High throughput, replay, multi-consumer | AWS-native, moderate scale | GCP-native, auto-scale | Simple queuing, decoupling |

**When to pick each:**

- **Kafka:** High throughput (50K+ events/sec), need replay, multiple
  consumers reading the same stream, team can manage clusters (or use MSK)
- **Kinesis:** AWS-native shop, moderate throughput (<10K records/sec per
  shard), want managed with no cluster ops
- **Pub/Sub:** GCP-native shop, want auto-scaling with no partition management,
  variable/bursty traffic
- **SQS:** Simple task queue, no replay needed, decoupling services. Not a
  streaming platform.

## Matrix 2: Processing Engine Selection

| Criterion | Spark | Flink | dbt | Airflow + Python |
|---|---|---|---|---|
| Batch | Excellent | Good | SQL only | Good (small scale) |
| Streaming | Good (micro-batch) | Excellent (true streaming) | No | No |
| Latency | Minutes | Milliseconds to seconds | Minutes | Minutes to hours |
| Language | Python/Scala/SQL | Java/Python/SQL | SQL + Jinja | Python |
| Scale | Petabyte | Petabyte | Warehouse-dependent | Single machine |
| ML support | MLlib, native DataFrame | Limited | No | Library-dependent |
| Ops complexity | High | High | Low | Moderate |
| Best for | Large batch, ML pipelines | Real-time event processing | SQL transforms in warehouse | Orchestration, glue code |

**When to pick each:**

- **Spark:** Batch processing over 100 GB, ML feature engineering, need
  Python/Scala flexibility beyond SQL
- **Flink:** Sub-second latency requirements, complex event processing,
  stateful streaming with exactly-once
- **dbt:** SQL transformations inside a warehouse, team is SQL-fluent,
  want built-in testing and documentation
- **Airflow + Python:** Orchestrating tasks across systems, lightweight
  transforms, connecting APIs to storage

## Matrix 3: Warehouse and Lakehouse Selection

| Criterion | BigQuery | Snowflake | Databricks | Redshift |
|---|---|---|---|---|
| Pricing | Per-query or flat-rate | Credit-based | DBU-based | Node-based |
| Serverless | Yes (default) | Yes (option) | Yes (SQL warehouse) | Serverless option |
| Auto-scale | Yes | Yes (multi-cluster) | Yes | Limited |
| Streaming ingest | Limited | Snowpipe (micro-batch) | Structured Streaming | Kinesis integration |
| Semi-structured | JSON native, nested | VARIANT type | Delta Lake native | JSON via Spectrum |
| ML integration | BigQuery ML, Vertex AI | Snowpark, Cortex | MLflow, native notebooks | SageMaker |
| Open formats | BigLake (external) | Iceberg support | Delta Lake native | Spectrum (external) |
| Best for | GCP shops, ad-hoc analytics | Multi-cloud, broad SQL needs | Heavy Spark/ML workloads | AWS-native, existing users |

**When to pick each:**

- **BigQuery:** GCP-first company, heavy ad-hoc analytics, want serverless
  with zero management. On-demand pricing suits variable workloads.
- **Snowflake:** Multi-cloud or cloud-agnostic, strong SQL culture,
  need data sharing across organizations. Credit model suits predictable
  workloads.
- **Databricks:** Heavy ML/data science workloads alongside analytics,
  already using Spark, want a unified lakehouse platform.
- **Redshift:** Deep AWS investment, existing Redshift workloads, cost
  optimization through reserved instances.

## Matrix 4: Storage Format Selection

| Criterion | Parquet | ORC | Delta Lake | Iceberg | Avro |
|---|---|---|---|---|---|
| Layout | Columnar | Columnar | Columnar (Parquet) | Columnar (Parquet/ORC) | Row-based |
| ACID transactions | No | No | Yes | Yes | No |
| Schema evolution | Add columns | Add columns | Full (merge schema) | Full | Full |
| Time travel | No | No | Yes | Yes | No |
| Compaction | Manual | Manual | OPTIMIZE command | rewrite_data_files | N/A |
| Engine support | Universal | Hive/Spark | Spark, Trino, some | Spark, Trino, Athena, many | Universal |
| Best for | General analytics | Hive ecosystem | Databricks lakehouse | Multi-engine open lakehouse | Streaming, schema registry |

**When to pick each:**

- **Parquet:** Default for analytical storage. Works everywhere. Use unless
  you need ACID or time travel.
- **Delta Lake:** Databricks environment, need ACID transactions and time
  travel. Strong Spark integration.
- **Iceberg:** Multi-engine environment (Athena + Spark + Trino), want open
  standard with no vendor lock-in. Broadest engine support of the table
  formats.
- **Avro:** Streaming data with schema registry (Kafka). Row-oriented, good
  for write-heavy ingestion and schema evolution.
- **ORC:** Hive-centric environments. Parquet has largely replaced ORC in
  new designs.

## Matrix 5: Orchestration Selection

| Criterion | Airflow | Dagster | Prefect | dbt Cloud | Step Functions |
|---|---|---|---|---|---|
| DAG model | Task-based | Asset-based | Flow-based | SQL lineage | State machine |
| Language | Python | Python | Python | SQL + Jinja | JSON/YAML |
| Self-hosted | Yes | Yes | Yes | No | No (AWS) |
| Managed option | MWAA, Astronomer | Dagster Cloud | Prefect Cloud | Managed | AWS native |
| Data quality | External (GE, custom) | Built-in asset checks | External | Built-in tests | External |
| Backfill | Manual date range | Native asset backfill | Manual | dbt build --full-refresh | N/A |
| Community | Very large | Growing | Growing | Large (SQL users) | AWS docs |
| Best for | Complex pipelines, large teams | Data-asset-centric orgs | Simple to moderate flows | SQL-only transforms | AWS-native event-driven |

**When to pick each:**

- **Airflow:** Complex dependencies across many systems, large team with
  Python skills, need maximum flexibility. Industry standard.
- **Dagster:** Asset-centric thinking (focus on data products rather than
  tasks), strong software engineering practices, want built-in observability.
- **Prefect:** Simpler workflow needs, want Python-native with less
  boilerplate than Airflow, moderate complexity.
- **dbt Cloud:** SQL-only transformations inside a warehouse, want managed
  scheduling with built-in testing and docs.
- **Step Functions:** AWS-native event-driven pipelines, Lambda-based
  processing, no Python orchestration needed.

## How to Use in an Interview

Do not just name a technology. Justify it against a requirement using the
tradeoff framework from `foundations/tradeoff_framework.md`:

**Weak answer:** "I would use Kafka."

**Strong answer:** "For our throughput requirement of 50K events/sec with
multi-consumer replay capability, Kafka is the right fit. If we were purely
on AWS with a small team wanting less ops overhead, Kinesis would work at
this throughput level. But Kafka's partition-level ordering and configurable
retention give us more flexibility for our event-sourcing pattern."

The matrix gives you the criteria. The tradeoff framework gives you the
structure. Together, they produce design decisions that interviewers find
compelling.
