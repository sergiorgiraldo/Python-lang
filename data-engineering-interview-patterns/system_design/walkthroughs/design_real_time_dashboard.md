# Walkthrough: Design a Real-Time Analytics Dashboard

**Prompt:** "Design a system that powers a real-time analytics dashboard with
5-second data freshness."

This walkthrough simulates a full 45-minute system design interview. The
5-second freshness requirement makes this a streaming-first design. The
key challenge is not the processing speed but maintaining accuracy and
managing state at high throughput.

---

## Phase 1: Clarify Requirements (Minutes 0-5)

### Questions to Ask

**Metric questions:**
- "What metrics does the dashboard display? Page views, active users,
  conversion rate, revenue, error rate?"
- "What dimensions can users filter by? Country, device type, traffic source,
  page category?"
- "What time windows are shown? Last 5 minutes, last hour, last 24 hours?"

**Scale questions:**
- "What's the event volume? How many events per second?"
- "How many concurrent dashboard viewers?"
- "Is this internal only or customer-facing?"

**Accuracy questions:**
- "Is approximate accuracy acceptable? For example, unique user counts with
  1-2% error?"
- "How should late-arriving events be handled? Update the dashboard or drop
  them?"

### Establishing Requirements

"Here's what I'm working with:

- **Metrics:** 10 dashboard metrics (page views, unique visitors, sessions,
  add-to-cart rate, conversion rate, revenue, average order value, error rate,
  bounce rate, active users)
- **Dimensions:** 4 filterable dimensions (country, device type, traffic source,
  page category). Each dimension has 10-50 distinct values.
- **Source:** Web events via Kafka at 50K events/sec sustained, 150K peak
- **Freshness:** Dashboard data must reflect events no more than 5 seconds behind real-time
- **Time windows:** Rolling 5 minutes, rolling 1 hour, rolling 24 hours
- **Viewers:** ~50 concurrent internal users
- **Accuracy:** 1-2% error on unique counts is acceptable

**Capacity math:**
- 50K events/sec * 200 bytes/event = 10 MB/sec throughput
- 5-minute window: 50K * 300 = 15M events, 3 GB
- 1-hour window: 50K * 3,600 = 180M events, 36 GB
- 24-hour window: 50K * 86,400 = 4.3B events, 864 GB

The 24-hour window is too large to hold in memory as raw events. We need
pre-aggregation to keep state manageable."

---

## Phase 2: High-Level Design (Minutes 5-10)

### Architecture

```
Web Server ──▶ Kafka (24 partitions)
                  │
                  ├──▶ Flink ──▶ Redis (metrics) ──▶ Dashboard API ──▶ UI
                  │         └──▶ Druid (drill-down)
                  └──▶ S3 (raw archive) ──▶ Warehouse (batch analytics)
```

### Component Justification

"**Kafka (24 partitions):** At 50K events/sec and 200 bytes each, that's 10
MB/sec. With 24 partitions, each handles about 2K events/sec. This leaves
significant headroom for peak traffic. Partition by a hash of the event to
distribute evenly (not by user_id since we are aggregating across all users).

**Flink:** Stream processor that computes the 10 metrics in real-time. Flink
handles event-time processing, windowing and state management. I chose Flink
over Spark Structured Streaming because we need sub-5-second latency. Spark's
micro-batch model adds latency at each batch boundary.

**Redis:** Stores pre-aggregated metric values. The dashboard reads from Redis,
not from the event stream. At 50 concurrent users refreshing every 5 seconds,
that's 10 reads/sec per user, or 500 reads/sec total. Redis handles 100K
ops/sec, so this is trivial.

**Druid (optional):** If the dashboard needs drill-down capability (filter by
specific country and device type), Druid provides sub-second OLAP queries on
streaming data with typical p99 latency of 50-200ms for aggregation queries.
If drill-down is not needed, Redis alone is sufficient.

**S3 raw archive:** Every event is also written to S3 as Parquet for
backfill, historical analysis and investigation when metrics look wrong.
At 10 MB/sec, the raw archive grows by 864 GB/day or roughly 26 TB/month
before compression. With Parquet compression (3-4x), long-term storage is
roughly 7 TB/month."

---

## Phase 3: Deep Dive (Minutes 10-30)

### Deep Dive: Flink Topology

"The Flink job has three stages:

**Stage 1: Parse and validate.** Deserialize Avro events, validate required
fields, route invalid events to a dead letter topic. This catches malformed
events before they corrupt aggregations.

**Stage 2: Key and window.** Key events by the dimension combinations needed
for dashboard filters. For 4 dimensions with 10-50 values each, the total
key space is manageable (roughly 10K-100K distinct combinations).

**Stage 3: Aggregate and emit.** For each key, maintain running aggregations:
- Counters: page views, sessions, errors (simple increment)
- Unique counts: HyperLogLog for unique visitors (~1% error, 16 KB per sketch)
- Rates: conversion rate = purchases / sessions (two counters, divide at read)
- Revenue: running sum

Results emit to Redis every 5 seconds using processing-time triggers.

**Window strategy:** I'd use sliding windows rather than tumbling for smoother
dashboard updates. A 5-minute sliding window with 5-second slide steps means
the dashboard always shows the most recent 5-minute aggregate, updated every
5 seconds."

### Deep Dive: State Management

"The critical question is how much state Flink needs to maintain.

**5-minute window state:** For each of the ~50K dimension key combinations:
counters (8 bytes each) and HLL sketches (16 KB each). Total: 50K * 16 KB =
~800 MB. Fits in a single TaskManager's heap.

**1-hour window state:** Same structure, 12x the events. But since we are
maintaining aggregates (not raw events), the state size is the same: ~800 MB.
The HLL sketch size does not grow with event count.

**24-hour window state:** Again ~800 MB for aggregates. This is the advantage
of pre-aggregation over storing raw events. The 864 GB of raw events in a
24-hour window compresses to under 1 GB of aggregate state.

**State backend:** RocksDB for resilience. State survives TaskManager restarts.
Checkpointing every 30 seconds to S3 ensures we can recover within a minute
after any failure.

HyperLogLog is the key enabler here. Exact unique counts would require
storing every distinct user_id in the window (potentially millions of IDs).
HLL gives us 1% error with 16 KB per sketch. See
[`patterns/11_probabilistic_structures/`](../../patterns/11_probabilistic_structures/README.md) for HLL implementation details."

### Deep Dive: Redis Data Model

"Redis stores pre-computed metric values that the dashboard reads directly.

**Key structure:**
`metrics:{window}:{dimension_key}:{metric_name}`

Example: `metrics:5m:US:mobile:organic:page_views` stores the 5-minute page
view count for US mobile organic traffic.

**Data types:**
- Counters: Redis strings with INCRBY for atomic updates
- HLL results: Redis strings storing the estimated count
- Rates: Two counters (numerator, denominator), division happens at read

**TTL:** Each key gets a TTL matching its window duration plus buffer.
5-minute keys expire after 10 minutes. 24-hour keys expire after 48 hours.
This prevents stale data from accumulating.

**Dashboard read pattern:** The API server reads all metrics for the
current filter combination in a single Redis MGET. At 10 metrics per
request, that's 10 Redis operations batched into 1 round trip: sub-1ms
response time."

### Deep Dive: Exactly-Once Processing

"Duplicate events would inflate metrics. Missing events would deflate them.
Both are visible on a real-time dashboard.

**Flink to Kafka:** Flink's checkpoint mechanism ensures exactly-once
consumption. If Flink fails mid-checkpoint, it replays from the last
committed offset.

**Flink to Redis:** Redis writes are idempotent if we use SET (overwrite the
entire value) rather than INCRBY (increment). Each Flink checkpoint writes
the complete aggregate value for each key. On replay after failure, the same
value is written again, not added again.

This means we trade eventual accuracy for exact correctness: during a
recovery window (up to 30 seconds), the dashboard may show slightly stale
data but will never show inflated numbers."

---

## Phase 4: Scaling and Edge Cases (Minutes 30-40)

### Traffic Spike (5x: Black Friday)

"At 250K events/sec, the Flink job needs 5x the throughput.

- **Kafka:** Increase partitions from 24 to 48. Pre-provision this before the
  event since partition increases require consumer group rebalancing.
- **Flink:** Scale from 4 to 12 TaskManagers. Flink's rescaling redistributes
  state across the new TaskManagers automatically.
- **Redis:** 500 reads/sec becomes 2,500 reads/sec. Still well under Redis's
  100K ops/sec capacity. No changes needed.

The key insight: pre-aggregation means dashboard read load does not increase
with event volume. Whether we process 50K or 250K events/sec, the dashboard
still reads the same number of pre-computed metric keys.

**Pre-scaling checklist:** Run a load test 2 weeks before Black Friday. Push
synthetic events at 5x throughput through a staging Kafka cluster and verify
Flink keeps up without dropping events. Validate Redis memory does not
exceed 70% capacity. Confirm S3 write throughput handles the increased
volume without throttling (S3 supports 3,500 PUT requests/sec per prefix).

**Cost at 5x:** Flink compute triples from $450 to ~$1,350/month. Kafka
adds 2 brokers at ~$300/month. Total steady-state cost at 5x scale is
roughly $3,500-4,500/month."

### Late-Arriving Events

"Web events can arrive late due to network delays, mobile connectivity issues
or client-side batching.

**Watermark strategy:** Set the watermark delay to 30 seconds. Events arriving
within 30 seconds of their event timestamp are included in the correct window.
Events arriving later are either:
- Dropped from real-time aggregations (acceptable for dashboards)
- Still written to S3 raw archive (nothing is lost permanently)

**Dashboard indicator:** The UI shows a small indicator with the current data
age. If watermark delay causes data to be 35 seconds old instead of 5, users
can see this. If the delay exceeds 60 seconds, an alert fires."

### Stale Data Detection

"The dashboard API checks the timestamp of the latest Redis write on each
request. If the latest write is older than 30 seconds, the dashboard displays
a 'data may be stale' warning. If older than 5 minutes, it displays an error
state.

This covers the scenario where Flink is down or falling behind. Rather than
showing confidently wrong numbers, the dashboard signals uncertainty.

### Dimension Cardinality Growth

"If the product team adds a new dimension (e.g. A/B test variant with 20
values), the key space multiplies. Going from 50K to 1M dimension
combinations increases Flink state from ~800 MB to ~16 GB per window. Still
manageable with RocksDB on disk, but query latency in Redis increases as
MGET operations grow. Monitor the dimension key count and alert if it
exceeds 500K. Add new dimensions only with an explicit review of the state
impact."

### Backfill After Logic Change

"When Flink processing logic changes (new metric, bug fix):

1. Deploy the new Flink job on the current stream
2. Run a Spark batch job against S3 raw events to recompute historical
   aggregations for the affected time range
3. Backfill the corrected values into Druid for historical drill-down

The raw event archive in S3 makes this possible. Without it, we could only
fix metrics going forward. See [`patterns/pipeline_architecture.md`](../patterns/pipeline_architecture.md) for
backfill patterns."

### Cost Estimate

"At 50K events/sec sustained:
- **Kafka (MSK, 3 brokers):** ~$500/month (broker cost + storage)
- **Flink (4 m5.xlarge on EKS):** ~$450/month
- **Redis (ElastiCache r6g.large):** ~$200/month
- **S3 raw archive:** 864 GB/day * 30 days * $0.023/GB = ~$600/month
- **Druid (if used, 3-node cluster):** ~$600/month

Total: roughly $1,800-2,400/month. The major cost is Flink compute and S3
storage. Reducing raw event retention from 30 to 7 days saves ~$450/month."

---

## Phase 5: Wrap Up (Minutes 40-45)

"Key design decisions and their tradeoffs:

1. **Pre-aggregation in Flink rather than raw event queries.** This is the
   core decision. Pre-aggregating reduces dashboard read latency to sub-1ms
   and keeps state manageable (under 1 GB vs 864 GB of raw events). The
   tradeoff is reduced flexibility: adding a new dimension requires changing
   the Flink job. But for a fixed-layout dashboard with known metrics, this
   is the right choice.

2. **HyperLogLog for unique counts.** Approximate counts with ~1% error use
   16 KB per sketch instead of potentially gigabytes for exact counts. The
   tradeoff is 1-2% error on unique visitor metrics, which the team has
   accepted.

3. **Redis for serving, not Druid alone.** Redis gives sub-1ms reads for
   pre-computed values. Druid adds drill-down capability but with 50-200ms
   query latency. For the primary dashboard view, Redis is the right choice.
   Druid handles the occasional drill-down query.

4. **30-second watermark delay.** Balances accuracy (includes most late
   events) against freshness (delays the dashboard by at most 30 seconds
   beyond the 5-second target). For an internal dashboard, this is
   acceptable.

With more time, I'd design the alerting system (automated alerts when metrics
cross thresholds), the A/B testing integration (how to show experiment-
specific metrics) and the disaster recovery strategy (multi-region Kafka
replication)."
