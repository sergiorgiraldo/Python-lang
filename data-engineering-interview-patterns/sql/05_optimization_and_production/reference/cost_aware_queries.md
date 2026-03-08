# Cost-Aware Query Design

In cloud data warehouses, every query has a dollar cost. Principal-level
engineers are expected to reason about cost when designing queries and
pipelines.

## How Cloud SQL Billing Works

### BigQuery (On-Demand)

- **Pricing model**: $6.25/TB scanned (as of 2024, US multi-region)
- **What counts**: bytes read from storage before any filtering. Column pruning
  reduces bytes. Partition pruning reduces bytes. Result caching avoids scanning.
- **Free tier**: first 1TB/month free
- **Key insight**: SELECT * costs more than SELECT column. A table with 100
  columns where you need 2 still scans all 100 if you use SELECT *.

### BigQuery (Flat-Rate / Editions)

- **Pricing model**: per-slot-second. Slots are units of compute capacity.
- **What counts**: query complexity and parallelism determine slot usage
- **Key insight**: cost is based on compute time, not data scanned. But
  scanning more data still means more compute.

### Snowflake

- **Pricing model**: per-second compute based on warehouse size
- **Warehouse sizes**: XS ($2/hr), S ($4/hr), M ($8/hr), L ($16/hr), XL ($32/hr) - standard tier, US regions
- **What counts**: wall-clock time the warehouse runs. Queries that scan more
  data or do more computation take longer.
- **Auto-suspend**: warehouses suspend after idle timeout (default 5 min).
  Each resume has a 60-second minimum charge.
- **Key insight**: a 30-second query on an XS warehouse costs ~$0.017. The
  same query on an XL warehouse might finish in 2 seconds and cost ~$0.018 -
  similar cost but much faster.

### Spark / Databricks

- **Pricing model**: per-DBU (Databricks Unit). DBUs measure compute per time.
- **What counts**: cluster size * runtime. Shuffle-heavy queries use more
  resources because data moves between executors.
- **Key insight**: broadcast joins avoid shuffle and reduce DBU consumption.
  Partition pruning avoids reading unnecessary files.

## Cost Reduction Techniques

### 1. Column Pruning

Select only the columns you need. This is the single highest-impact optimization
in columnar storage systems.

```sql
-- Expensive: reads all columns
SELECT * FROM events WHERE date = '2024-01-15';

-- Cheap: reads only 3 columns
SELECT user_id, event_type, event_time
FROM events WHERE date = '2024-01-15';
```

**Impact**: if a table has 50 columns and you need 2, column pruning reduces
scan volume by ~96%.

### 2. Partition Pruning

Always filter on the partition key. This tells the engine which physical
partitions to read.

```sql
-- Full scan: reads all 365 daily partitions
SELECT user_id, COUNT(*) FROM events GROUP BY user_id;

-- Pruned: reads only 1 partition
SELECT user_id, COUNT(*)
FROM events
WHERE date = '2024-01-15'
GROUP BY user_id;
```

**Impact**: on a table with daily partitions covering one year, partition
pruning reduces scan volume by ~99.7% when filtering to a single day.

### 3. Clustering / Sort Keys

Organize data within partitions for efficient range filtering.

- **BigQuery**: clustering on up to 4 columns. Blocks within a partition are
  sorted, enabling block-level pruning.
- **Snowflake**: automatic micro-partition pruning. Use CLUSTER BY for explicit
  ordering.
- **Spark/Delta**: ZORDER BY for multi-column clustering.

```sql
-- BigQuery: create clustered table
CREATE TABLE events
PARTITION BY DATE(event_time)
CLUSTER BY user_id, event_type
AS SELECT * FROM raw_events;
```

### 4. Materialized Views / Pre-Aggregation

Pre-compute expensive aggregations that are queried frequently.

```sql
-- Instead of computing daily from raw data:
SELECT region, DATE_TRUNC('day', event_time) AS day, COUNT(*) AS events
FROM raw_events
GROUP BY region, DATE_TRUNC('day', event_time);

-- Materialize once, query the summary:
SELECT * FROM daily_event_summary WHERE day = '2024-01-15';
```

**Impact**: pre-aggregation can reduce data scanned from billions of rows to
thousands.

### 5. Result Caching

BigQuery and Snowflake cache recent query results (typically 24 hours).
Identical queries return cached results at zero cost.

- **BigQuery**: automatic. Exact same query text + same tables = cache hit.
- **Snowflake**: automatic. Same query + no underlying data changes = cache hit.

**Gotcha**: `SELECT *, CURRENT_TIMESTAMP()` always busts the cache because
CURRENT_TIMESTAMP changes.

### 6. Approximate Functions

Use approximate aggregations when exact counts are not required.

```sql
-- Exact: expensive on billions of rows
SELECT COUNT(DISTINCT user_id) FROM events;

-- Approximate: ~1-2% error, much faster
SELECT APPROX_COUNT_DISTINCT(user_id) FROM events;
```

**Impact**: on tables with billions of rows, approximate distinct counts can be
10-100x faster.

## Back-of-Envelope Cost Estimation

### Example 1: BigQuery Full Table Scan

A table with:
- 1 billion rows
- 100 columns, averaging 10 bytes each
- Total size: 1B * 100 * 10 = 1TB

| Query | Bytes Scanned | Cost at $6.25/TB |
|---|---|---|
| SELECT * | 1 TB | $6.25 |
| SELECT one_column | ~10 GB | $0.06 |
| SELECT one_column WHERE date = today (365 partitions) | ~27 MB | $0.0002 |

Running SELECT * hourly for a month: $6.25 * 24 * 30 = **$4,500/month**
Running the partitioned, pruned query hourly: $0.0002 * 24 * 30 = **$0.14/month**

### Example 2: Snowflake Query Cost

A dashboard query runs for 30 seconds on an XS warehouse ($2/hour):
- Cost per run: $2 * (30/3600) = **$0.017**
- Running every 15 minutes: $0.017 * 4 * 24 * 30 = **$49/month**

Optimizing the query to run in 5 seconds:
- Cost per run: $2 * (5/3600) = **$0.003**
- Running every 15 minutes: $0.003 * 4 * 24 * 30 = **$8.64/month**

### Example 3: Costly Pipeline

A daily pipeline scans 500GB from a raw events table:
- BigQuery on-demand: $6.25 * 0.5 = $3.13/run = **$94/month**
- After partitioning by date and adding a date filter, scan drops to 2GB/run:
  $6.25 * 0.002 = $0.013/run = **$0.39/month**

**Savings: $93.61/month from one partition filter.** At scale, these savings
compound across hundreds of pipelines.

## Cost-Aware Design Patterns

### Pattern 1: Incremental Processing

Instead of reprocessing the entire table daily, process only new data.

```sql
-- Full reprocess (expensive): scans entire history
CREATE OR REPLACE TABLE summary AS
SELECT date, COUNT(*) FROM events GROUP BY date;

-- Incremental (cheap): process only new data, merge with existing
MERGE INTO summary s
USING (
    SELECT date, COUNT(*) AS cnt
    FROM events
    WHERE date = CURRENT_DATE - 1  -- only yesterday
    GROUP BY date
) n ON s.date = n.date
WHEN MATCHED THEN UPDATE SET cnt = n.cnt
WHEN NOT MATCHED THEN INSERT VALUES (n.date, n.cnt);
```

### Pattern 2: Tiered Storage

Store frequently accessed data in hot storage, archive older data.

- **BigQuery**: long-term storage pricing (50% cheaper after 90 days untouched)
- **Snowflake**: automatic tiering is not user-controlled, but warehouse
  suspension reduces compute costs
- **Spark/Delta**: use OPTIMIZE and VACUUM to manage storage

### Pattern 3: Query Governance

Set guardrails to prevent runaway costs:

- **BigQuery**: set `maximum_bytes_billed` on queries
  ```sql
  -- Fails if query would scan more than 10GB
  SET @@maximum_bytes_billed = 10737418240;
  ```
- **Snowflake**: set resource monitors and statement timeouts
- **Organizational**: require partition filters in production queries (enforce
  via CI/linting)

## Interview Context

Principal-level candidates are expected to discuss cost when designing queries
and pipelines. Demonstrating cost awareness sounds like this:

> "This query scans 500GB per run. At $6.25/TB, that is $3.13 per run. Running
> hourly, that is $75/day or $2,250/month. Partitioning by date and adding a
> date filter would reduce the scan to ~2GB per run, bringing cost down to
> $0.013 per run, or about $9.36/month. That is a 99.6% cost reduction from
> a single partition filter."

This kind of reasoning demonstrates:
1. You understand the billing model
2. You can estimate costs quickly
3. You think about operational efficiency, not just correctness
4. You can justify optimization work with concrete dollar savings
