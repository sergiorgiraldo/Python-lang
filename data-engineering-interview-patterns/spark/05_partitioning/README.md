# Partitioning

## Pattern Connection

Maps to [`patterns/03_binary_search/`](../../patterns/03_binary_search/README.md)
(data organization for fast lookup) and
[`system_design/patterns/scale_and_performance/`](../../system_design/patterns/scale_and_performance.md)
(partitioning strategies).

Binary search works because data is sorted. Partition pruning works because data is
organized into partitions by key. Both skip irrelevant data to find answers faster.
At scale the question is not "how do I search?" but "how do I organize data so I
don't have to search at all?"

## Key Concepts

**Partition strategies:**
- Hash: `repartition(n, "key")` - rows with same key land on same partition
- Range: `repartitionByRange(n, "key")` - contiguous ranges per partition
- Round-robin: `repartition(n)` without columns - even distribution, no key affinity

**coalesce vs repartition:**
- `coalesce(n)` reduces partitions WITHOUT a shuffle (merges adjacent partitions)
- `repartition(n)` changes partition count WITH a shuffle (redistributes all data)
- Use coalesce after filters that leave many small partitions
- Use repartition when you need a specific key distribution

**Write-time partitioning:**
`df.write.partitionBy("year", "month").parquet(path)` creates a directory structure
like `year=2024/month=01/part-00000.parquet`. This enables partition pruning on reads:
a query filtering `WHERE year = 2024` skips all other year directories entirely.

**Explain plans:**
Reading Spark's physical plan is the primary debugging skill for production jobs.
Look for Exchange nodes (shuffles), Scan nodes (data reads) and the join strategy
(BroadcastHashJoin vs SortMergeJoin).

## Interview Context

Partitioning and optimization are senior-level topics. Interviewers expect you to:
- Choose the right partition strategy for a given workload
- Explain when to use coalesce vs repartition
- Read an explain plan and identify bottlenecks
- Know about predicate pushdown, column pruning and caching

## Files

| File | Description |
|---|---|
| `partition_strategies.py` | Hash, range and round-robin partitioning with coalesce vs repartition |
| `explain_plans.py` | Reading physical plans, identifying shuffles and join strategies |
| `optimization_patterns.py` | Predicate pushdown, column pruning, caching, AQE configuration |
