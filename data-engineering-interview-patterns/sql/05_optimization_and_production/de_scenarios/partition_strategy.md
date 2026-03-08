# Partition Strategy

Partitioning divides a large table into smaller physical chunks based on a
column value (usually date). Queries that filter on the partition key read
only the relevant chunks instead of the entire table.

## Types of Partitioning

### Date Partitioning (Most Common)

Partition by a date/timestamp column. Most event and transaction tables use this.

| Granularity | Use When | Partition Count (1 year) |
|---|---|---|
| Daily | High-volume tables, queries filter to specific days | 365 |
| Monthly | Medium-volume, queries filter to months | 12 |
| Yearly | Low-volume or historical data | 1 |

**Rule of thumb**: choose the granularity that matches your most common query
filter. If dashboards filter by day, partition by day.

### Hash Partitioning

Distribute rows evenly across N partitions using a hash of a column value.

- **Pro**: even data distribution, no hot partitions
- **Con**: no pruning benefit for range queries (WHERE date BETWEEN)
- **Use case**: join optimization (co-partition two tables on join key)

### List Partitioning

Partition by specific values of a column (e.g., region, country).

- **Pro**: queries filtering on the list column prune effectively
- **Con**: uneven partition sizes if value distribution is skewed

## When to Partition

**Partition when:**
- Table exceeds 1GB (smaller tables scan fast enough without partitioning)
- Frequent queries filter on a specific column (date, region, tenant_id)
- You need to manage data lifecycle (drop old partitions instead of DELETE)

**Do not partition when:**
- Table is small (< 1GB)
- Queries rarely filter on any consistent column
- The partition key has too many distinct values (millions of tiny partitions)

## Partition Granularity Pitfalls

### Too Fine: Millions of Tiny Files

Partitioning a 10GB table by (date, hour, user_id) creates millions of
tiny files. Each file has overhead (metadata, file handles, listing operations).

**Symptoms**: slow query planning, "too many files" errors, high cloud storage
API costs (per-request pricing).

**Fix**: partition by date only. Use clustering/sort keys within partitions
for additional filtering.

### Too Coarse: No Pruning Benefit

Partitioning a 100TB table by year creates 3-5 partitions of 20-33TB each.
Queries filtering to a single day still scan an entire year.

**Fix**: partition by day or month.

## Dialect Specifics

### BigQuery

```sql
CREATE TABLE events
PARTITION BY DATE(event_timestamp)
CLUSTER BY user_id, event_type
AS SELECT * FROM raw_events;
```

- Partitions by DATE, TIMESTAMP, INTEGER range or ingestion time
- Supports `REQUIRE PARTITION FILTER` to prevent full scans
- Clustering sorts data within partitions (up to 4 columns)

### Snowflake

Snowflake uses **micro-partitions** (50-500MB compressed). Partitioning is
automatic. You do not explicitly create partitions.

```sql
-- Clustering key hints for the automatic optimizer
ALTER TABLE events CLUSTER BY (event_date, region);
```

- Clustering determines the sort order within micro-partitions
- Query Profile shows "partitions scanned" vs "partitions total"
- `SYSTEM$CLUSTERING_INFORMATION('table')` shows clustering quality

### Spark / Delta Lake

```python
# Partition on write
df.write.partitionBy("event_date").format("delta").save("/path/to/table")

# Z-ORDER for multi-column clustering within partitions
spark.sql("OPTIMIZE events ZORDER BY (user_id, event_type)")
```

- Physical directories per partition value: `event_date=2024-01-15/`
- Small files problem: use OPTIMIZE / compaction
- Z-ORDER clusters data within partitions for non-partition filters

### Postgres

```sql
CREATE TABLE events (
    event_id SERIAL, event_date DATE, ...
) PARTITION BY RANGE (event_date);

CREATE TABLE events_2024_01 PARTITION OF events
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

- Manual partition creation (or use pg_partman extension)
- Partition pruning happens at query planning time
- `EXPLAIN` shows which partitions are scanned

## Monitoring Partition Effectiveness

Questions to ask when reviewing a partitioned table:

1. **What percentage of partitions does the average query scan?**
   Target: < 5% for date-partitioned tables with daily queries.

2. **Are any partitions disproportionately large?**
   A skewed partition (one day with 100x normal volume) can cause hotspots.

3. **Are queries actually filtering on the partition key?**
   Check EXPLAIN plans. If most queries scan all partitions, the partitioning
   is not providing value.

4. **Is the partition granularity appropriate?**
   A table queried by month should not be partitioned by hour.
