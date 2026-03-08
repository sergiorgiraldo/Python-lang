# Spark vs Python Cheatsheet

Quick reference for translating Python algorithmic patterns to PySpark. Use this
to connect interview whiteboard solutions to distributed implementations.

## Pattern Translation Table

| Python Pattern | PySpark Equivalent | Shuffle? | Section |
|---|---|---|---|
| `dict` lookup (hash map) | Broadcast join | No | [01_joins](../01_joins/) |
| `dict` lookup (both large) | Shuffle hash / sort-merge join | Yes | [01_joins](../01_joins/) |
| `collections.Counter` | `groupBy().count()` | Yes | [04_aggregations](../04_aggregations/) |
| `heapq.nlargest(k, data)` | `orderBy(desc()).limit(k)` | Partial | [02_sorting](../02_sorting_and_merging/) |
| `sorted(data)` | `orderBy()` | Yes (full) | [02_sorting](../02_sorting_and_merging/) |
| Sort within groups | `sortWithinPartitions()` | No | [02_sorting](../02_sorting_and_merging/) |
| `for x in data: running += x` | `sum().over(Window.rowsBetween(...))` | Sort only | [03_windows](../03_window_functions/) |
| Two-pointer merge | Sort-merge join | Yes | [02_sorting](../02_sorting_and_merging/) |
| Sliding window with set | `row_number().over(Window)` + filter | Sort only | [03_windows](../03_window_functions/) |
| `set()` for dedup | `dropDuplicates()` or `row_number()` dedup | Yes | [03_windows](../03_window_functions/) |
| Nested loop (O(n^2)) | Cross join (avoid) | Yes (massive) | [01_joins](../01_joins/) |
| Binary search on sorted data | Partition pruning on range-partitioned data | No | [05_partitioning](../05_partitioning/) |
| Bloom filter membership | `approx_count_distinct` / bloom filter API | Partial | [04_aggregations](../04_aggregations/) |

## Shuffle Guide

| Operation | Triggers Shuffle? | Why |
|---|---|---|
| `filter()` | No | Narrows rows within each partition |
| `select()` | No | Transforms columns within each partition |
| `withColumn()` | No | Adds column within each partition |
| `orderBy()` | Yes | Global sort requires range partitioning |
| `groupBy().agg()` | Yes | Same keys must be on same partition |
| `join()` (both large) | Yes (both sides) | Same keys must co-locate |
| `join()` (one broadcast) | No (large side) | Small side sent to all partitions |
| `repartition(n, col)` | Yes | Redistributes by hash of column |
| `coalesce(n)` | No | Merges adjacent partitions |
| `distinct()` / `dropDuplicates()` | Yes | Must check all values |
| Window functions | Sort within partition | Partition key determines grouping |

## Cost Hierarchy (cheapest to most expensive)

1. `filter`, `select`, `withColumn` - no shuffle, no sort
2. `coalesce` - no shuffle, just merge
3. Window functions - sort within partitions
4. Broadcast join - serialize + send small side
5. `groupBy` aggregation - shuffle one side
6. Shuffle join - shuffle both sides
7. `orderBy` - full global sort with shuffle
8. Cross join - cartesian product (almost never correct)

## Quick Decision Guide

```
Need to join?
├── One side small (< 1GB) -> broadcast join (no shuffle)
├── Both sides large -> shuffle join
│   └── One key dominates? -> salted join or AQE
└── Need exact match? -> equi-join
    └── Need range match? -> range join (expensive)

Need to aggregate?
├── Group by low-cardinality key -> groupBy().agg() (fast shuffle)
├── Group by high-cardinality key -> groupBy().agg() (expensive shuffle)
├── Need exact distinct count? -> countDistinct() (full shuffle)
└── Approximate OK? -> approx_count_distinct() (partial shuffle)

Need to sort?
├── Global order needed? -> orderBy() (full shuffle)
├── Local order sufficient? -> sortWithinPartitions() (no shuffle)
└── Only need top-k? -> orderBy().limit(k) (partial, TakeOrdered)

Need to reduce partitions?
├── After filter with many empty partitions? -> coalesce() (no shuffle)
└── Need even redistribution? -> repartition() (shuffle)
```

## Related Resources

- [Pattern Recognition Guide](../../docs/PATTERN_RECOGNITION.md) - algorithmic and SQL pattern matching
- [Time Complexity Cheatsheet](../../docs/TIME_COMPLEXITY_CHEATSHEET.md) - Big-O reference
- [Common Interview Questions](common_interview_questions.md) - top 20 PySpark questions
