# Capacity Estimation

Back-of-envelope math is expected in system design interviews. The numbers do
not need to be precise. They need to be reasonable. The point is to show you
can reason about scale and use numbers to drive design decisions rather than
hand-waving about "a lot of data."

An interviewer who hears "this will be about 25 GB/day compressed, so roughly
9 TB/year, costing about $200/month on S3" will trust your judgment far more
than one who hears "this will be a lot of data so we need a big cluster."

## The Estimation Framework

Use this 5-step sequence for any capacity question. It moves from the known
(user counts, event rates) to the useful (design decisions).

```
1. Start with user/event counts (given or estimated)
2. Convert to throughput (events/second, average and peak)
3. Convert to storage (bytes * events * retention period)
4. Identify bottlenecks (which component handles the most load?)
5. Use the bottleneck to drive design (technology choice, scaling)
```

Step 5 is what separates good answers from great ones. The numbers are not the
point. The design decisions they inform are the point.

## Essential Numbers to Memorize

These are the "napkin math" reference numbers. You do not need exact figures.
You need the right order of magnitude. Knowing that an SSD random read is
roughly 100 microseconds (not 1 microsecond, not 10 milliseconds) is enough.

### Latency

| Operation | Latency |
|---|---|
| L1 cache reference | 1 ns |
| L2 cache reference | 10 ns |
| RAM reference | 100 ns |
| SSD random read | 100 us |
| Network round trip (same datacenter) | 1 ms |
| SSD sequential read (1 MB) | 1 ms |
| HDD disk seek | 10 ms |
| Network round trip (cross-continent) | 100 ms |

### Throughput

| System | Throughput |
|---|---|
| Kafka (per partition, small messages) | 1M messages/sec |
| Kafka (per broker, sustained) | 100 MB/sec |
| Spark (typical batch processing) | 1 TB/hour |
| Kinesis (per shard) | 1 MB/sec or 1,000 records/sec |
| S3 (single prefix read) | 5 GB/sec |
| BigQuery (per slot) | ~100 GB/slot/hour scan |
| Postgres (typical OLTP) | 10K transactions/sec |
| Redis (in-memory operations) | 100K operations/sec |

### Storage

| Data | Size |
|---|---|
| 1 event (JSON) | 500 bytes - 2 KB typical |
| 1 row (columnar format) | 50 - 200 bytes typical |
| 1M rows (columnar) | 50 - 200 MB |
| 1B rows (columnar) | 50 - 200 GB |
| 1 day at 10K events/sec (compressed Parquet) | ~1 GB |
| 1 year at 10K events/sec (compressed Parquet) | ~365 GB |

### Cost (approximate, 2024 pricing)

| Service | Cost |
|---|---|
| S3 storage | $0.023/GB/month |
| BigQuery storage (active) | $0.02/GB/month |
| BigQuery query (on-demand) | $5/TB scanned |
| Snowflake compute | $2-4/credit (~1 XS warehouse-hour) |
| Kafka (MSK) | $0.10/GB in + $0.05/GB out |
| Lambda | $0.20/1M invocations + $0.0000167/GB-sec |

## Worked Estimation Examples

### Example 1: Event Pipeline for an E-Commerce Site

**Given:** 10M daily active users, average 20 events per user per day.

**Step 1 - Event counts:**
- 10M users * 20 events = 200M events/day

**Step 2 - Throughput:**
- 200M / 86,400 sec = ~2,300 events/sec average
- Peak (assume 3-5x average): ~10K events/sec
- At 500 bytes/event: ~5 MB/sec sustained, ~20 MB/sec peak

**Step 3 - Storage:**
- Raw: 200M events * 500 bytes = 100 GB/day
- Compressed Parquet (4:1 ratio): ~25 GB/day
- Yearly: 25 GB * 365 = ~9 TB/year compressed

**Step 4 - Bottleneck:**
- Ingestion: 10K events/sec peak is well within a single Kafka partition
  (1M/sec capacity). Not the bottleneck.
- Storage: 9 TB/year is modest. S3 handles this trivially.
- Processing: 25 GB/day is small for Spark batch. A single job runs in
  minutes.
- The bottleneck is not technical here. It is cost and operational simplicity.

**Step 5 - Design decision:**
- This is a moderate-scale pipeline. Hourly batch processing is fine unless
  real-time dashboards are required.
- S3 storage cost: 9 TB * $0.023/GB = ~$207/month for year 1
- Single Kafka topic with 3-6 partitions handles the throughput with headroom
- Spark batch job on hourly schedule processes ~1 GB per run

### Example 2: Data Warehouse for a B2B SaaS

**Given:** 50K customer accounts, 500 users average per account, 25M total
users.

**Step 1 - Data volumes:**
- Events table: 10B rows/year (product analytics, user actions)
- Users table: 25M rows
- Accounts table: 50K rows
- Supporting dimension tables: relatively small

**Step 2 - Throughput:**
- 10B events/year = ~27M events/day = ~320 events/sec average
- Peak: ~1,500 events/sec
- Write volume is modest for any modern warehouse

**Step 3 - Storage:**
- Events: 10B rows * 100 bytes (columnar) = 1 TB/year
- Full warehouse after transforms and aggregations: ~2 TB
- Growing roughly 1 TB/year

**Step 4 - Bottleneck:**
- Not ingestion (low throughput)
- Not storage (2 TB is small)
- Query performance: typical analyst query scans 10-50 GB. This is the
  component that determines cost and user experience.

**Step 5 - Design decision:**
- BigQuery on-demand: at $5/TB scanned, a 10-50 GB query costs $0.05-$0.25.
  At 100 queries/day, that is $5-$25/day or $150-$750/month.
- Snowflake with auto-suspend XS warehouse: similar cost profile with more
  predictable billing.
- No need for dedicated infrastructure at this scale. Managed services are
  the right call. Partition the events table by date to keep query costs
  down through partition pruning.

### Example 3: Real-Time Dashboard with 5-Second Freshness

**Given:** Source Kafka topic at 50K events/sec, dashboard showing 10 metrics
aggregated over the last 5 minutes.

**Step 1 - Event counts:**
- 50K events/sec * 300 sec (5-minute window) = 15M events in the active
  window
- Each event: 200 bytes

**Step 2 - Throughput:**
- 50K events/sec sustained = 10 MB/sec
- Kafka handles this comfortably on a few partitions

**Step 3 - State size:**
- Active window: 15M events * 200 bytes = 3 GB
- For 10 aggregation metrics, the state is much smaller (counters, sums,
  HLL sketches) but the raw throughput is 3 GB in the window

**Step 4 - Bottleneck:**
- Processing: maintaining aggregations at 50K events/sec with 5-second
  freshness. This requires stream processing, not micro-batch.
- State: 3 GB fits in a single Flink TaskManager's memory. Not the
  bottleneck unless we add many more metrics.

**Step 5 - Design decision:**
- Flink with event-time processing and watermarks. State size (3 GB) fits
  in a single TaskManager. For 5-second freshness, use processing-time
  triggers with event-time windows.
- Results write to Redis for dashboard serving (100K reads/sec capacity is
  far more than dashboard needs).
- If freshness requirement relaxes to 1 minute, Spark Structured Streaming
  micro-batch becomes viable and operationally simpler.

## Common Estimation Mistakes

**Forgetting compression ratios.** Raw JSON is 3-5x larger than compressed
Parquet. If you estimate storage on raw sizes, your numbers will be 3-5x too
high. Always state whether you are talking about raw or compressed sizes.

**Using average throughput without considering peaks.** Systems must handle
peak load, not average. Design for 3-5x average throughput. An e-commerce site
with 2,300 events/sec average might hit 10K during a flash sale and 50K on
Black Friday.

**Ignoring retention policy.** "How long do we keep the data?" changes storage
costs dramatically. 1 TB/year with 7-year retention is 7 TB. With a 90-day
hot tier and cold storage after that, the cost profile changes completely.

**Not converting between units consistently.** Events/sec to GB/day requires
multiplying by event size and 86,400 seconds. It is easy to drop a factor.
Write out the full calculation:

```
10K events/sec
  * 500 bytes/event
  * 86,400 sec/day
  = 432 GB/day raw
  / 4 (compression)
  = 108 GB/day compressed
```

**Forgetting that storage cost compounds.** 100 GB/day seems cheap. After a
year, that is 36.5 TB sitting in storage. On S3 at $0.023/GB/month, that is
$840/month just for storage, growing every month. Always multiply by your
retention period.
