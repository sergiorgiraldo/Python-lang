# Aggregations

## Pattern Connection

Maps to [`patterns/01_hash_map/`](../../patterns/01_hash_map/README.md)
(Counter and frequency counting),
[`patterns/05_heap_priority_queue/`](../../patterns/05_heap_priority_queue/README.md)
(top-k after counting),
[`patterns/11_probabilistic_structures/`](../../patterns/11_probabilistic_structures/README.md)
(approximate distinct counting) and
[`sql/03_aggregations/`](../../sql/03_aggregations/README.md).

In Python you use `collections.Counter` or `defaultdict(int)` to count by key. In
Spark, `groupBy().agg()` does the same thing but distributes the counting: rows are
shuffled by key so each partition handles a subset of keys. Spark also applies
partial aggregation (map-side combine) to reduce the amount of data shuffled.

## Key Concepts

**groupBy + agg:** the basic pattern for counting, summing, averaging per key.
Triggers a shuffle to co-locate rows with the same key.

**Conditional aggregation:** `F.sum(F.when(...))` replaces SQL's
`SUM(CASE WHEN ...)`. Useful for computing multiple metrics in a single pass.

**Pivot:** `df.groupBy("key").pivot("category").agg(F.sum("amount"))` turns row
values into columns. Spark needs to know the distinct pivot values (pass them
explicitly for better performance).

**Approximate counting:** `approx_count_distinct()` uses HyperLogLog for ~2% error
at a fraction of the memory cost. Essential when counting billions of distinct values.

## Interview Context

Aggregation questions test whether you understand the shuffle cost of groupBy and
when approximate methods are acceptable. Common questions:
- "How would you count unique users per day across 1TB of events?"
- "What happens when you groupBy a high-cardinality column?"
- "When would you use approximate counting instead of exact?"

## Files

| File | Description |
|---|---|
| `group_by_patterns.py` | Basic groupBy, conditional aggregation, pivot, top-N per group |
| `approximate_counting.py` | Exact vs HyperLogLog counting, accuracy tradeoffs |
