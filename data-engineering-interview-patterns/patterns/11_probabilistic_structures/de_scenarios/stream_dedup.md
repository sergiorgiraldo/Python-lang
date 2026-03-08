# DE Scenario: Stream Deduplication

## Real-World Context

Event pipelines using Kafka, Kinesis or Pub/Sub typically provide at-least-once delivery. Duplicate events arrive from retries, reprocessing and consumer restarts. Deduplicating requires checking "have I seen this event ID before?" for every event.

Checking a database for each event at 100K events/second means 100K DB queries/second. A Bloom filter pre-filter eliminates the DB lookup for events that are definitely new (the common case), reducing DB load by 90%+.

## Worked Example

The Bloom filter sits in front of the database as a fast, in-memory pre-filter. Events that the filter says are "definitely new" skip the DB entirely. Events that the filter says are "possibly seen" still need a DB check (some will be false positives).

```
Stream: [evt_001, evt_002, evt_001, evt_003, evt_002, evt_004, ...]

Event evt_001 (first time):
  Bloom check: all bits at 0 -> DEFINITELY NEW
  Skip DB lookup (saved). Add to Bloom + DB.

Event evt_002 (first time):
  Bloom check: -> DEFINITELY NEW
  Skip DB lookup (saved). Add to Bloom + DB.

Event evt_001 (duplicate):
  Bloom check: all bits set -> POSSIBLY SEEN
  DB lookup: yes, exists -> TRUE DUPLICATE. Drop.

Event evt_005 (first time, false positive):
  Bloom check: all bits set (collision) -> POSSIBLY SEEN
  DB lookup: not found -> FALSE POSITIVE. Add to Bloom + DB.

Results for 130K events (100K unique + 30K duplicates):
  DB lookups saved: ~99K (for definitely-new events)
  False positives: ~1K (checked DB unnecessarily)
  Memory: ~120 KB (Bloom) vs ~7 MB (exact set)
```
