# Walkthrough: Design an ML Feature Store

**Prompt:** "Design a feature store for a company with 10 ML models in
production."

This walkthrough simulates a full 45-minute system design interview. Feature
stores sit at the intersection of data engineering and ML engineering. The
interviewer wants to see that you understand both the data pipeline challenges
(freshness, consistency, scale) and the ML-specific concerns (training-serving
skew, point-in-time correctness, feature reuse).

---

## Phase 1: Clarify Requirements (Minutes 0-5)

### Questions to Ask

**Model questions:**
- "What types of models are in production? Fraud detection, recommendations,
  pricing, churn prediction?"
- "What are the serving latency requirements for each model?"
- "How often are models retrained?"

**Feature questions:**
- "How many total features across all models?"
- "Do features need real-time freshness (last transaction amount) or is daily
  sufficient (30-day purchase count)?"
- "How many features does a typical model use per inference?"

**Consistency questions:**
- "Is training-serving consistency a known problem today?"
- "Do you need point-in-time correct features for training?"

**Scale questions:**
- "How many inference requests per second across all models?"
- "How large is the entity space? How many users, products, etc.?"

### Establishing Requirements

"Here's what I'm working with:

**Models:**
- Fraud detection: <50ms serving latency, real-time features, ~5K inferences/sec
- Recommendation engine: <200ms latency, daily features, ~2K inferences/sec
- Dynamic pricing: <100ms latency, hourly features, ~500 inferences/sec
- Churn prediction: batch scoring (daily), no real-time serving
- 6 other models with varying latency requirements

**Features:**
- ~500 total features across all models
- Typical model uses 20-50 features per inference
- Feature freshness ranges: real-time (10 features), hourly (40 features),
  daily (450 features)
- Entity types: users (5M), products (100K), merchants (10K)

**Scale:**
- Combined serving: ~8K feature lookups/sec at peak
- Each lookup retrieves 20-50 features for a single entity
- Training data: models retrain weekly on 3-12 months of historical data

**Key requirement:** Features used in training must match features used in
serving. Training-serving skew has caused production incidents with the
current ad-hoc approach.

**Capacity math:**
- 8K lookups/sec * 50 features * 100 bytes/feature = 40 MB/sec read
  throughput from the online store
- 5M users * 500 features * 100 bytes = 250 GB offline feature table
- Training data: 12 months * 5M users * 500 features * 100 bytes = 3 TB
  (with point-in-time snapshots)"

---

## Phase 2: High-Level Design (Minutes 5-10)

### Architecture

```
Raw Data ──▶ Spark (daily) ──▶ Offline Store (S3) ──▶ Training Pipeline
                  │
                  └──▶ Online Store (Redis) ◀── Flink ◀── Kafka (real-time)
                            │
                       Serving API (<50ms) ──▶ ML Models
```

Feature Registry provides metadata, lineage and ownership across all
components.

### Component Justification

"**Dual store architecture (offline + online):** The offline store holds all
historical feature values for training. The online store holds only the
latest values for low-latency serving. Same features, two access patterns.

**Spark for batch features:** Computes daily features like 30-day purchase
count, lifetime order total, average session duration. These features change
slowly and do not need real-time computation. Spark reads from the warehouse
or S3 and writes to both the offline store (with timestamp) and the online
store (latest value only).

**Flink for real-time features:** Computes features that need sub-minute
freshness. Last transaction amount, time since last login, current session
page count. Flink reads from Kafka event streams and writes to the online
store (Redis).

**Redis as the online store:** Sub-1ms reads for individual feature lookups.
At 8K lookups/sec with 50 features each, that's ~400K Redis operations/sec.
Within a single Redis cluster's capacity of 100K+ ops/sec per shard (2-4
shards handle this comfortably).

**S3 + Warehouse as the offline store:** Feature values keyed by (entity_id,
feature_name, timestamp). Stored as Parquet, partitioned by date. Supports
point-in-time queries for training: 'give me user X's features as they
existed on date Y.'

**Feature registry:** Metadata catalog tracking each feature's owner,
description, data type, freshness SLA, computation logic and which models
consume it."

---

## Phase 3: Deep Dive (Minutes 10-30)

### Deep Dive: Point-in-Time Joins

"This is the most critical correctness concern in a feature store. When
training a fraud detection model on historical data, we need to join each
transaction with the features that existed at the time of that transaction,
not the features that exist today.

**The problem:** A transaction from January 15 should use the user's
'30-day purchase count' as of January 15 (say, 12 purchases). If we
naively join to the current feature value (say, 45 purchases), the model
trains on information that was not available at prediction time. This is
data leakage and produces models that perform well in training but poorly in
production.

**The solution:** The offline store records feature values with timestamps.
The training pipeline performs an as-of join:

```sql
SELECT t.*, f.feature_value
FROM transactions t
LEFT JOIN features f
  ON t.user_id = f.entity_id
  AND f.feature_name = '30day_purchase_count'
  AND f.computed_at <= t.transaction_time
ORDER BY f.computed_at DESC
LIMIT 1  -- per transaction
```

In practice, this is implemented with a window function:

```sql
ROW_NUMBER() OVER (
  PARTITION BY t.transaction_id
  ORDER BY f.computed_at DESC
) = 1
```

This pattern connects directly to the window function dedup technique in
[`sql/01_window_functions/`](../../sql/01_window_functions/README.md). The same SQL pattern that deduplicates dimension
records (SCD Type 2 current version) handles point-in-time feature lookups.

**Storage cost:** Point-in-time snapshots are expensive. 500 features * 5M
users * 365 daily snapshots * 100 bytes = 91 TB/year. To manage this, we
only snapshot features daily (not on every change) and only retain 12 months
of snapshots (older training data is rarely useful). That reduces storage to
~3 TB, costing about $70/month on S3."

### Deep Dive: Online Store Design

"The online store serves the low-latency path. Each model inference retrieves
20-50 features for a single entity and must complete in under 50ms (for fraud
detection).

**Redis data model:**

Key: `features:{entity_type}:{entity_id}`
Value: Hash map of feature_name to feature_value

Example: `features:user:12345` contains a hash with 500 fields (all features
for user 12345).

**Read pattern:** A single `HGETALL features:user:12345` retrieves all
features for a user. Or `HMGET features:user:12345 field1 field2 ...` for
a subset. Either way, one Redis round trip.

**Latency budget for fraud detection (50ms total):**
- Feature retrieval from Redis: <1ms
- Network overhead (service to Redis): ~1ms
- Model inference: ~30-40ms
- Remaining buffer: ~10ms

**Memory sizing:** 5M users * 500 features * 100 bytes per feature = 250 GB.
A Redis cluster with 3 shards at ~85 GB each handles this. At
ElastiCache r6g.2xlarge pricing (~$0.50/hour per node), the online store
costs roughly $3,300/month including replicas for high availability.

**Alternative for lower cost:** DynamoDB with DAX caching. DynamoDB handles
the storage at lower cost than Redis for large datasets. DAX provides
microsecond read latency for hot keys. The tradeoff is higher tail latency
(p99) compared to Redis."

### Deep Dive: Feature Pipeline

"Features follow two paths depending on freshness requirements.

**Batch features (450 features, daily freshness):**

Spark jobs run daily. Each job computes a set of related features (user
engagement features, purchase history features, product popularity features).

```
Warehouse/S3 ──▶ Spark ──▶ Offline Store (S3, with timestamp)
                    │
                    └──▶ Online Store (Redis, latest value)
```

The Spark job writes to both stores in the same run. The offline store gets
(entity_id, feature_name, value, computed_at). The online store gets the
latest value only (overwriting the previous day's value).

Runtime: 500 features across 5M users. With proper partitioning and
parallelism, this runs in 30-60 minutes on a 10-node Spark cluster (~$4/hour
on spot instances = ~$3/run).

**Real-time features (10 features, sub-minute freshness):**

Flink reads from Kafka event streams and maintains running computations.

Example: 'last_transaction_amount' updates on every purchase event.
'minutes_since_last_login' updates on every login event.

Flink writes updated values to Redis on every event. At 50K events/sec from
Kafka. Assuming 10% of events trigger a feature update, that's 5K Redis
writes/sec. Trivial for Redis.

**Consistency:** Both paths use the same feature definitions from the
registry. The batch Spark job and the Flink job compute features using
identical logic (defined once, executed in both batch and streaming contexts).
This is the key to avoiding training-serving skew."

### Deep Dive: Feature Registry

"The registry is the metadata layer that makes the feature store manageable
at 500+ features across 10 models.

**What it tracks per feature:**
- Name, description, data type
- Owner (team or individual)
- Computation logic (SQL or Python reference)
- Freshness SLA (real-time, hourly, daily)
- Models that consume this feature
- Data source and lineage

**Why it matters:** Without a registry, features become undocumented tribal
knowledge. A new data scientist cannot discover existing features and builds
duplicates. A data engineer changes an upstream table and does not know which
features break.

**Implementation:** A metadata table in the warehouse with a simple UI or
API for discovery. Tools like Feast provide a built-in registry. For a
custom build, a database table with a lightweight web frontend is sufficient."

---

## Phase 4: Scaling and Edge Cases (Minutes 30-40)

### Feature Backfill

"When a data scientist creates a new feature, they need historical values
for training. A new feature 'days_since_first_purchase' needs to be computed
for all 5M users for every day in the past 12 months.

**Backfill pipeline:** A Spark job parameterized by date range computes the
feature value for each entity as of each historical date. This is essentially
the batch pipeline run in a loop over historical dates.

**Scale:** 5M users * 365 days * 1 feature = 1.8B rows. At 100 bytes/row,
that's 180 GB. A Spark job processes this in roughly 30-60 minutes.

**Gotcha:** Historical data may not support the new feature. If the feature
requires data from a source that was not captured 12 months ago, the backfill
is limited to the available history. Document the earliest available date in
the feature registry."

### Training-Serving Skew Detection

"Skew happens when the feature values used during training differ from those
used during serving due to bugs in feature computation, timing differences
or data pipeline issues.

**Detection approach:**
1. During serving, log the feature vector alongside each prediction
2. Periodically compare logged serving features to what the offline store
   says the feature values should have been at that timestamp
3. Flag features where the serving value differs from the offline value by
   more than a threshold (e.g., 1% of values differ)

**Cost:** Logging every serving feature vector at 8K requests/sec = 8K * 50
features * 100 bytes = 40 MB/sec = 3.4 TB/day. Expensive. Sample at 1%
instead: 34 GB/day. Compare the sampled serving features to the offline
store weekly. Alert on drift."

### Feature Versioning

"When feature computation logic changes (e.g., 'purchase_count_30d' switches
from including refunded orders to excluding them):

1. Register the new logic as v2 of the feature
2. Backfill v2 for the historical period needed for training
3. Retrain the model on v2 features
4. Deploy the model alongside the v2 feature computation
5. Deprecate v1 after all models have migrated

The key principle: never change a feature's computation in place. Always
version it. Models trained on v1 logic must serve with v1 logic until
retrained on v2. Mixing versions causes training-serving skew."

### Cost Estimate

"Steady-state monthly costs:

- **Redis online store (3 r6g.2xlarge + replicas):** ~$3,300/month
- **S3 offline store (3 TB):** ~$70/month
- **Spark batch features (daily, 10-node spot):** ~$90/month
- **Flink real-time features (2 m5.large):** ~$130/month
- **Serving API (3 containers on EKS):** ~$200/month
- **Skew detection logging (sampled):** ~$50/month (S3 storage)

**Total: ~$3,840/month**

The dominant cost is Redis. If latency requirements relax (200ms instead of
50ms), DynamoDB with DAX reduces this to roughly $1,500/month. For the fraud
detection model's 50ms requirement, Redis is worth the premium."

---

## Phase 5: Wrap Up (Minutes 40-45)

"Key design decisions and tradeoffs:

1. **Dual store (offline + online) rather than single store.** The offline
   store optimizes for historical queries (point-in-time joins for training).
   The online store optimizes for low-latency lookups (serving). A single
   store cannot serve both patterns well. The tradeoff is maintaining
   consistency between two stores, which we handle by writing from the same
   pipeline to both.

2. **Point-in-time correct training data.** This prevents data leakage and
   training-serving skew. The tradeoff is storage cost (~3 TB for 12 months
   of snapshots) and query complexity (as-of joins instead of simple lookups).
   For a company with 10 production models, this investment pays for itself
   by preventing the production incidents caused by skewed features.

3. **Redis over DynamoDB for the online store.** Redis gives sub-1ms reads
   which fits within the fraud model's 50ms latency budget. The tradeoff is
   higher cost ($3,300/month vs ~$1,500 for DynamoDB) and operational
   complexity (cluster management). For the fraud use case, the latency
   guarantee justifies the cost.

4. **Batch + streaming feature computation.** Only 10 of 500 features need
   real-time freshness. Running all 500 through Flink would be far more
   expensive and complex. The tradeoff of dual pipelines is maintaining
   consistency between batch and streaming computation logic, which we
   address through shared feature definitions in the registry.

With more time, I'd design the feature monitoring dashboard (tracking
freshness, null rates and distribution drift per feature), the automated
retraining pipeline (triggered when feature distributions shift significantly)
and the A/B testing integration (how to experiment with new features without
affecting production models)."
