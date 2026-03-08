# Common PySpark Interview Questions

These are the PySpark questions that appear most frequently in DE interviews,
organized from fundamental to advanced. Each answer is a framework, not a script.
Adapt the details to the specific question.

---

## Fundamentals (asked at all levels)

### 1. "What is a shuffle and why is it expensive?"

Data moves across the network between executors. Triggered by joins, groupBy,
orderBy, repartition and distinct. Expensive because of network I/O,
serialization/deserialization and potential disk spill. Minimize shuffles with
broadcast joins, pre-partitioning and coalesce instead of repartition.

See: [spark/01_joins/shuffle_join.py](../01_joins/shuffle_join.py)

### 2. "Explain the difference between transformations and actions."

Transformations are lazy: they build a logical plan but don't execute (map, filter,
select, join). Actions trigger execution: collect, count, write, show. Spark
optimizes the entire chain of transformations before executing. This enables
predicate pushdown, column pruning and other optimizations.

### 3. "How does Spark handle memory management?"

Unified memory model: execution memory (shuffles, sorts) + storage memory (cache).
Spills to disk when memory is full (performance degrades but doesn't crash).
Executor memory is set via `spark.executor.memory` (typically 4-16GB). Driver memory
is set via `spark.driver.memory` (where `collect()` results land).

### 4. "What's the difference between repartition and coalesce?"

`repartition(n)` shuffles all data into n partitions (can increase or decrease).
`coalesce(n)` merges adjacent partitions without a shuffle (can only decrease). Use
coalesce after filtering when many partitions are nearly empty. Use repartition when
you need even distribution by key.

See: [spark/05_partitioning/partition_strategies.py](../05_partitioning/partition_strategies.py)

### 5. "When would you use a broadcast join?"

When one side is small enough to fit in executor memory (typically < 1GB). Default
threshold is `spark.sql.autoBroadcastJoinThreshold = 10MB`. Override with
`F.broadcast(df)` for larger tables you know fit. Common case: fact table (large)
joined with dimension table (small).

See: [spark/01_joins/broadcast_join.py](../01_joins/broadcast_join.py)

---

## Intermediate (asked at mid-senior level)

### 6. "How do you handle data skew?"

Identify the hot key causing skew. Options: salted join (add random suffix to hot
key, replicate small side), AQE skew join (Spark 3.x splits skewed partitions
automatically), broadcast the small side, or pre-aggregate the hot key before
joining.

See: [spark/01_joins/skew_handling.py](../01_joins/skew_handling.py)

### 7. "Explain partitioning strategies."

Hash partitioning (`repartition(n, col)`) puts rows with the same key on the same
partition. Range partitioning (`repartitionByRange(n, col)`) puts contiguous key
ranges together. Write-time partitioning (`write.partitionBy(col)`) organizes output
files for partition pruning. Choose hash for joins/aggregations, range for sorted
output, write-time for read optimization.

See: [spark/05_partitioning/partition_strategies.py](../05_partitioning/partition_strategies.py)

### 8. "How do you read a Spark explain plan?"

Read bottom to top, left to right. Leaf nodes are data sources (Scan). Look for
Exchange nodes (shuffles, the expensive part). Identify the join strategy
(BroadcastHashJoin vs SortMergeJoin). Check for TakeOrderedAndProject (optimized
top-k) instead of full Sort. PushedFilters in the Scan node means predicate pushdown
is working.

See: [spark/05_partitioning/explain_plans.py](../05_partitioning/explain_plans.py)

### 9. "What is AQE and what problems does it solve?"

Adaptive Query Execution (Spark 3.x) optimizes the query plan at runtime based on
actual data statistics. Key features: coalesces small shuffle partitions, detects
and splits skewed partitions, converts sort-merge joins to broadcast joins when one
side is smaller than expected. Enable with
`spark.sql.adaptive.enabled = true`.

See: [spark/05_partitioning/optimization_patterns.py](../05_partitioning/optimization_patterns.py)

### 10. "How do you tune a Spark job that's running slowly?"

Check the explain plan for unnecessary shuffles. Look for skewed partitions (one
task takes much longer). Verify broadcast joins are being used for small tables.
Check if caching helps for reused DataFrames. Review partition count (too few =
large partitions, too many = overhead). Consider predicate pushdown and column
pruning for I/O reduction.

---

## Advanced (asked at senior/principal level)

### 11. "How does Structured Streaming work?"

Treats a stream as an unbounded table. Each micro-batch processes new rows
incrementally. Supports exactly-once semantics with checkpointing. Three output
modes: append (new rows only), complete (full result each batch), update (changed
rows only). State is maintained across batches for windowed aggregations.

See: [spark/06_streaming/structured_streaming_basics.py](../06_streaming/structured_streaming_basics.py)

### 12. "Explain watermarks and late data handling."

Watermarks define how late data can arrive before being dropped. Set with
`.withWatermark("timestamp", "10 minutes")`. Spark tracks the maximum observed event
time and drops events older than `max_event_time - watermark_delay`. Without a
watermark, state grows unbounded. With a watermark, Spark can clean up old window
state.

### 13. "How would you implement exactly-once processing?"

Use Structured Streaming with checkpointing (write-ahead log of offsets). For Kafka
sources, Spark tracks committed offsets. For file sinks, use idempotent writes. For
database sinks, use transactional writes (write output + offset in same transaction).
End-to-end exactly-once requires both source replay and sink idempotency.

### 14. "Compare Spark vs Flink for streaming."

Spark uses micro-batching (higher latency, simpler programming model). Flink uses
true event-at-a-time processing (lower latency, more complex). Spark is better for
unified batch + streaming workloads. Flink is better for sub-second latency
requirements. Both support event-time processing and watermarks. Spark's ecosystem
is larger; Flink's streaming semantics are more mature.

### 15. "How do you handle schema evolution in a Spark pipeline?"

Use a schema registry (Confluent, AWS Glue) to track schema versions. For Parquet,
use `mergeSchema` option when reading. For Delta Lake/Iceberg, use built-in schema
evolution (add columns, widen types). For breaking changes (rename, remove columns),
use a migration strategy: write both old and new schemas during transition, then
switch consumers.

---

## Common Mistakes in Spark Interviews

- Saying "Spark is in-memory" (it spills to disk when memory is full)
- Not knowing what triggers a shuffle
- Using `collect()` on large DataFrames (pulls all data to driver)
- Not mentioning partitioning when discussing performance
- Describing Spark as "just distributed Pandas" (very different execution model)
- Not knowing the difference between narrow and wide transformations
- Forgetting that `orderBy()` is one of the most expensive operations
- Not considering data skew when discussing joins at scale

---

## Related Resources

- [Spark vs Python Cheatsheet](spark_vs_python_cheatsheet.md) - pattern translation table
- [Pattern Recognition Guide](../../docs/PATTERN_RECOGNITION.md) - algorithmic and SQL patterns
- [Interview Strategy Guide](../../docs/INTERVIEW_STRATEGY.md) - pacing and communication
