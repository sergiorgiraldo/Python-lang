# DE Scenario: Approximate Distinct Count

## Real-World Context

"How many unique users visited yesterday?" sounds simple. With 500M events and 50M unique users, an exact COUNT DISTINCT requires a hash set holding 50M entries (~3.5 GB of RAM) or a database sort/hash operation. BigQuery and Snowflake offer APPROX_COUNT_DISTINCT() which uses HyperLogLog internally to answer this in 16 KB with ~1% error.

Understanding HLL helps you:
- Explain the ~1% discrepancy when stakeholders compare exact vs approximate counts
- Choose precision settings based on accuracy requirements
- Use merge operations for distributed counting across shards or time windows

## Worked Example

HLL provides fixed-memory cardinality estimation regardless of dataset size. The merge operation (element-wise max of registers) enables distributed counting: each worker processes its shard independently, then the coordinator merges all HLLs for the global estimate.

```
Scenario: 5M events from 500K unique users

Exact approach:
  HashSet of user IDs -> 500K entries -> ~35 MB memory
  Time: ~800 ms (hashing + set operations)

HLL approach (p=14):
  16,384 registers -> 16 KB memory (2,100x smaller)
  Time: ~600 ms
  Estimate: 498,200 (error: 0.36%)

Distributed counting (3 Kafka partitions):
  Worker 0: processes events for users 0-200K -> HLL estimate: 201K
  Worker 1: processes events for users 150K-350K -> HLL estimate: 199K
  Worker 2: processes events for users 300K-500K -> HLL estimate: 198K

  Merge: max(register[i]) across all 3 workers
  Merged estimate: 497,800 (error: 0.44%)
  Note: overlapping users are handled automatically by the max operation

SQL equivalent:
  SELECT APPROX_COUNT_DISTINCT(user_id) FROM events
  WHERE event_date = '2024-01-15';
  -- Returns: 498,200 (same result, ~16 KB internal state)
```
