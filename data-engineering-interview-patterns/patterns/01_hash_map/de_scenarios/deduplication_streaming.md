# DE Scenario: Deduplication in Streaming Data

**Run it:** `uv run python -m patterns.01_hash_map.de_scenarios.deduplication_streaming`

## Real-World Context

Your pipeline receives events from multiple sources. Some events arrive more than once - retries from producers, redeliveries from message brokers, overlapping batch windows. You need to ensure each event is processed exactly once.

At-least-once delivery is the default for most message systems (Kafka, SQS, Pub/Sub). Your pipeline needs to handle the duplicates.

## The Problem

```python
events = [
    {"event_id": "e001", "user": "alice", "action": "purchase", "amount": 50},
    {"event_id": "e002", "user": "bob", "action": "click"},
    {"event_id": "e001", "user": "alice", "action": "purchase", "amount": 50},  # duplicate
    {"event_id": "e003", "user": "charlie", "action": "view"},
    {"event_id": "e002", "user": "bob", "action": "click"},  # duplicate
]

# Goal: process each event_id exactly once
```

## Worked Example

In streaming pipelines, the same event can arrive multiple times. Kafka's at-least-once delivery guarantee means consumers may process retries. Producer bugs can send duplicate messages. A set of event IDs lets you detect and skip duplicates in O(1) per event. This is the exact same pattern as Contains Duplicate (problem 217) applied to production data.

We use a set (not a dict) because we only need to know "have I seen this event ID before?" - we don't need to associate any data with the ID.

```
Incoming Kafka messages (some are retries from a producer failure):
  msg 1: event_id="evt_a1b2" payload={"action": "click", "user": 42}
    seen = {}
    "evt_a1b2" in seen? No → PROCESS event. Add to seen. seen = {"evt_a1b2"}

  msg 2: event_id="evt_c3d4" payload={"action": "purchase", "user": 17}
    "evt_c3d4" in seen? No → PROCESS. seen = {"evt_a1b2", "evt_c3d4"}

  msg 3: event_id="evt_a1b2" payload={"action": "click", "user": 42}
    "evt_a1b2" in seen? YES → SKIP (duplicate, likely a retry after timeout)

  msg 4: event_id="evt_e5f6" payload={"action": "signup", "user": 88}
    "evt_e5f6" in seen? No → PROCESS. seen = {"evt_a1b2", "evt_c3d4", "evt_e5f6"}

  msg 5: event_id="evt_c3d4" payload={"action": "purchase", "user": 17}
    "evt_c3d4" in seen? YES → SKIP (duplicate)

  msg 6: event_id="evt_g7h8" payload={"action": "click", "user": 42}
    "evt_g7h8" in seen? No → PROCESS.
    (Same user as msg 1, but different event_id = genuinely new event)

Processed: 4 unique events from 6 messages. 2 duplicates caught.
Each check is an O(1) set lookup regardless of how many events we've seen.

At scale: 10M messages/hour with ~1% duplicates. The set holds
~9.9M event IDs (~400MB for 40-byte IDs). Each dedup check is a
hash lookup, adding microseconds per message.
```

## Why Hash Maps

A duplicate purchase event means charging someone twice. A duplicate click event inflates analytics. Getting deduplication wrong has real consequences.

The hash set gives O(1) membership checking per event. Without it, you'd need to scan all previously seen events for each new one - O(n²) total.

## The Approaches

**Set-based (in-memory):** Track seen event IDs in a set. O(1) lookup per event. Works when the dedup window fits in memory.

**Time-windowed:** Only deduplicate within a time window (e.g., last 24 hours). Keeps memory bounded. Most duplicates arrive within minutes of the original.

**Bloom filter pre-check:** When the event space is massive, use a Bloom filter as a fast pre-check. If the filter says "not seen," it's definitely new. If it says "maybe seen," check the authoritative store (database, Redis).

## Production Considerations

**Memory growth is the main risk.** An unbounded set of seen IDs grows forever. Time-windowed dedup or periodic cleanup is essential.

**Idempotent writes are the safety net.** Even with dedup logic, design your sinks to be idempotent. If the same event somehow gets through, the write should be a no-op (MERGE/upsert, not blind INSERT).

**Distributed dedup is harder.** If multiple workers process events in parallel, a local set won't catch duplicates that land on different workers. You need a shared store (Redis, database) or partition by event ID so all copies of the same event hit the same worker.

## Connection to LeetCode

This is Contains Duplicate (LeetCode 217) in production form. The set-based existence check is identical. The production complexity comes from scale, distribution and memory management.

See: [217. Contains Duplicate](../problems/217_contains_duplicate.md)

## Benchmark

See the `.py` file for comparisons across dedup strategies. At 1M events: simple set-based dedup runs in ~0.4s, time-windowed in ~0.3s. The Bloom filter variant uses less memory at the cost of false positives.
