# Data Quality Patterns

Data quality is the most underestimated topic in DE system design interviews.
Every pipeline produces incorrect data sometimes. The question is whether you
detect it before or after your stakeholders do. Mentioning data quality
unprompted in an interview signals operational maturity and separates
experienced engineers from those who have only built prototypes.

## Data Quality Dimensions

Six dimensions cover the ways data can go wrong. Knowing these gives you a
vocabulary for discussing quality in interviews.

### Completeness

Are all expected records present? A pipeline that ingests 10M events/day
but only loads 9.5M has a completeness problem. Detection: compare source
row counts to destination row counts. Check for gaps in time-series data
(missing hours, missing dates).

### Accuracy

Do values match reality? A revenue column showing $0 for all orders last
Tuesday is an accuracy problem. Detection: range checks (revenue > 0),
cross-system reconciliation (pipeline totals match source system reports),
statistical bounds (daily revenue within 3 standard deviations of the
trailing 30-day mean).

### Consistency

Do related datasets agree? If the orders table shows $1M revenue for January
but the payments table shows $950K, there is a consistency problem.
Detection: cross-table reconciliation queries, sum-of-details vs header
total checks, bidirectional foreign key validation.

### Timeliness

Is data fresh enough for its consumers? A dashboard with a 6 AM SLA showing
yesterday's data at 9 AM is a timeliness problem. Detection: freshness
monitoring (compare max timestamp in the table to current time), SLA
tracking with alerting.

### Uniqueness

Are there duplicates? A pipeline that processes the same event twice creates
duplicate rows. Detection: primary key uniqueness checks, COUNT(*) vs
COUNT(DISTINCT primary_key) comparison. See [`sql/03_aggregations/`](../../sql/03_aggregations/README.md) for
duplicate detection patterns.

### Validity

Do values conform to expected formats and ranges? An email column containing
phone numbers is a validity problem. Detection: regex validation, enum
checks (status must be one of [active, inactive, pending]), type assertions,
range constraints (age between 0 and 150).

## Testing Patterns: A Layered Approach

Quality checks are not all equal. Some are cheap and catch most issues. Others
are expensive but catch subtle bugs. Layer them from cheapest to most expensive.

### Layer 1: Schema Validation

**Cost:** Near zero. Runs in milliseconds.
**Catches:** Renamed columns, type changes, dropped columns, added columns.

Assert that the data matches the expected schema before any processing begins.
Column names, types and nullability constraints.

**Implementation:** Avro schema registry for streaming data. dbt schema tests
for warehouse models. Custom assertions at pipeline ingestion points.

**Example:** A source API changes `user_id` from integer to string. Schema
validation catches this before the pipeline attempts to CAST it into an
integer column and fails with a cryptic error 6 tasks downstream.

### Layer 2: Statistical Validation

**Cost:** Moderate. Requires computing aggregates over the dataset.
**Catches:** Partial loads, source issues, transformation bugs, drift.

Assert that statistical properties of the data are within expected bounds.

**Key checks:**
- Row count within expected range (yesterday's count +/- 20%)
- NULL rate per column within threshold (email NULL rate < 5%)
- Value distribution within bounds (mean order value between $10 and $500)
- Cardinality checks (number of distinct product categories between 15 and 25)

**Example:** A source system migration changes a field from required to
optional. The column's NULL rate jumps from 0% to 45%. Statistical
validation catches this even though schema validation passes (the column
still exists, still the right type).

### Layer 3: Business Rule Validation

**Cost:** Highest. May require joins, aggregations and cross-system queries.
**Catches:** Join errors, aggregation bugs, missing data, logic errors.

Assert that business rules hold in the output data.

**Key checks:**
- Revenue sums match source system (reconciliation within 0.1%)
- Referential integrity (every order has a valid customer_id)
- Cross-table reconciliation (sum of line items = order total)
- Temporal logic (start_date <= end_date, no future-dated records)

**Example:** A code change in the transformation layer accidentally filters
out orders with discount codes. Revenue drops 15% but row counts are fine
(the orders without discounts still load normally). Only a business rule
check comparing revenue totals to the source system catches this.

### Choosing Which Layers to Implement

| Pipeline Criticality | Recommended Layers |
|---|---|
| Prototype / experimental | Layer 1 only |
| Internal analytics | Layers 1 and 2 |
| Customer-facing data | Layers 1, 2 and 3 |
| Financial / regulatory | All layers, plus reconciliation |

## Circuit Breaker Pattern

When quality checks fail, what happens next matters as much as detecting the
failure.

### Fail-Fast

Stop the pipeline immediately. Do not propagate bad data downstream. Alert
the on-call engineer.

**When to use:** Critical data paths where downstream systems cannot tolerate
incorrect data. Financial reporting, customer-facing dashboards, ML model
training data.

**Implementation:** Airflow branch operators that skip downstream tasks on
check failure. dbt severity levels (error stops the run, warn continues).
Custom checkpoint tasks that raise exceptions on quality failures.

### Quarantine

Isolate bad records into a quarantine table. Continue processing good records.
Review quarantined records separately.

**When to use:** High-volume pipelines where a small percentage of bad records
should not block the majority. Event streaming where some malformed events
are expected.

**Implementation:** Try/except in transformation logic that routes failures to
a dead letter table. Separate processing paths for valid and invalid records.

### Choosing Between Fail-Fast and Quarantine

Apply the tradeoff framework from `foundations/tradeoff_framework.md`:

- **Fail-fast** optimizes for correctness at the cost of availability. No
  bad data gets through but the pipeline stops on any quality issue.
- **Quarantine** optimizes for availability at the cost of completeness. The
  pipeline keeps running but some records are set aside for review.

Financial data: fail-fast. Clickstream analytics: quarantine (a few malformed
events do not change business decisions).

## Data Observability

Quality checks are point-in-time assertions. Observability is continuous
monitoring that detects problems before they trigger failures.

### What to Monitor

**Freshness:** When was the table last updated? Track the maximum timestamp
or the last successful pipeline run. Alert if freshness exceeds the SLA.

**Volume:** How many rows arrived today vs the trailing 7-day average? A
sudden drop of 30%+ warrants investigation even if quality checks pass.

**Schema changes:** Did the upstream schema change? Log and alert on column
additions, removals and type changes. Even additive changes (new columns)
deserve awareness.

**Distribution drift:** Are column value distributions shifting? A product
category that was 5% of orders jumping to 40% may indicate a data issue or
a real business change. Either way, someone should know.

### Tools

| Tool | Approach | Cost Model |
|---|---|---|
| Monte Carlo | Automated monitoring, ML-based anomaly detection | SaaS, per-table pricing |
| Great Expectations | Assertion-based, developer-defined checks | Open source |
| dbt tests | Integrated with transformation layer | Open source (dbt Core) |
| Elementary | dbt-native observability | Open source + cloud |
| Custom dashboards | SQL queries on metadata tables | Build cost only |

For interviews, you do not need to name specific tools. Describing the
approach (automated freshness monitoring, volume trend tracking, schema
change alerts) matters more than the implementation.

## SLA Management

### Defining SLAs

Work with stakeholders to define measurable data SLAs.

**Good SLA:** "The `fact_orders` table is updated by 6 AM UTC daily with less
than 1% NULL rate in the `revenue` column and row count within 20% of the
prior day."

**Bad SLA:** "The data should be fresh and accurate."

Specific, measurable SLAs enable automated monitoring and clear escalation
paths.

### Monitoring Compliance

Track SLA compliance as a percentage over time. Target 99.5%+ on-time
delivery for critical tables. A 99.5% SLA on a daily refresh allows roughly
2 missed days per year.

### Escalation Path

Define what happens when an SLA is breached:

1. **Automated alert** fires to the on-call channel (Slack, PagerDuty)
2. **On-call engineer** investigates within 15 minutes
3. **Stakeholder notification** if resolution will exceed the SLA by more
   than 1 hour
4. **Post-incident review** for SLA breaches that impact business decisions

### Budgeting for Catch-Up

If the 6 AM SLA is missed because upstream data was late, what is the
recovery plan? Options: re-run the pipeline as soon as upstream data arrives,
process a partial dataset and backfill later, or push the SLA to a fallback
time.

Build catch-up capacity into pipeline design. If the normal batch window is
2 hours (4 AM to 6 AM), the pipeline should be able to process the same
volume in 1 hour when running catch-up. This means the pipeline normally
runs at 50% capacity with headroom for recovery.

## Connection to Interview

When designing a pipeline in a system design interview, always mention data
quality. Even a single sentence makes a difference:

- "I would add row count checks after each transformation stage."
- "A freshness monitor on the final table alerts if data is stale."
- "Schema validation at ingestion catches upstream changes early."
- "For financial data, I would add cross-system reconciliation checks."

These statements show you have operated pipelines in production and
understand that building the pipeline is half the work. Keeping it running
correctly is the other half.

The quality patterns connect directly to the pipeline architecture patterns
in [`system_design/patterns/pipeline_architecture.md`](pipeline_architecture.md) (testing and monitoring
sections) and to the tradeoff framework in [`foundations/tradeoff_framework.md`](../foundations/tradeoff_framework.md)
(fail-fast vs quarantine, exact vs approximate quality thresholds).
