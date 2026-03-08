# DE Scenario: Heavy Hitter Detection

## Real-World Context

In distributed data systems, "hot keys" cause skew. If a Kafka topic is partitioned by customer_id and one customer generates 10% of all events, that partition's consumer falls behind while others idle. Detecting hot keys in real time helps trigger alerts, repartitioning or special handling.

A Count-Min Sketch tracks approximate frequencies for all keys using fixed memory, paired with a small heap to track the top candidates.

## Worked Example

The CMS estimates frequencies for every key seen in the stream. A threshold (e.g., 1% of total traffic) identifies which keys are "hot." The CMS never under-counts, so any key above the threshold is flagged. Some keys slightly below the threshold might be flagged too (over-counting), but hot keys are never missed.

```
Stream: 100K events across 10,005 unique keys
  5 hot keys: ~8,000 events each (8% of traffic)
  10,000 normal keys: ~6 events each

CMS tracking (width=2000, depth=5):
  After processing all events:

  estimate("hot_key_0") = 8,012   (true: 8,000, over-count: 12)
  estimate("hot_key_1") = 8,003   (true: 8,000, over-count: 3)
  estimate("key_00042") = 9       (true: 6, over-count: 3)

  Threshold: 1% of 100K = 1,000 events

  Heavy hitters detected:
    hot_key_0: ~8,012 (8.0%)  <- correctly flagged
    hot_key_1: ~8,003 (8.0%)  <- correctly flagged
    hot_key_2: ~7,998 (8.0%)  <- correctly flagged
    hot_key_3: ~8,015 (8.0%)  <- correctly flagged
    hot_key_4: ~7,991 (8.0%)  <- correctly flagged

  No false positives (normal keys are ~6 events, far below 1K threshold)
  Memory: 80 KB (vs ~700 KB for exact counter per key)
```
