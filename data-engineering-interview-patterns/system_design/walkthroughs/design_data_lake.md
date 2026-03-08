# Walkthrough: Design a Data Lake Architecture

**Prompt:** "Design a data lake architecture for a company transitioning from
on-premise to cloud."

This walkthrough simulates a full 45-minute system design interview. Cloud
migrations are a common interview topic because they involve technology
selection, migration strategy, cost analysis and organizational change. The
interviewer wants to see that you can plan a migration, not just design a
greenfield system.

---

## Phase 1: Clarify Requirements (Minutes 0-5)

### Questions to Ask

**Current state:**
- "What's the existing infrastructure? Database platform, ETL tool, storage?"
- "How much data exists today? What's the growth rate?"
- "How many people interact with the data platform? Engineers, analysts,
  data scientists?"

**Target state:**
- "Is there a preferred cloud provider, or are we evaluating options?"
- "What workloads need to be supported? BI, ML, operational reporting?"
- "Are there multi-cloud or hybrid requirements?"

**Constraints:**
- "What's the migration timeline?"
- "Can we tolerate downtime during migration, or does it need to be seamless?"
- "Are there regulatory or data residency constraints?"

### Establishing Requirements

"Here's my understanding of the current and target state:

**Current state:**
- Oracle database: 50 TB, transactional and analytical workloads on the same
  instance
- Informatica ETL: ~200 transformation jobs running nightly
- On-premise Hadoop cluster: 100 TB raw data in HDFS, Hive for SQL queries
- Team: 5 data engineers, 10 analysts, 3 data scientists

**Target state:**
- Cloud-based (I'll assume AWS since you mentioned S3 earlier, but the
  architecture is similar on GCP)
- Support analytics (SQL queries), ML (Python, Spark) and operational
  reporting (dashboards)
- Data volume: 50 TB current warehouse + 100 TB Hadoop = 150 TB total,
  growing ~2 TB/month

**Constraints:**
- 6-month migration timeline
- Minimal downtime (parallel run, then cutover)
- Financial data has 7-year retention requirement

**Cost context:**
- On-premise costs: Oracle licensing (~$50K-100K/year), server hardware
  depreciation, Hadoop cluster maintenance, Informatica licensing. Total
  estimated: $200K-400K/year.
- Cloud target: we need to show this migration saves money or enables
  capabilities that justify the cost."

---

## Phase 2: High-Level Design (Minutes 5-10)

### Architecture

```
Oracle DB ──▶ DMS/CDC  ──┐
Hadoop    ──▶ distcp   ──┼──▶ S3 Lake [Bronze│Silver│Gold] ──▶ Snowflake (BI)
APIs      ──▶ Airflow  ──┘    (Delta/Iceberg format)       ──▶ Spark/EMR (ETL)
                                                           ──▶ SageMaker (ML)
```

### Component Justification

"**S3 as the storage foundation:** All data lives in S3 in open formats.
This decouples storage from compute and avoids lock-in to any single query
engine. At $0.023/GB/month for S3 Standard, 150 TB costs about $3,450/month
for storage. With lifecycle policies tiering older data to S3 Infrequent
Access ($0.0125/GB), the blended cost drops to roughly $2,500/month.

**Delta Lake or Apache Iceberg as the table format:** Provides ACID
transactions, time travel, schema evolution and efficient upserts on top of
Parquet files in S3. I'd choose Iceberg for its broader engine compatibility
(works with Spark, Trino, Athena, Snowflake) unless the team is already
invested in Databricks (then Delta Lake).

**Medallion architecture (Bronze/Silver/Gold):** Raw data preserved as-is in
Bronze. Cleaned and typed in Silver. Aggregated and business-ready in Gold.
Each layer serves different consumers. See
[`patterns/data_modeling_patterns.md`](../patterns/data_modeling_patterns.md) for the medallion pattern.

**Snowflake as the SQL engine:** Serves the BI team and analysts. Reads from
the curated Gold layer. Auto-suspend keeps costs low during off-hours.

**Spark on EMR for heavy processing:** Handles the Informatica job migration
(200 transformation jobs) and ML feature engineering. Spot instances reduce
compute cost by 60-90%.

**AWS Glue Catalog:** Central metadata catalog. All tools (Athena, Spark,
Snowflake) point to the same catalog for table discovery."

---

## Phase 3: Deep Dive (Minutes 10-30)

### Deep Dive: Storage Format and Organization

"Every table in the lake uses Parquet as the physical format with Iceberg as
the table format layer.

**Why Parquet:** Columnar storage with 3-5x compression vs raw CSV. Column
pruning means queries only read the columns they need. Predicate pushdown
skips row groups that do not match filter conditions. See
[`patterns/scale_and_performance.md`](../patterns/scale_and_performance.md) for storage optimization details.

**Why Iceberg over raw Parquet:** Raw Parquet files in S3 lack ACID
transactions, schema evolution and efficient upserts. Iceberg adds:
- **ACID writes:** No partial writes visible to readers
- **Time travel:** Query data as of any previous snapshot
- **Schema evolution:** Add/rename columns without rewriting data
- **Partition evolution:** Change partitioning strategy without rewriting data

**S3 organization:**

```
s3://data-lake/
├── bronze/oracle/{orders,customers}/, bronze/hadoop/events/
├── silver/{orders,customers}/   (cleaned, typed, deduped, SCD applied)
└── gold/{fact_orders,dim_customers}/   (star schema, query-optimized)
```

**File sizing:** Target 128 MB - 512 MB per file. The 150 TB dataset at
256 MB per file produces roughly 600K files. Iceberg's metadata layer handles
this efficiently through manifest files rather than listing the S3 prefix.

**Compression:** Parquet with Snappy compression balances speed and ratio.
Raw CSV at 150 TB compresses to roughly 40-50 TB in Parquet (3-4x savings).
For cold archival data, Zstandard offers 20-30% better compression than
Snappy at the cost of slower write speeds."

### Deep Dive: Migration Strategy

"I'd use a parallel-run approach over the 6-month timeline:

**Month 1-2: Infrastructure and ingestion.**
Set up the S3 bucket structure, Iceberg tables and Glue Catalog. Configure
DMS to replicate Oracle to S3 via CDC. Run `hadoop distcp` to copy HDFS data
to S3. At this point, both the old and new systems have the data.

**Month 3-4: Transform migration.**
Port the 200 Informatica jobs to Spark or dbt. Prioritize by business
criticality: start with the 20 most-used reports. Run old and new pipelines
in parallel and compare outputs.

**Validation approach:** For each migrated pipeline, compare:
- Row counts (must match exactly)
- Sum of numeric columns (must match within rounding tolerance)
- Sample of 1,000 random rows (must match exactly)

If outputs match for 2 consecutive weeks, the pipeline is validated.

**Month 5: Analyst onboarding.**
Move BI dashboards from the old system to Snowflake/Looker. Train analysts
on the new tools. Keep the old system read-only as a fallback.

**Month 6: Cutover and decommission.**
Decommission Informatica licenses and the Hadoop cluster. Keep Oracle running
in read-only mode for 3 months as a safety net, then decommission.

The parallel-run approach costs more during the migration period (running
both systems) but eliminates the risk of a big-bang cutover. At the scale of
this company, the 3-month overlap cost is modest compared to the risk of data
loss during migration."

### Deep Dive: Access Control

"Multiple teams need different levels of access:

**Data engineers:** Full read/write to all layers (Bronze, Silver, Gold).
IAM roles scoped to the data-lake S3 bucket with full permissions.

**Analysts:** Read-only on Silver and Gold. No access to Bronze (raw data may
contain unmasked PII). Access through Snowflake with row-level security for
sensitive tables.

**Data scientists:** Read on Silver and Gold, plus write access to a separate
`sandbox/` prefix for experimental work. Spark access via EMR with IAM roles.

**Implementation:** IAM policies on S3 prefixes control who can read/write
each layer. Snowflake roles provide SQL-level access control. Column-level
masking in Snowflake hides PII from analysts who do not need it (email and
phone masked, customer_id visible).

For the 7-year financial data retention requirement: lifecycle policies move
Gold financial tables to S3 Glacier after 1 year. Retrieval takes minutes
but costs drop from $0.023/GB to $0.004/GB. A 50 TB financial archive on
Glacier costs $200/month vs $1,150/month on Standard."

---

## Phase 4: Scaling and Edge Cases (Minutes 30-40)

### The Small Files Problem

"The Hadoop migration and CDC ingestion both produce many small files. CDC
writes one file per Kafka batch (potentially thousands of tiny files per day).

**Solution:** Run Iceberg's `rewrite_data_files` procedure daily on Silver
tables. This compacts small files into the target 256 MB size. Delta Lake's
equivalent is `OPTIMIZE`. On a table with 10K small files, compaction runs in
5-10 minutes on a small Spark cluster and reduces file count by 95%.

For the Bronze layer, I'd compact weekly rather than daily since raw data is
read less frequently."

### Cross-Cloud Egress

"If the company uses S3 for storage but needs BigQuery for some workloads
(perhaps an acquired company uses GCP):

- **Egress cost:** $0.09/GB from AWS to GCP. A 10 TB dataset synced monthly
  costs $900/month in egress alone.
- **Mitigation:** Replicate only the Gold layer (much smaller than total
  lake). A 5 TB Gold layer replicated monthly costs $450/month.
- **Alternative:** Use Snowflake with cross-cloud data sharing if both
  environments use Snowflake. Zero egress for shared data.
- **Best practice:** Keep storage and compute in the same cloud and region.
  Design for single-cloud unless there is a strong business reason for
  multi-cloud."

### Legacy Compatibility

"Some teams may resist moving off Oracle immediately (stored procedures,
custom reports, embedded SQL in applications).

**Short-term:** Provide a read replica of the Oracle data via DMS. The
replica stays in sync with the new pipeline's output. Legacy applications
read from the replica while being migrated.

**Medium-term:** Identify which Oracle features are in use (stored
procedures, materialized views, specific functions) and build equivalents
in the new platform. Many Oracle-specific features have direct Snowflake or
Spark equivalents.

**Long-term:** Decommission Oracle entirely. The parallel-run period gives
teams time to migrate without pressure.

**Timeline risk:** Oracle decommission often stretches beyond plan because
teams discover undocumented dependencies. Budget 2-3 months of extended
read-only Oracle availability beyond the target cutover date. At roughly
$6K/month for the Oracle license during this period, the insurance cost
is modest compared to the risk of a rushed cutover."

### Cost Comparison

"Estimated annual costs:

**Current on-premise:**
- Oracle licensing: ~$75K/year
- Informatica licensing: ~$50K/year
- Hadoop cluster (hardware, support): ~$80K/year
- Server room, power, networking: ~$30K/year
- **Total: ~$235K/year**

**Target cloud (steady state, post-migration):**
- S3 storage (150 TB): ~$3,450/month = $41K/year
- Snowflake (XS warehouse, moderate usage): ~$500/month = $6K/year
- EMR/Spark (daily batch, spot instances): ~$400/month = $5K/year
- DMS replication: ~$200/month = $2.4K/year
- Glue Catalog, Lambda, misc: ~$100/month = $1.2K/year
- **Total: ~$56K/year**

The cloud option is roughly 75% cheaper in direct costs, plus eliminates
hardware refresh cycles and reduces operational burden. The 6-month
migration has a one-time cost of ~$40K (parallel-run overlap), paid back
within 3 months of steady-state savings.

**Hidden costs to mention:** Data transfer from on-premise to S3 costs
$0.09/GB for the initial 150 TB upload (about $13,500 one-time). AWS
Snowball ($300 per device, 80 TB capacity) is cheaper for the Hadoop
migration at this scale. Staff training on the new platform (Spark, dbt,
Snowflake) typically runs $2K-5K per engineer for formal courses or 2-3
weeks of ramp-up time."

---

## Phase 5: Wrap Up (Minutes 40-45)

"Key design decisions and tradeoffs:

1. **Lakehouse architecture (S3 + Iceberg + Snowflake) over warehouse-only.**
   The lake stores everything in open formats, avoiding lock-in. Snowflake
   provides the SQL experience analysts need. The tradeoff is more
   architectural complexity than a warehouse-only approach, but the
   flexibility to support ML workloads and ad-hoc Spark processing justifies
   it for a team with data scientists.

2. **Parallel-run migration over big-bang cutover.** Costs more during the
   overlap period but eliminates the risk of data discrepancies going
   undetected. At this company's scale, the overlap cost (~$40K) is small
   relative to the risk.

3. **Iceberg over Delta Lake.** Broader engine compatibility (Athena, Trino,
   Snowflake, Spark) reduces lock-in risk. Delta Lake would be the right
   choice if the team were standardizing on Databricks.

4. **Managed services (Snowflake, EMR) over self-hosted.** A team of 5 data
   engineers cannot maintain a custom warehouse and a Spark cluster and
   build pipelines. Managed services let the team focus on data rather than
   infrastructure.

With more time, I'd detail the data quality framework for validating the
migration, the disaster recovery strategy (cross-region S3 replication for
critical data) and the cost monitoring setup (AWS Cost Explorer alerts to
catch runaway spend).

**Key numbers summary:** 150 TB total data (50 TB Oracle + 100 TB Hadoop),
2 TB/month growth, 200 Informatica jobs to migrate. Current cost ~$235K/year
on-premise, target ~$56K/year on cloud (75% savings). 6-month migration
timeline with a $40K one-time overlap cost, paid back within 3 months of
steady-state savings. S3 Glacier drops archival storage costs from $0.023/GB
to $0.004/GB for the 7-year financial data retention requirement."
