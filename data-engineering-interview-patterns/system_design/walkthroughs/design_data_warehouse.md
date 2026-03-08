# Walkthrough: Design a Data Warehouse

**Prompt:** "Design a data warehouse for a mid-size e-commerce company."

This walkthrough simulates a full 45-minute system design interview. It
follows the communication framework from [`foundations/communication_framework.md`](../foundations/communication_framework.md)
and uses the data modeling patterns from [`patterns/data_modeling_patterns.md`](../patterns/data_modeling_patterns.md).

---

## Phase 1: Clarify Requirements (Minutes 0-5)

### Questions to Ask

**Source questions:**
- "What are the source systems? Transactional database, web analytics, payment
  processor, marketing tools?"
- "What databases? Postgres, MySQL, something else?"
- "Are there third-party SaaS sources like Shopify, Stripe, Salesforce?"

**Consumer questions:**
- "Who will query the warehouse? BI team, finance, marketing, data science?"
- "What BI tool are they using? Looker, Tableau, Power BI?"
- "Are there specific reporting deadlines? Month-end close, daily dashboards?"

**Scale questions:**
- "How many orders per year? How many web events?"
- "How many analysts will query concurrently?"
- "What's the acceptable data freshness? Real-time, hourly, daily?"

### Establishing Requirements

"Based on your answers, here's what I'm working with:

**Sources:**
- PostgreSQL: orders, customers, products, inventory (~5M orders/year, 500K
  customers, 50K products)
- Shopify: web analytics (~50M page views/month)
- Stripe: payment records (~1M transactions/month)

**Consumers:**
- BI team: daily dashboards in Looker (order trends, conversion funnel)
- Finance: monthly revenue reports, needed by 8 AM on the 1st of each month
- Marketing: campaign attribution, weekly cohort analysis
- Data science: churn prediction features, recommendation training data

**Volume and freshness:**
- Orders table: 5M rows/year, ~500 bytes/row = 2.5 GB/year
- Web events: 600M rows/year, ~200 bytes/row = 120 GB/year
- Total warehouse (with transforms): roughly 200-300 GB after 2 years
- Daily refresh is sufficient for all consumers except the month-end
  deadline, which needs a guaranteed completion time

This is a moderate-scale warehouse. Managed services (Snowflake or BigQuery)
make sense over self-hosted solutions. The data volumes do not justify the
operational overhead of running our own infrastructure. Self-hosted Postgres
or ClickHouse would save on licensing costs but add significant maintenance
burden for a team this size."

---

## Phase 2: High-Level Design (Minutes 5-10)

### Architecture

```
Sources                  Ingestion           Transform      Serve
─────────               ─────────           ─────────      ─────
PostgreSQL ──▶ Debezium (CDC) ──▶
                                    S3/GCS   ──▶  dbt  ──▶  Snowflake ──▶ Looker
Shopify API ──▶ Fivetran ────────▶ (staging)       │        /BigQuery     Tableau
                                                   │                      Reports
Stripe API  ──▶ Fivetran ────────▶                 │
                                                   ▼
                                    Airflow (orchestration)
```

### Component Justification

"**Debezium for PostgreSQL:** Log-based CDC captures every insert, update and
delete from the PostgreSQL transaction log with sub-second latency and under
1% overhead on the source database. We need CDC because the orders table gets frequent
updates (status changes, shipping updates). See
[`patterns/ingestion_patterns.md`](../patterns/ingestion_patterns.md) for CDC pattern details.

**Fivetran for SaaS sources:** Managed connectors for Shopify and Stripe.
These are commodity integrations where building custom connectors adds no
business value. Fivetran handles API pagination, rate limiting, schema
changes and incremental loads. This is a build-vs-buy decision: buy for
commodity connectors, build for differentiated pipelines. See
`foundations/tradeoff_framework.md` on build vs buy.

**S3/GCS as staging:** Raw data lands here before transformation. Provides
durability and replay capability independent of the warehouse.

**dbt for transformation:** SQL-based transformations with testing, documentation
and lineage built in. The analytics team can contribute to and review
transformation logic.

**Snowflake or BigQuery:** Managed warehouse with auto-scaling compute. At
200-300 GB total, either handles this comfortably. I'd choose based on which
cloud provider the company already uses.

**Airflow for orchestration:** Manages the daily DAG: ingest, transform, test,
notify. Handles dependencies and retries. A typical daily DAG for this setup
has 15-20 tasks: 3 source extractions, 10-15 dbt models running in
dependency order and 2-3 data quality check tasks."

---

## Phase 3: Deep Dive (Minutes 10-30)

### Deep Dive: Data Modeling

"I'd use a star schema as the core modeling approach. The primary fact table
is `fact_orders` with dimension tables for customers, products, dates and
geography.

**fact_orders:** order_id, customer_key (FK), product_key (FK), date_key (FK),
order_status, quantity, unit_price, discount_amount, total_amount,
shipping_cost. One row per order line item.

**dim_customers:** customer_key (surrogate), customer_id (natural), name,
email, signup_date, segment, city, state, country, effective_date, end_date,
is_current. SCD Type 2 for tracking address and segment changes.

**dim_products:** product_key (surrogate), product_id (natural), name,
category, subcategory, brand, current_price. SCD Type 2 for price and
category changes.

**dim_dates:** date_key, full_date, year, quarter, month, week, day_of_week,
is_weekend, is_holiday. Pre-populated for the next 10 years.

I'm using SCD Type 2 for customers and products because the business needs
to answer questions like 'what was the customer's segment when they placed
this order?' and 'what was the product's price at the time of sale?' Without
Type 2 tracking, historical analysis uses current values, which gives
misleading results. The SQL pattern for getting the current version uses:

```sql
ROW_NUMBER() OVER (
  PARTITION BY customer_id
  ORDER BY effective_date DESC
) = 1
```

This connects to the window function patterns in [`sql/01_window_functions/`](../../sql/01_window_functions/README.md).

**Sizing:** At 500K customers with an average of 3 historical versions each,
`dim_customers` has roughly 1.5M rows. At 200 bytes/row, that is 300 MB.
Small enough that Snowflake caches the entire dimension in memory after the
first query."

### Deep Dive: dbt Project Structure

"I'd organize the dbt project into three layers following the medallion
pattern from [`patterns/data_modeling_patterns.md`](../patterns/data_modeling_patterns.md):

**Staging (stg_):** One-to-one with source tables. Light transformation:
renaming columns, casting types, basic cleaning. Full refresh. At 3 source
systems, the staging layer has roughly 10-15 models.

**Intermediate (int_):** Business logic joins and calculations. Deduplication,
SCD processing, currency conversion, address standardization.

**Marts:** Final star schema models consumed by BI tools. Fact and dimension
tables optimized for Looker's explore pattern. The marts layer typically has
5-10 models: 1-2 fact tables, 3-4 dimensions and 2-3 aggregated views for
specific dashboard needs.

For fact_orders, I'd use dbt's incremental materialization:

```sql
{{ config(
  materialized='incremental',
  unique_key='order_line_id',
  partition_by={'field': 'order_date'}
) }}
```

New and updated orders (identified by updated_at > last run) are merged into
the fact table. Full refresh is available for backfill or recovery. At 5M
orders/year, the incremental load processes roughly 15K new/changed records
per day, finishing in under a minute."

### Deep Dive: Cost Optimization

"At 200-300 GB total warehouse size, costs are modest but worth optimizing:

**Snowflake approach:**
- XS warehouse ($2/credit/hour) with auto-suspend after 5 minutes
- Daily dbt run takes ~15 minutes: ~$0.50/day in compute
- Analyst queries: ~20 queries/day, average 10 seconds each on XS. ~$1/day
- Storage: 300 GB at $23/TB/month = ~$7/month
- **Total: roughly $50-60/month**

**BigQuery approach:**
- On-demand pricing: $5/TB scanned
- With proper partitioning (fact_orders by order_date) and clustering
  (by customer_id), typical analyst queries scan 1-5 GB: $0.005-$0.025/query
- 20 queries/day: ~$0.10-$0.50/day
- Storage: 300 GB at $0.02/GB/month = ~$6/month
- **Total: roughly $10-20/month**

Both are well within reasonable budgets for a mid-size e-commerce company.
BigQuery is cheaper at this scale due to on-demand pricing. Snowflake becomes
more cost-effective at higher concurrency (many analysts querying
simultaneously) because you pay per warehouse-hour rather than per query."

---

## Phase 4: Scaling and Edge Cases (Minutes 30-40)

### Schema Changes in Source

"When a developer adds a column to the PostgreSQL orders table:

- **Debezium:** Detects the schema change from the binlog and includes the new
  column in subsequent messages. Existing messages in Kafka do not have the
  column.
- **Staging layer:** The new column appears as NULL for historical records.
  The staging model needs a column added to its SELECT.
- **Impact:** Additive changes (new columns) are low-risk. We add the column
  to the staging model and downstream as needed. Breaking changes (renamed
  or removed columns) require coordinated updates across the pipeline.

I'd set up schema change alerts in the ingestion layer so the team knows
immediately when a source schema changes, rather than discovering it when a
downstream model breaks.

**Schema testing:** Run a nightly contract test that compares the source
schema to the expected schema in the staging layer. If a new column appears,
log it as informational. If a column is removed or its type changes, alert
the team and pause ingestion for that source. At this scale (3 sources), the
test runs in under 10 seconds."

### Data Quality

"I'd implement quality checks at each layer using dbt tests:

**Staging tests:** Column presence, types, not-null on required fields.
**Intermediate tests:** Uniqueness of business keys after deduplication.
**Mart tests:** Referential integrity (every fact row has valid dimension
keys), accepted values (order_status in [pending, shipped, delivered,
cancelled]), recency (max order_date is within 2 days of today).

For the month-end deadline, a specific test asserts: 'all orders with
order_date in the closing month have been processed.' This prevents the
finance team from running reports on incomplete data. See
[`patterns/data_quality_patterns.md`](../patterns/data_quality_patterns.md) for the full layered testing approach."

### Monitoring and Observability

"I'd implement three categories of monitoring:

**Pipeline health:** DAG completion time tracked daily. The normal dbt run
finishes in 10-15 minutes. If it exceeds 30 minutes, alert the on-call
engineer. Track task-level durations to identify which transformation is
slowing down.

**Data freshness:** A Snowflake task checks the max `updated_at` in
`fact_orders` every 30 minutes. If the data is more than 3 hours stale,
page the team. This is the single most important operational metric for
downstream consumers.

**Cost tracking:** Set up Snowflake resource monitors with a monthly budget
of $100. Alert at 80% utilization. At this scale, runaway queries are the
main cost risk (an analyst accidentally scanning the full events table
without a date filter)."

### Month-End Processing

"The finance team needs all December data available by 8 AM on January 1.
This creates a specific SLA:

- **Risk:** Late-arriving orders, CDC replication delay, long-running
  transforms could push past 8 AM.
- **Mitigation:** Run the December close pipeline at 2 AM on January 1,
  giving 6 hours of buffer. Add an explicit completeness check: compare order
  count in the warehouse to order count in the source database for December.
  Alert the on-call engineer if the counts diverge by more than 0.1%.
- **Fallback:** If the pipeline fails, a manual re-run takes ~15 minutes at
  this data volume. Notify finance of the delay and the expected completion
  time."

### Slowly Changing Products

"Products change in two ways: price changes (frequent) and category
reclassifications (rare but impactful).

**Price changes:** SCD Type 2 on dim_products. Each price change creates a
new dimension row with an effective_date. Historical orders join to the
price that was active at the time of sale.

**Category reclassification:** This is tricky. If a product moves from
'Electronics' to 'Accessories,' should historical reports show the old or
new category? I'd use SCD Type 2 by default (historical reports show the
category at the time), but provide a 'current_category' column (Type 1
overwrite) for reports that want the latest classification. This hybrid
approach (sometimes called Type 6) gives analysts both options."

---

## Phase 5: Wrap Up (Minutes 40-45)

"To summarize the key design decisions:

1. **CDC for PostgreSQL, managed connectors for SaaS sources.** CDC gives us
   near-real-time replication with minimal source impact. Managed connectors
   eliminate maintenance burden for commodity integrations. The tradeoff is
   vendor dependency on Fivetran, but the alternative (building custom Shopify
   and Stripe connectors) is not worth the engineering time at this scale.

2. **Star schema with SCD Type 2 dimensions.** This gives the analytics team
   fast queries with historical accuracy. The tradeoff is more complex
   dimension management, but dbt handles the SCD logic well.

3. **dbt for transformations with layered testing.** SQL-based transforms are
   accessible to the analytics team. The built-in testing framework
   catches quality issues before they reach dashboards.

4. **Managed warehouse (Snowflake or BigQuery).** At 200-300 GB with ~20
   queries/day, managed services cost $20-60/month. Self-hosted alternatives
   cannot match that cost or operational simplicity.

With more time, I'd design the marketing attribution model in detail (multi-
touch attribution requires careful join logic between web events and orders)
and the data access control layer (PII masking for analysts who don't need
customer names or emails).

**Key numbers summary:** 3 source systems, 5M orders/year, 600M web
events/year, 200-300 GB total warehouse, $20-60/month operating cost. The
daily dbt run processes ~15K new records in under a minute. Month-end close
runs at 2 AM with 6 hours of buffer before the 8 AM deadline."
