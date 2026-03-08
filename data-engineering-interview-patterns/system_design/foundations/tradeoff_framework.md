# Tradeoff Framework

Every system design answer is a series of tradeoff decisions. The interviewer
does not care which option you pick. They care that you can identify the
tradeoffs, articulate them clearly and make a reasoned choice given the
requirements.

The engineers who do well in these interviews are not the ones who memorize
architectures. They are the ones who can stand at a whiteboard and say "here
are the two options, here is why I am choosing this one and here is what we
give up."

## The Tradeoff Discussion Template

Use this 4-step structure every time you face a design decision. It takes about
30 seconds to say out loud and signals clear thinking to the interviewer.

```
1. State the decision: "We need to choose between X and Y"
2. Identify concerns: "X optimizes for [A] at the cost of [B]"
3. Evaluate: "Given our SLA requires [number], X fits because..."
4. Acknowledge downside: "We accept [tradeoff]. If [scenario], revisit."
```

Every step matters. Skipping step 4 makes you sound overconfident. Skipping
step 3 makes the decision feel arbitrary. Skipping step 2 means you are not
analyzing the tradeoff.

## Core Data Engineering Tradeoffs

### 1. Batch vs Streaming

**Batch processing** runs on a schedule (hourly, daily), processes accumulated
data in bulk and produces results with minutes-to-hours latency. It is simpler
to build, cheaper to run and easier to debug. Spark batch can process 1 TB in
roughly 10 minutes on a moderately sized cluster.

**Streaming processing** handles events as they arrive, producing results in
seconds to minutes. It is more complex (state management, watermarks, late
data handling), more expensive (always-on compute) and harder to debug. Flink
processes individual events in under 100ms. Kafka can sustain 1M messages/sec
per partition for small messages.

**Micro-batch** sits in the middle. Spark Structured Streaming processes data
in small batches (as low as 100ms intervals), giving near-real-time latency
with batch-like simplicity. Good enough for many "we need it faster than
hourly" requirements.

**Decision factor:** What latency does the business need? If the
dashboard refreshes hourly, streaming is wasted money and added complexity. If
traders need position updates within 5 seconds, batch will not work.

**Example:** An e-commerce analytics pipeline with 10K events/sec. The
marketing team checks dashboards each morning. Hourly batch is the right
choice: simpler, cheaper and the consumers do not need real-time data. If the
fraud detection team later needs sub-minute alerts, add a streaming path for
that specific use case rather than rebuilding the whole pipeline.

### 2. Normalized vs Denormalized

**Normalized models** (3NF) store each fact once. Less storage, easier updates
(change a customer name in one place), but queries require many joins. A
typical normalized query might join 5-8 tables to answer a business question.

**Denormalized models** (star schema, OBT) duplicate data for query
performance. More storage, harder updates (a customer name change touches
millions of rows), but queries are simpler and faster with fewer joins.

**Decision factor:** Read-heavy or write-heavy? Analytical warehouses are
overwhelmingly read-heavy (analysts run hundreds of queries per update cycle),
so denormalize. OLTP systems handling thousands of writes per second benefit
from normalization to avoid update anomalies.

**Example:** A star schema with a `fact_orders` table and `dim_customer`,
`dim_product`, `dim_date` dimensions. The customer name is stored in
`dim_customer` once, not repeated in every order row. This is the practical
middle ground: denormalized enough for fast queries, normalized enough that
dimension updates are manageable. See [`patterns/01_hash_map/`](../../patterns/01_hash_map/README.md) for the
algorithmic patterns behind efficient join operations.

### 3. Exact vs Approximate

**Exact computation** gives correct results but can be expensive. A
`COUNT(DISTINCT user_id)` on 1B rows requires sorting or hashing all values:
roughly 2 minutes and 2 GB of memory.

**Approximate computation** uses probabilistic structures to trade bounded
error for massive speed and memory gains. HyperLogLog computes approximate
distinct counts on 1B rows in about 2 seconds using 16 KB of memory, with
less than 2% error.

**Decision factor:** Who consumes the result? Executive dashboards showing
"~45M monthly active users" tolerate 1-2% error easily. Billing systems
charging per-event require exact counts. Regulatory reporting typically
requires exact numbers.

**Example:** A real-time dashboard showing unique visitors per page.
HyperLogLog in Redis gives sub-second responses with 0.81% standard error.
The monthly billing report for API usage runs an exact count as a nightly
batch job. Different consumers, different accuracy requirements. See
[`patterns/11_probabilistic_structures/`](../../patterns/11_probabilistic_structures/README.md) for implementation details on Bloom
filters, HyperLogLog and Count-Min Sketch.

### 4. Schema-on-Write vs Schema-on-Read

**Schema-on-write** enforces a schema at ingestion time. Bad data is rejected
before it enters the system. This protects downstream consumers but makes
schema evolution harder. Every source change requires updating the ingestion
schema.

**Schema-on-read** stores raw data (JSON, CSV, raw events) and applies schema
at query time. This is flexible and fast to set up, but risks bad data
propagating through the system undetected until someone queries it.

**Decision factor:** How fast does the schema change and how much do you trust
the source? A well-defined internal API with a stable schema: schema-on-write.
A third-party webhook that changes without notice: store raw, validate later.

**Modern approach:** "Schema-on-write for known, stable sources.
Schema-on-read for new or experimental sources." Many teams land raw data in a
bronze/raw layer (schema-on-read), then validate and conform it into a
silver/clean layer (schema-on-write). This gives you both flexibility and
safety. Delta Lake and Iceberg support schema enforcement and evolution to
make this practical.

### 5. Build vs Buy

**Building** gives full control, customization for your exact use case and no
vendor lock-in. It also means maintenance burden, hiring specialized
engineers and slower time to value.

**Buying** (managed services) gets you running fast with less operational
overhead. It also means vendor lock-in, less customization and recurring cost
that scales with usage.

**Decision factor:** Is this capability a differentiator for the business? If
yes, building may be worth the investment. If it is commodity infrastructure,
buy it and focus engineering effort on what makes the business unique.

**Example:** A fintech company building a custom ML feature store because
feature freshness and proprietary feature engineering are competitive
advantages: build. The same company choosing a warehouse for analytical
queries: buy Snowflake or BigQuery. Warehousing is not a differentiator, so
spend engineering time elsewhere.

### 6. Idempotent vs At-Most-Once

**Idempotent processing** produces the same result regardless of how many
times an operation runs. Safe to retry on failure. Requires more complex logic
(upserts, deduplication keys, check-then-write patterns) and higher write
cost.

**At-most-once processing** is simpler but risks data loss on failure. If a
write fails, the data is gone. No retries, no deduplication overhead.

**Decision factor:** What is the cost of duplicate data vs missing data?
Financial transactions: idempotent, always. Losing a payment record or
double-charging a customer is unacceptable. Clickstream analytics:
at-least-once delivery with downstream deduplication is often acceptable. A
few duplicate page views do not change business decisions.

**Example:** An order processing pipeline uses Kafka consumer offsets with
transactional writes to a database. Each batch commits the offset and the
database write atomically. If the consumer restarts, it replays from the last
committed offset and the upsert logic (keyed on order_id) prevents
duplicates. More complex than a simple insert, but safe to retry.

### 7. Partitioning Strategy: Time vs Hash vs Range

**Time partitioning** groups data by date or hour. Best for time-series
queries where filters almost always include a date range. Partition pruning
skips irrelevant partitions entirely. Risk: today's partition receives all
writes (hot partition problem).

**Hash partitioning** distributes data evenly across partitions using a hash
function. Even write distribution, but no benefit for range queries since
related rows scatter across partitions.

**Range partitioning** groups data by value ranges (customer_id 1-1000 in
partition 1, etc.). Good for range scans on the partition key, but risks skew
if the distribution is uneven.

**Decision factor:** What is the primary query pattern? If queries always
filter by date (and they usually do in DE), partition by date. If queries
filter by customer_id and customers vary wildly in data volume, hash
partitioning avoids hot partitions.

**Example:** An event analytics table partitioned by `event_date`. A query
for last week's data scans 7 partitions instead of the entire table. At 1 TB
total and 365 daily partitions, each partition is roughly 2.7 GB. A weekly
query scans ~19 GB instead of 1 TB. In BigQuery at $5/TB scanned, that is
$0.10 instead of $5.00 per query.

### 8. Push vs Pull Ingestion

**Push ingestion** means the source sends data to your pipeline (webhooks,
Kafka producers, event streams). Lower latency since data arrives as it is
produced. Requires the source to be reliable and your endpoint to be available.

**Pull ingestion** means your pipeline fetches data from the source (API
polling, database replication, file downloads). Higher latency but the
pipeline controls the pace. Easier to handle rate limits and backpressure.

**Decision factor:** Who controls the integration? If you own both sides, push
is typically simpler and lower latency. If integrating with a third-party API
that rate-limits you to 100 requests/minute, pull with a scheduled job is the
practical choice.

**Example:** Internal microservices publish events to Kafka (push). The
pipeline consumes from Kafka topics with no polling overhead. An external
vendor provides a REST API with daily data dumps. The pipeline polls this API
every hour (pull), handles rate limits and retries gracefully and does not
depend on the vendor implementing webhooks.

## How to Practice Tradeoff Discussions

For each tradeoff above, practice saying the 4-step template out loud. This
is not optional advice. Speaking your reasoning is a different skill from
thinking it and interviews require the spoken version.

**Practice method:**
1. Pick a tradeoff (e.g. batch vs streaming)
2. Invent a scenario (e.g. "social media analytics for 50M daily events")
3. Walk through the 4-step template in 30-60 seconds
4. Record yourself and listen back

**What to check in your recording:**
- Did you state both options clearly?
- Did you name specific numbers (throughput, latency, cost)?
- Did you tie the decision to a requirement, not just preference?
- Did you acknowledge what you are giving up?

**The most common mistake:** stating a preference without explaining why and
what you are giving up. "I would use Kafka" is not a tradeoff discussion.
"I would use Kafka over Kinesis because we need 50K events/sec with at-least-once
delivery and Kafka's partition-level ordering gives us the sequencing guarantee
our downstream consumers need. The tradeoff is more operational overhead since
we are managing brokers ourselves" is a tradeoff discussion.
