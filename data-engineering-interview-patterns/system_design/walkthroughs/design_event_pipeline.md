# Walkthrough: Design an Event Ingestion Pipeline

**Prompt:** "Design an event ingestion pipeline for a mobile app with 10M
daily active users."

This walkthrough simulates a full 45-minute system design interview. It
follows the communication framework from `foundations/communication_framework.md`
and references patterns and numbers from the foundations and patterns sections.

---

## Phase 1: Clarify Requirements (Minutes 0-5)

Do not start drawing. Start asking. The interviewer deliberately leaves the
prompt vague to see whether you clarify before designing.

### Questions to Ask

**Data questions:**
- "What types of events are we ingesting? App opens, screen views, button
  clicks, purchases, errors?"
- "What's the expected event volume per user per day?"
- "What format do events arrive in? JSON from a mobile SDK?"

**Consumer questions:**
- "Who consumes this data? Analytics team, ML models, real-time dashboards?"
- "What's the latency requirement? Do any consumers need real-time data, or
  is hourly/daily sufficient?"

**Operational questions:**
- "What's the retention policy? How long do we keep raw events?"
- "Any compliance requirements? PII handling, GDPR, data residency?"
- "What cloud provider is the company on?"

### Establishing Requirements

After the interviewer answers (or you state assumptions), summarize what you
are working with:

"Let me summarize the requirements before I start designing:

- 10M DAU with roughly 30 events per user per day
- That gives us 300M events/day, or about 3,500 events/sec average
- Assuming 3-5x peak factor, we need to handle ~15K events/sec at peak
- Event size: ~500 bytes JSON
- Daily volume: ~150 GB raw JSON, ~40 GB compressed Parquet
- Yearly volume: ~15 TB compressed
- Three consumer groups: analytics team needs hourly dashboards, ML team
  needs daily feature pipelines, fraud team needs sub-minute alerting
- Retention: 30 days hot, 1 year warm, 7 years cold (compliance)

Given the dual latency requirement (sub-minute for fraud, hourly for
analytics), I'll design a dual-path architecture: streaming for real-time
consumers and batch for analytics."

This takes about 2 minutes to say. The interviewer now knows you understand
the scale and have a plan.

**Cost context:** At 150 GB/day raw and 40 GB/day compressed, yearly storage
is roughly 15 TB. At $0.023/GB on S3, that is about $345/month for the
first year. The compute cost depends on the processing framework, which
we will choose in the next phase."

---

## Phase 2: High-Level Design (Minutes 5-10)

Draw the skeleton with 5-7 components. Name specific technologies and explain
the data flow in one pass.

### Architecture

```
Mobile App ──▶ API Gateway ──▶ Kafka (12 partitions, 7-day retention)
                                  │
                                  ├──▶ Flink ──▶ Redis ──▶ Fraud Dashboard
                                  ├──▶ Spark (hourly) ──▶ S3 (Parquet) ──▶ Warehouse
                                  └──▶ S3 raw archive (7-year retention)
```

### Component Justification (30 seconds each)

"**API Gateway:** Handles authentication, rate limiting and basic event
validation before events hit Kafka. Rejects malformed events early.

**Kafka:** Central event bus. Decouples producers from consumers. At 15K
events/sec peak with 500-byte messages, that's ~7.5 MB/sec. Well within a
single broker's 100 MB/sec capacity. I'd start with 12 partitions for
parallelism headroom.

**Flink (streaming path):** Processes events in real-time for the fraud team.
Handles windowed aggregations with sub-second latency.

**Spark (batch path):** Runs hourly to transform raw events into Parquet on
S3 and load into the warehouse. Hourly batch is sufficient for the analytics
team's dashboards. Each hourly run processes roughly 12.5M events (6.25 GB
raw), finishing in 2-5 minutes on a small cluster.

**S3:** Durable storage for both raw archive (JSON, 7-year retention) and
processed data (Parquet, partitioned by date).

**Warehouse (Snowflake or BigQuery):** Serves the analytics team and ML
feature pipelines. At 15 TB/year, warehouse costs are roughly $5/TB scanned
in BigQuery or ~$200-500/month in Snowflake depending on query volume.

**Why dual-path over streaming-only:** A pure streaming architecture
(everything through Flink) would work but adds complexity for the analytics
team, which only needs hourly data. The batch path is cheaper (spot
instances, no always-on compute) and simpler to debug. Apply the principle
from `foundations/tradeoff_framework.md`: pick the simplest architecture
that meets each consumer's requirements."

---

## Phase 3: Deep Dive (Minutes 10-30)

The interviewer will pick 1-2 areas. Here are the common deep-dive topics for
this design and how to discuss each.

### Deep Dive: Kafka Design

"For Kafka topic design, I'd create a single `mobile-events` topic with 12
partitions. At 15K events/sec peak, that's about 1,250 events/sec per
partition, well under Kafka's 1M messages/sec per partition capacity.

**Partition key:** I'd partition by user_id. This guarantees ordering per user,
which matters for session analysis and fraud detection. The tradeoff is
potential skew if some users generate far more events than others. At 10M
users, the distribution should be even enough. If we see skew, we can switch
to random partitioning and handle ordering in the consumer.

**Retention:** 7 days on Kafka. This gives us a replay buffer if a consumer
falls behind or we need to reprocess. For long-term retention, raw events
flow to S3.

**Consumer groups:** Three separate consumer groups (fraud-flink, spark-batch,
raw-archive). Each reads independently at its own pace. The fraud consumer
processes events within milliseconds. The batch consumer reads in hourly
micro-batches. The archive consumer writes raw JSON to S3 continuously.

**Replication factor:** Set to 3 across at least 2 availability zones. This
means each message is stored on 3 brokers. Storage cost triples, but at
7.5 MB/sec, 7 days of retention with RF=3 is roughly 14 TB. On gp3 EBS
volumes at $0.08/GB, that is about $1,120/month for broker storage. A
reasonable cost for the durability guarantee.

**Topic configuration:** Set `min.insync.replicas=2` and
`acks=all` on the producer. This ensures no acknowledged message is lost
even if one broker fails. The tradeoff is slightly higher producer latency
(~5ms vs ~1ms with acks=1), but at 15K events/sec the added latency is
negligible."

### Deep Dive: Schema Management

"I'd use Avro with a schema registry. Each event type (app_open, purchase,
click) has a registered schema. The mobile SDK serializes events using Avro,
which gives us typed data and smaller payloads than JSON (~40% smaller).

**Backward compatibility:** The schema registry enforces backward compatibility.
New fields must have defaults. Consumers using an older schema can still read
events with new fields. This lets us evolve the event schema without
coordinating deployments across mobile apps and consumers.

**Breaking changes:** If we need to rename a field or change a type, we create
a new topic version (mobile-events-v2) and run both in parallel during the
migration period. See [`patterns/data_modeling_patterns.md`](../patterns/data_modeling_patterns.md) for schema
evolution patterns.

**Schema overhead:** Avro with a schema registry adds a 5-byte header per
message (magic byte + 4-byte schema ID). At 300M events/day, that is 1.5 GB
of overhead per day. Negligible compared to the ~40% payload savings over
JSON."

### Deep Dive: S3 Layout and File Format

"Raw events land in S3 with this path structure:

```
s3://data-lake/events/raw/year=2024/month=01/day=15/hour=08/
s3://data-lake/events/processed/year=2024/month=01/day=15/
```

Processed files are Parquet with Snappy compression, targeting 128 MB per
file. At 40 GB/day compressed, that is roughly 312 files per day. Over a
year, the processed layer accumulates about 114K files. Iceberg or Delta
Lake metadata handles this file count without S3 LIST performance issues.

Hourly raw partitions let us reprocess specific hours if needed. Daily
processed partitions match the analytics team's query patterns (they almost
always filter by date). This aligns with the partitioning guidance in
[`patterns/scale_and_performance.md`](../patterns/scale_and_performance.md)."

### Deep Dive: Exactly-Once Semantics

"For the streaming path, we need to avoid both duplicate events and lost
events.

**Producer side:** Kafka's idempotent producer (enable.idempotence=true)
prevents duplicates from network retries. The API gateway assigns a unique
event_id before publishing.

**Consumer side:** Flink's checkpointing with Kafka's transactional consumer
gives exactly-once processing. Flink snapshots its state and Kafka offsets
atomically every 30 seconds.

**Batch path:** The Spark job uses INSERT OVERWRITE on hourly partitions.
If it reruns the same hour, it overwrites rather than appends. This makes
the batch path idempotent by design. See [`patterns/pipeline_architecture.md`](../patterns/pipeline_architecture.md)
for more on idempotency patterns."

---

## Phase 4: Scaling and Edge Cases (Minutes 30-40)

### 10x Scale (100M DAU)

"At 100M DAU, we're looking at 3B events/day, ~35K events/sec average, ~150K
peak. Let me walk through what changes:

- **Kafka:** Increase from 12 to 48+ partitions. Add brokers. 150K events/sec
  at 500 bytes = 75 MB/sec, still within a 3-broker cluster's capacity.
- **Spark:** Increase executors and memory. 400 GB/day compressed is still
  manageable for hourly batch (~17 GB per run).
- **S3:** Scales infinitely. No changes needed.
- **Flink:** Add TaskManagers. The fraud detection logic is stateless per
  event, so it scales linearly with partition count.
- **Warehouse:** Larger warehouse size or more slots. Query costs increase
  linearly with data volume, so partitioning and clustering become critical."

### Late-Arriving Events

"Mobile events can arrive late due to offline usage. A user on airplane mode
generates events that arrive hours later.

**Streaming path:** Flink uses event-time processing with watermarks. I'd set
a watermark delay of 30 seconds for the real-time fraud dashboard. Events
arriving later than 30 seconds are dropped from the real-time aggregation
(acceptable for dashboards).

**Batch path:** Late events land in whatever hour they arrive. A nightly
reconciliation job can re-process affected partitions to ensure completeness.
For the analytics use case, next-day accuracy is sufficient.

**Quantifying lateness:** In practice, 95% of mobile events arrive within
5 seconds, 99% within 60 seconds and 99.9% within 5 minutes. The remaining
0.1% (300K events/day at our scale) trickle in over hours due to offline
sessions. The nightly reconciliation job catches these."

### Failure Scenarios

"**Kafka broker failure:** With replication factor 3, the cluster survives
losing one broker. Producers automatically redirect to the new leader.

**Flink failure:** Checkpoints let Flink recover from the last consistent
state. The gap between checkpoint and failure (up to 30 seconds) is replayed
from Kafka.

**Spark job failure:** Idempotent hourly partitions mean we retry the failed
hour. Downstream tasks wait automatically in Airflow.

**Unparseable events:** A dead letter queue captures events that fail schema
validation. These are investigated separately rather than blocking the
pipeline.

**Monitoring:** Track three key metrics: ingestion lag (difference between
event timestamp and processing time), consumer group offset lag (how far
behind each consumer is) and dead letter queue depth (how many events are
failing validation). Alert if ingestion lag exceeds 5 minutes, offset lag
exceeds 100K messages or the DLQ receives more than 0.1% of total events."

### Cost Estimate

"At current scale (300M events/day):
- **Kafka (MSK):** ~15 GB/day ingress. At $0.10/GB: ~$45/month
- **S3 storage:** 15 TB/year. At $0.023/GB: ~$345/month for year 1
- **Spark (EMR):** 2-hour daily job on 5 m5.xlarge instances: ~$150/month
- **Flink:** 2 always-on m5.large instances: ~$130/month
- **Warehouse:** Depends on query volume, but ~$200-500/month at this scale

Total: roughly $900-1,200/month. At 10x scale, expect roughly $5,000-8,000/month.

**Cost optimization levers:** Use Kafka tiered storage to move data older
than 24 hours to S3 (reduces broker disk by 80%). Run Spark on spot instances
(60-90% savings on compute). Use S3 Intelligent-Tiering for the raw archive
to move infrequently accessed data to cheaper storage classes automatically."

---

## Phase 5: Wrap Up (Minutes 40-45)

"To summarize the key decisions:

1. **Dual-path architecture** (streaming + batch) because we have two
   distinct latency requirements. The tradeoff is operational complexity of
   maintaining two paths, but the alternative (streaming for everything) is
   more expensive and complex for the analytics use case that only needs
   hourly data.

2. **Kafka as the central event bus** because it decouples producers from
   consumers, provides replay capability and handles our throughput with
   headroom. The tradeoff vs Kinesis is more operational overhead but more
   control over partitioning and retention.

3. **Parquet on S3 for the batch path** because columnar format with
   compression gives us 4x storage savings and fast analytical queries.

4. **Event-time processing in Flink** for the streaming path, with watermarks
   to handle late events. The tradeoff is dropping events that arrive more
   than 30 seconds late from real-time aggregations.

With more time, I'd design the data quality layer in more detail (row count
checks after each batch run, freshness monitoring on the warehouse tables)
and the PII handling strategy (pseudonymization in the transformation layer,
access controls on raw data)."
