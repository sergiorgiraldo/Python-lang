# Scale and Performance

Scale in data engineering is not about handling 10M concurrent users. It is
about processing terabytes efficiently and keeping costs under control. The
performance patterns here address the four areas that matter most at scale:
partitioning, data skew, storage optimization and cost management.

## Partitioning

Partitioning divides large datasets into smaller, manageable segments. Done
right, it reduces query scan size by orders of magnitude. Done wrong, it
creates operational problems that are hard to fix later.

### Why Partition

**Reduce scan size:** A query filtering on `event_date = '2024-01-15'`
scans one partition instead of the entire table. On a 1 TB table with 365
daily partitions, that is 2.7 GB instead of 1 TB.

**Enable parallelism:** Spark assigns one task per partition. More partitions
means more parallel tasks up to the cluster's capacity.

**Manage file sizes:** Partitioning naturally segments data into files.
Combined with compaction, this keeps file sizes in the optimal range.

### Time Partitioning

The most common strategy for event data. Partition by date for most use
cases, by hour for high-volume streaming data.

**Query benefit:** In BigQuery at $5/TB scanned (on-demand), a full table
scan on 1 TB costs $5.00. A single daily partition scan costs about $0.014.
Over 100 queries/day, that is $500 vs $1.40.

**Risk:** Today's partition receives all writes (hot partition). For append-
heavy workloads, this is expected and most systems handle it well. For
update-heavy workloads, consider decoupling write partitioning from query
partitioning.

### Hash Partitioning

Distribute data evenly across N partitions by hashing a key column. Each
partition gets roughly 1/N of the data regardless of key distribution.

**When to use:** Non-time-series data where queries filter by a specific
key (customer_id, device_id) rather than date ranges. Eliminates hot
partitions but sacrifices range scan efficiency.

### Composite Partitioning

Partition by one column, cluster/sort by another within each partition.
BigQuery supports this natively: partition by date, cluster by customer_id.
Delta Lake and Iceberg support similar multi-level organization.

**Example:** Partition by `event_date`, cluster by `user_id`. A query for
"all events from user X on January 15" benefits from partition pruning
(skip all non-January-15 data) and cluster pruning (skip blocks within the
partition that do not contain user X).

### The Small Files Problem

Over-partitioning creates many tiny files. A table with hourly partitions,
100 source systems and 365 days produces 876,000 partitions. If each has
10 files, that is 8.7M files. Spark and Hive perform poorly with millions
of small files because metadata operations dominate runtime.

**Rule of thumb:** Each file should be 100 MB - 1 GB in compressed Parquet.
If your partitions produce files smaller than 10 MB, you are
over-partitioned.

**Solutions:** Compaction jobs that merge small files (Delta Lake OPTIMIZE,
Iceberg rewrite_data_files). Reduce partition granularity (daily instead
of hourly). Bucketing within partitions.

### Sizing Example

A table with 1B rows at 100 bytes/row (columnar) = 100 GB total. With daily
partitions over 1 year: 100 GB / 365 = ~274 MB per partition. Good size.
With hourly partitions: 100 GB / 8,760 = ~11 MB per partition. Too small.
Daily partitioning is the right choice here.

## Data Skew

Data skew occurs when data is unevenly distributed across partitions or
workers. It is one of the most common performance problems in distributed
data processing.

### Why It Matters

In a distributed join, each worker processes a range of keys. If one key
(say customer_id = 12345) has 100M rows while others have 10K rows, the
worker assigned to key 12345 takes 10,000x longer than the others. The job
finishes when the slowest worker finishes. 99 fast workers wait for 1 slow
worker.

### Detection

- **Spark UI:** Look for tasks that take 10-100x longer than the median
- **Partition size distribution:** Query partition sizes and look for outliers
- **Key frequency:** COUNT(*) GROUP BY the join key. Keys with counts far
  above the median are skew candidates

### Solutions

**Salting:** Add a random suffix (0-9) to hot keys. The key "12345" becomes
"12345_0" through "12345_9". The data spreads across 10 partitions instead
of 1. Both sides of the join must apply the same salting logic.

**Broadcast join:** If one side of the join is small enough to fit in memory
(under 1-2 GB for Spark), broadcast it to all workers. No shuffle needed,
no skew possible. Spark automatically broadcasts tables under 10 MB by
default (configurable via `spark.sql.autoBroadcastJoinThreshold`).

**Pre-aggregation:** Aggregate hot keys separately before joining. If the
join only needs a SUM, pre-aggregate the 100M rows for key 12345 into a
single row, then join.

**Adaptive Query Execution (Spark 3+):** Automatically detects skew at
runtime and splits large partitions into smaller ones. Enable with
`spark.sql.adaptive.enabled=true`. Handles many skew scenarios without
manual intervention.

**Connection:** Key skew in distributed joins is the distributed equivalent
of hash collisions. The same algorithmic thinking from
[`patterns/01_hash_map/`](../../patterns/01_hash_map/README.md) applies: when keys cluster, performance degrades.

## Storage Optimization

### File Format Selection

| Format | Compression | Read Speed | Write Speed | Best For |
|---|---|---|---|---|
| Parquet | 3-5x vs CSV | Fast (columnar) | Moderate | Analytics, warehouses |
| ORC | 3-5x vs CSV | Fast (columnar) | Moderate | Hive ecosystem |
| Avro | 2-3x vs JSON | Moderate (row) | Fast | Streaming, schema evolution |
| JSON | 1x (baseline) | Slow | Fast | Interchange, debugging |
| CSV | 0.8-1x | Slow | Fast | Legacy, human-readable |

**Default choice:** Parquet with Snappy compression. It is the standard for
analytical workloads across Spark, BigQuery, Snowflake, Athena and most
modern data tools.

### Compression Algorithms

| Algorithm | Ratio vs Raw | Speed | Use Case |
|---|---|---|---|
| Snappy | ~3:1 | Fast | Default for Parquet, hot data |
| ZSTD | ~5:1 | Moderate | Cold/archive data, storage cost priority |
| Gzip | ~4:1 | Slow | Compatibility, interchange |
| LZ4 | ~2.5:1 | Very fast | Real-time processing, streaming |

**Tradeoff:** Better compression saves storage cost but increases CPU cost.
Snappy is the default because it balances both. Switch to ZSTD for data
that is written once and read rarely (archives, compliance data).

### Query Optimization Techniques

**Column pruning:** Select only the columns you need. In Parquet, unselected
columns are never read from disk. A 100-column table where you select 5
columns: 95% data reduction at the I/O level.

**Predicate pushdown:** Filters pushed to the file reader. Rows that do not
match the predicate are skipped during deserialization. In Parquet, min/max
statistics per column chunk allow skipping entire row groups.

**Z-ordering / Clustering:** Organize data within files by multiple columns
so that rows with similar values in those columns are physically co-located.
Enables efficient multi-dimensional filtering.

- BigQuery: CLUSTER BY up to 4 columns
- Delta Lake: ZORDER BY
- Snowflake: automatic clustering on designated columns
- Iceberg: sort orders defined in table metadata

**Materialized views:** Pre-compute expensive aggregations. Trade storage
for query speed. A 1 TB fact table aggregated into a 10 GB summary table
turns a 30-second scan into a sub-second lookup.

**Connection:** Query-level optimization techniques like indexing and
partition pruning are covered in [`sql/05_optimization_and_production/`](../../sql/05_optimization_and_production/README.md).
The patterns here operate at the storage and architecture level.

## Cost Management

Storage is cheap. Compute is expensive. The cost optimization strategy
follows from this asymmetry.

### Storage Costs

| Tier | Cost (S3/month) | Access |
|---|---|---|
| Standard | $0.023/GB | Immediate |
| Infrequent Access | $0.0125/GB | Immediate, retrieval fee |
| Glacier | $0.004/GB | Minutes to hours retrieval |
| Deep Archive | $0.00099/GB | 12-48 hours retrieval |

A 10 TB dataset on S3 Standard costs $230/month. The same data on Glacier
costs $40/month. On Deep Archive: $10/month. Lifecycle policies that move
data to cheaper tiers after 90 days reduce storage costs by 50-80%.

### Compute Costs

| Service | Cost | Unit |
|---|---|---|
| BigQuery (on-demand) | $5/TB scanned | Per query |
| Snowflake (XS warehouse) | ~$2/credit/hour | Per warehouse-hour |
| Spark (EMR, 10-node m5.xlarge) | ~$4/hour | Per cluster-hour |
| Lambda | $0.20/1M invocations | Per invocation |

### Cost Reduction Strategies

**Better partitioning:** The single biggest cost lever. Partition pruning
turns a $5 full-table scan into a $0.01 single-partition scan.

**Column pruning:** SELECT only what you need. `SELECT *` on a 200-column
table scans 200 columns. `SELECT user_id, event_type, timestamp` scans 3.

**Approximate functions:** HyperLogLog for distinct counts. See
[`patterns/11_probabilistic_structures/`](../../patterns/11_probabilistic_structures/README.md) for details. Approximate
COUNT(DISTINCT) on 1B rows: ~2 seconds. Exact: ~2 minutes.

**Auto-suspend and auto-scale:** Snowflake warehouses auto-suspend after 5
minutes of inactivity (configurable). Spark clusters on EMR can auto-scale
from 2 to 20 nodes based on queue depth.

**Spot/preemptible instances:** Spark batch jobs tolerate interruption. Spot
instances cost 60-90% less than on-demand. A 10-node Spark cluster at $4/hour
on-demand costs $1.00/hour on spot instances.

**Retention policies:** Delete or archive data that is past its useful life.
A 90-day retention policy on detailed event data with yearly aggregates
retained long-term balances cost and analytical value.

### The Biggest Waste

Full table scans on partitioned tables where the query forgot the partition
filter. A single missing `WHERE event_date = ...` clause turns a $0.01 query
into a $5.00 query. Enforce partition filters using BigQuery's
`require_partition_filter` table option or equivalent guardrails.

## Connection to Interview

When discussing scale in an interview, tie every optimization to a number.
"We partition by date" is good. "We partition by date, which reduces query
scan from 1 TB to ~2.7 GB per day, saving roughly $4.99 per query at
BigQuery on-demand pricing" is much better.

Use the capacity estimation framework from `foundations/capacity_estimation.md`
to size the system. Use the tradeoff framework from
`foundations/tradeoff_framework.md` to justify optimization choices (Snappy
vs ZSTD, exact vs approximate, spot vs on-demand).
