# Ingestion Patterns

Data ingestion is where every pipeline starts. The choice between batch,
streaming and hybrid determines the architecture, cost and complexity of
everything downstream. Before picking a technology, ask: what latency does the
business need?

## Pattern 1: Batch Ingestion

Batch ingestion processes data in scheduled chunks. It is the simplest pattern,
the cheapest to run and the right default unless requirements demand otherwise.

### Full Load (Truncate and Reload)

Drop the target table and reload from source. No watermark tracking, no
incremental logic. Just a clean copy every run.

**When to use:** Small tables (under 10M rows), slowly changing reference data,
sources that do not expose change tracking. A 10M row table at 200 bytes/row
is 2 GB. Spark loads that in under 2 minutes.

**Tradeoff:** Simple and reliable but wastes compute on unchanged data. Fine at
2 GB. Painful at 200 GB.

### Incremental Load

Process only new or changed records since the last run. Requires a reliable
watermark: an `updated_at` timestamp, an auto-incrementing ID or a change
sequence number.

**When to use:** Large tables where full loads are too expensive. A 1 TB table
with 1% daily changes means processing 10 GB instead of 1 TB.

**Risks:** Watermark gaps (records updated between query start and watermark
capture), clock skew between source systems and missed deletes (a deleted
row has no `updated_at`).

### Snapshot Comparison

Extract the full table today, compare to yesterday's snapshot and detect
inserts, updates and deletes by diffing the two copies.

**When to use:** Sources with no reliable watermark, requirements to detect
deletes, regulatory environments needing full audit trails.

**Tradeoff:** Expensive (two full copies compared row by row) but the most
reliable approach when the source cannot tell you what changed. At 1 TB,
this comparison takes roughly 10-20 minutes in Spark.

### Batch Sizing and Technologies

Spark processes roughly 1 TB/hour on a moderately sized cluster. A nightly
batch window of 6 hours handles 6 TB comfortably. Common orchestration:
Airflow triggering Spark jobs, dbt for SQL transforms, Fivetran or Airbyte
for managed connectors.

## Pattern 2: Change Data Capture (CDC)

CDC captures individual changes from a source database and streams them
downstream. It bridges the gap between batch and full streaming.

### Log-Based CDC

Read the database transaction log directly (MySQL binlog, Postgres WAL,
SQL Server change tracking). Every INSERT, UPDATE and DELETE is captured in
order with no impact on application queries.

```
Source DB --> Transaction Log --> Debezium --> Kafka --> Sink
   |                                                     |
   |  (< 1% overhead)                    (seconds delay) |
   +--- Application queries unaffected ---               v
                                              Warehouse / Lake
```

Debezium on MySQL sustains roughly 10K changes/sec with under 1% overhead
on the source database. Changes appear in Kafka within seconds.

### Trigger-Based CDC

Database triggers fire on each change and write to a change table. No log
access needed but adds write overhead to every transaction on the source.

**When to use:** Legacy databases where log access is restricted. Adds 10-30%
write overhead depending on trigger complexity.

### Timestamp-Based CDC

Query `WHERE updated_at > last_run_timestamp`. The simplest CDC approach but
misses deletes entirely and is vulnerable to clock skew.

**When to use:** Quick implementation when log access is unavailable and
deletes are handled separately (soft deletes or periodic full snapshots).

### Choosing a CDC Approach

Log-based is the gold standard: low overhead, captures deletes, preserves
ordering. Use it when available. Fall back to timestamp-based for simplicity
or trigger-based for legacy systems. Technologies: Debezium (open source),
AWS DMS, Fivetran CDC, Striim.

## Pattern 3: Event Streaming

Event streaming handles data as a continuous flow of events rather than
scheduled batches.

### Publish/Subscribe

Producers write events to topics. Consumers read independently at their own
pace. Multiple consumers can process the same events for different purposes:
one for analytics, one for alerting, one for ML features.

### Event Sourcing

The event stream is the source of truth. Current state is derived by replaying
events from the beginning. Every change is an immutable event, giving you a
complete audit trail and the ability to rebuild state at any point in time.

**When to use:** Systems where the history of changes matters as much as
current state. Financial systems, audit-heavy domains, systems requiring
temporal queries.

### Key Concepts

**Partitioning:** Events with the same key go to the same partition,
guaranteeing ordering per key. Choose partition keys that match your
processing needs (user_id for user-level aggregations, region for
geographic processing).

**Consumer groups:** Multiple consumers in a group split the partitions
among themselves. Adding consumers scales throughput linearly up to the
partition count.

**Offset management:** Track which events each consumer has processed.
Commit offsets after processing for at-least-once delivery. Commit before
processing for at-most-once. See `foundations/tradeoff_framework.md` for the
idempotent vs at-most-once tradeoff.

### Throughput Numbers

| System | Throughput |
|---|---|
| Kafka (per partition) | 1M messages/sec (small messages) |
| Kafka (per broker) | 100 MB/sec sustained |
| Kinesis (per shard) | 1 MB/sec or 1,000 records/sec |
| Pub/Sub (per topic) | 200 MB/sec |

## Pattern 4: API Ingestion

Most third-party data enters through APIs. The challenge is not the
integration itself but handling rate limits, pagination and failure gracefully.

### Polling

Scheduled requests to REST or GraphQL endpoints. Simple, predictable and
works within rate limits. Typical SaaS API rate limits: 100-1,000
requests/minute. At 100 records per request, that is 10K-100K records/minute.

### Webhooks

The source pushes events to your endpoint as they happen. Lower latency than
polling but requires your endpoint to be highly available. If your endpoint is
down when the webhook fires, you may lose data unless the source retries.

### Bulk Export

Request a full data dump, wait for it to be prepared, download as a file.
For large datasets where record-by-record API calls would take hours.
Salesforce bulk API, Stripe data exports and GitHub archive downloads all
use this pattern.

### Handling API Challenges

**Pagination:** Prefer cursor-based over offset-based. Offset pagination
breaks when records are inserted or deleted during iteration. Cursor-based
pagination uses a stable pointer and handles concurrent changes. At 100
records per page, extracting 1M records requires 10K API calls. With a
1,000 requests/minute rate limit, the full extract takes about 10 minutes.

**Rate limiting:** Implement exponential backoff (wait 1s, 2s, 4s, 8s on
consecutive failures). Queue requests and process within rate windows.
Parallelize up to the rate limit but not beyond. Track rate limit headers
(X-RateLimit-Remaining, Retry-After) to avoid hitting limits preemptively.

**Idempotency:** Track which API responses have been processed. Store the
last cursor position or page token. If the pipeline restarts, resume from
the last checkpoint rather than starting over.

## Pattern 5: File-Based Ingestion

Files dropped to landing zones remain common for partner integrations,
legacy system exports and regulatory data feeds.

### Landing Zones

External systems drop files to S3, GCS or SFTP. The pipeline watches for new
files and processes them on arrival.

**File watching:** S3 event notifications trigger Lambda or an SQS queue. GCS
Pub/Sub notifications trigger Cloud Functions. SFTP requires polling (check
for new files every N minutes).

### File Format Considerations

| Format | Pros | Cons |
|---|---|---|
| CSV | Ubiquitous, human-readable | No schema, no types, delimiter issues |
| JSON | Nested structures, self-describing | Verbose, slow to parse at scale |
| Parquet | Columnar, typed, compressed | Not human-readable, write-once |

For ingestion from external sources, accept whatever format they provide (often
CSV). Convert to Parquet in the first transformation step. The 3-5x compression
ratio and columnar read performance pay off immediately.

### Idempotency for File Processing

Track processed files in a manifest table or by renaming files after
processing (move from `incoming/` to `processed/`). If the pipeline restarts,
check the manifest before reprocessing. Without this, duplicate processing
is inevitable.

**File arrival monitoring:** Set up alerts if expected files have not arrived
within the SLA window (e.g. partner feed expected by 6 AM daily). Track file
sizes over time. A file that is normally 500 MB arriving at 5 KB signals a
truncated export from the source system.

## Choosing Between Patterns

| Requirement | Recommended Pattern |
|---|---|
| Latency < 1 second | Event streaming |
| Latency < 5 minutes | CDC or micro-batch |
| Latency < 1 hour | Incremental batch |
| Full historical loads | Snapshot comparison |
| Third-party SaaS data | API ingestion |
| External partner feeds | File-based ingestion |
| No source change tracking | Snapshot comparison |
| Multiple downstream consumers | Event streaming |

## Connection to Interview

When asked "how would you ingest data from [source]?", resist the urge to
jump straight to Kafka. Instead:

1. Clarify the latency requirement (seconds, minutes, hours)
2. Ask about the source type (database, API, files, event stream)
3. Ask about change detection capabilities (CDC logs, timestamps, none)
4. Pick the simplest pattern that meets the requirement

Apply the tradeoff framework from `foundations/tradeoff_framework.md`: state
your choice, explain why, name the alternative and acknowledge the downside.
A batch pipeline that meets the SLA is better than a streaming pipeline that
adds complexity without business value.
