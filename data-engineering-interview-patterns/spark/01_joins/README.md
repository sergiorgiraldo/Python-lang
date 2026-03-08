# Joins

## Pattern Connection

Maps directly to [`patterns/01_hash_map/`](../../patterns/01_hash_map/README.md)
and [`sql/02_joins/`](../../sql/02_joins/README.md).

In Python you build a `dict` from the small dataset and probe it with the large one.
Spark does the same thing but distributes it: the "dict" is either broadcast to every
worker or hash-partitioned so matching keys land on the same node.

## Join Strategies

Spark has three physical join strategies. The optimizer picks one based on table sizes
and configuration.

| Strategy | When Used | Shuffle? | Analogy |
|---|---|---|---|
| Broadcast Hash Join | One side < 10MB (default) | No | Send the dict to every worker |
| Shuffle Hash Join | Medium tables, hash-joinable | Both sides | Partition both sides by key |
| Sort-Merge Join | Large-large (default fallback) | Both sides | Sort then two-pointer merge |

The 10MB threshold is configurable via `spark.sql.autoBroadcastJoinThreshold`.
Use `F.broadcast(df)` to force a broadcast regardless of size.

## Data Skew

The main production concern with joins. When one key appears far more than others
(e.g., `country="US"` in a global dataset), the partition handling that key becomes
a bottleneck while other partitions finish quickly. Solutions include salted joins
and Adaptive Query Execution (Spark 3.x).

## Interview Context

Joins are the most commonly tested Spark topic. Interviewers want to know:
- When to broadcast vs shuffle
- How to read an explain plan to identify the join strategy
- How to handle skewed keys in production
- The cost of shuffles (network I/O, disk spill)

## Files

| File | Description |
|---|---|
| `broadcast_join.py` | Small-large join using broadcast hint, explain plan analysis |
| `shuffle_join.py` | Large-large join with hash partitioning, Exchange nodes |
| `skew_handling.py` | Salted join technique and AQE configuration for skewed data |
