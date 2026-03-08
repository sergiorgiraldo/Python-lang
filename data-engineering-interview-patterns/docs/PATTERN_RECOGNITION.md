# Pattern Recognition Guide

Pattern recognition is the core skill in coding interviews. This guide maps problem characteristics to the pattern most likely to solve them. Use it as a study aid and a quick-reference before interviews.

---

## Algorithmic Pattern Recognition

| If you see... | Think... | Pattern | Example |
|---|---|---|---|
| "Find pair that sums to target" | Hash map for O(1) complement lookup | 01_hash_map | Two Sum |
| "Count frequency / group by value" | Hash map as counter | 01_hash_map | Group Anagrams |
| "O(1) insert, delete, lookup" | Hash map + array combination | 01_hash_map | Insert Delete GetRandom |
| "Sorted array" + "find target" | Two pointers or binary search | 02/03 | Two Sum II |
| "Remove duplicates in-place" | Two pointers (read/write) | 02_two_pointers | Remove Duplicates |
| "Sorted array" + "minimize/maximize" | Two pointers from both ends | 02_two_pointers | Container With Most Water |
| "Find position in sorted data" | Binary search | 03_binary_search | Search Insert Position |
| "Minimum/maximum that satisfies condition" | Binary search the answer | 03_binary_search | Koko Eating Bananas |
| "Contiguous subarray/substring" | Sliding window | 04_sliding_window | Max Average Subarray |
| "Longest/shortest with condition" | Variable-size sliding window | 04_sliding_window | Min Window Substring |
| "Top K" or "Kth largest" | Heap (min-heap of size k) | 05_heap | Top K Frequent |
| "Merge K sorted" | Heap (k-way merge) | 05_heap | Merge K Sorted Lists |
| "Stream of data" + "running statistic" | Heap (two heaps for median) | 05_heap | Find Median Stream |
| "Dependencies / prerequisites" | Topological sort | 06_graph | Course Schedule |
| "Connected components / islands" | BFS/DFS | 06_graph | Number of Islands |
| "Shortest path with weights" | Dijkstra | 06_graph | Network Delay Time |
| "Overlapping intervals" | Sort by start + merge | 07_intervals | Merge Intervals |
| "Maximum concurrent" | Sort events + sweep line | 07_intervals | Meeting Rooms II |
| "Matching brackets / nesting" | Stack | 08_stack | Valid Parentheses |
| "Next greater/smaller element" | Monotonic stack | 08_stack | Daily Temperatures |
| "Parse / decode structured text" | Stack or state machine | 09_string_parsing | Decode String |
| "Tree traversal / depth" | Recursion (DFS) or queue (BFS) | 10_recursion_trees | Max Depth |
| "Serialize/deserialize hierarchy" | Preorder + null markers | 10_recursion_trees | Serialize Binary Tree |
| "Approximate count / membership" | Probabilistic structure | 11_probabilistic | HyperLogLog, Bloom Filter |
| "Multiple patterns combined" | Decompose into sub-problems | 12_combined | Task Scheduler |

---

## SQL Pattern Recognition

| If you see... | Think... | Section | Example |
|---|---|---|---|
| "Rank / top N" | DENSE_RANK window function | [sql/01](../sql/01_window_functions/README.md) | Rank Scores |
| "Deduplicate rows" | ROW_NUMBER PARTITION BY key | [sql/01](../sql/01_window_functions/README.md) | Dedup DE scenario |
| "Compare to previous/next row" | LAG / LEAD | [sql/01](../sql/01_window_functions/README.md) | Rising Temperature |
| "Consecutive streak" | id - ROW_NUMBER() island technique | [sql/01](../sql/01_window_functions/README.md) | Human Traffic |
| "Running total / moving average" | SUM/AVG OVER (ORDER BY ... ROWS) | [sql/01](../sql/01_window_functions/README.md) | Running Totals DE scenario |
| "Sessionize event stream" | LAG gap detection + running SUM | [sql/01](../sql/01_window_functions/README.md) | Sessionization DE scenario |
| "Find missing / never occurred" | LEFT JOIN + IS NULL (anti-join) | [sql/02](../sql/02_joins/README.md) | Customers Who Never Order |
| "Compare to same table" | Self-join | [sql/02](../sql/02_joins/README.md) | Employees Earning More |
| "Upsert / incremental load" | MERGE or INSERT ON CONFLICT | [sql/02](../sql/02_joins/README.md) | Merge Upsert DE scenario |
| "Find duplicates" | GROUP BY + HAVING COUNT > 1 | [sql/03](../sql/03_aggregations/README.md) | Duplicate Emails |
| "Conditional counting" | SUM(CASE WHEN ...) | [sql/03](../sql/03_aggregations/README.md) | Trips and Users |
| "Detect gaps in a sequence" | generate_series + LEFT JOIN | [sql/03](../sql/03_aggregations/README.md) | Gap Detection DE scenario |
| "Pivot rows to columns" | PIVOT or CASE + GROUP BY | [sql/03](../sql/03_aggregations/README.md) | Pivot Patterns DE scenario |
| "Approximate distinct count" | APPROX_COUNT_DISTINCT (HLL) | [sql/03](../sql/03_aggregations/README.md) | Approximate Counting DE scenario |
| "Traverse hierarchy" | WITH RECURSIVE | [sql/04](../sql/04_recursive_ctes/README.md) | Hierarchy DE scenario |
| "Expand nested structure" | Recursive CTE with accumulation | [sql/04](../sql/04_recursive_ctes/README.md) | Bill of Materials DE scenario |
| "Find paths in a graph" | Recursive CTE with path array | [sql/04](../sql/04_recursive_ctes/README.md) | Graph Traversal DE scenario |
| "Filter after window function" | QUALIFY clause | [sql/05](../sql/05_optimization_and_production/README.md) | Dedup without subquery |
| "Multiple aggregation levels" | GROUPING SETS / ROLLUP / CUBE | [sql/05](../sql/05_optimization_and_production/README.md) | Multi-level reporting |
| "Query JSON / nested data" | Semi-structured functions | [sql/05](../sql/05_optimization_and_production/README.md) | Semi-structured DE scenario |
| "Cross-row join by nearest time" | LATERAL JOIN or ASOF JOIN | [sql/05](../sql/05_optimization_and_production/README.md) | Point-in-time lookup |

---

## System Design Pattern Recognition

| If you see... | Think... | Reference |
|---|---|---|
| "Ingest from database" | CDC (Debezium) or incremental batch | [system_design/patterns/ingestion_patterns](../system_design/patterns/ingestion_patterns.md) |
| "Real-time analytics" | Kafka -> Flink -> Redis/Druid | [system_design/walkthroughs/design_real_time_dashboard](../system_design/walkthroughs/design_real_time_dashboard.md) |
| "Build a warehouse" | Star schema + dbt + Snowflake/BQ | [system_design/walkthroughs/design_data_warehouse](../system_design/walkthroughs/design_data_warehouse.md) |
| "Handle late data" | Watermarks + late partition | [system_design/walkthroughs/design_event_pipeline](../system_design/walkthroughs/design_event_pipeline.md) |
| "Store ML features" | Offline store (warehouse) + online store (Redis) | [system_design/walkthroughs/design_ml_feature_store](../system_design/walkthroughs/design_ml_feature_store.md) |
| "Migrate to cloud" | Lakehouse (Delta/Iceberg on S3) | [system_design/walkthroughs/design_data_lake](../system_design/walkthroughs/design_data_lake.md) |
| "How would you ensure quality" | Layered testing + circuit breakers | [system_design/patterns/data_quality_patterns](../system_design/patterns/data_quality_patterns.md) |
| "Handle data skew" | Salting, broadcast join, AQE | [system_design/patterns/scale_and_performance](../system_design/patterns/scale_and_performance.md) |
| "Design a streaming pipeline" | Kafka + Flink + checkpointing | [system_design/walkthroughs/design_event_pipeline](../system_design/walkthroughs/design_event_pipeline.md) |
| "How to handle schema changes" | Schema registry + evolution | [system_design/patterns/data_modeling_patterns](../system_design/patterns/data_modeling_patterns.md) |
| "Estimate capacity / sizing" | Back-of-envelope math | [system_design/foundations/capacity_estimation](../system_design/foundations/capacity_estimation.md) |
| "Compare batch vs streaming" | Latency vs complexity tradeoff | [system_design/foundations/tradeoff_framework](../system_design/foundations/tradeoff_framework.md) |

---

## Decision Tree

```
Is the input sorted?
├── Yes -> Two pointers or binary search
│   ├── Finding a pair? -> Two pointers (opposite ends)
│   ├── Finding one element? -> Binary search
│   └── Merging two sorted inputs? -> Two pointers (merge)
│
├── No -> Would sorting help?
│   ├── Yes -> Sort first, then two pointers or scan
│   └── No -> Hash map or sliding window
│       ├── Need O(1) lookup? -> Hash map
│       ├── Subarray/substring problem? -> Sliding window
│       └── Need ordering/priority? -> Heap
│
└── Is it a graph/dependency problem?
    ├── Dependencies/ordering -> Topological sort
    ├── Connected components -> BFS/DFS
    └── Shortest path -> BFS (unweighted) or Dijkstra (weighted)
```

## PySpark Pattern Recognition

| If you see... | Think... | Spark Section |
|---|---|---|
| "Join large + small table" | Broadcast join | [spark/01_joins](../spark/01_joins/) |
| "Join two large tables" | Shuffle join, check for skew | [spark/01_joins](../spark/01_joins/) |
| "Deduplicate at scale" | row_number window + filter | [spark/03_window_functions](../spark/03_window_functions/) |
| "Top K across large dataset" | orderBy().limit() with TakeOrdered | [spark/02_sorting](../spark/02_sorting_and_merging/) |
| "Reduce file/partition count" | coalesce (not repartition) | [spark/05_partitioning](../spark/05_partitioning/) |
| "Job is slow" | Check explain plan for shuffles | [spark/05_partitioning](../spark/05_partitioning/) |
| "Real-time aggregation" | Structured Streaming + window | [spark/06_streaming](../spark/06_streaming/) |
| "Count distinct at scale" | approx_count_distinct (HLL) | [spark/04_aggregations](../spark/04_aggregations/) |
| "Running total at scale" | Window with unboundedPreceding | [spark/03_window_functions](../spark/03_window_functions/) |
| "Sessionize event stream" | LAG + cumulative SUM over window | [spark/03_window_functions](../spark/03_window_functions/) |
| "Data skew in join" | Salted join or AQE | [spark/01_joins](../spark/01_joins/) |
| "Optimize Parquet reads" | Partition pruning + predicate pushdown | [spark/05_partitioning](../spark/05_partitioning/) |

See also: [Spark vs Python Cheatsheet](../spark/reference/spark_vs_python_cheatsheet.md) for a full translation table.

---

## Pattern Overlap

Some problems can be solved by multiple patterns. Knowing the tradeoffs helps:

| Problem type | Option A | Option B | Notes |
|---|---|---|---|
| Find pair summing to target | Hash map: O(n) time, O(n) space | Two pointers: O(n) time, O(1) space | Two pointers needs sorted input |
| Remove duplicates | Hash set: O(n) time, O(n) space | Two pointers: O(n) time, O(1) space | Two pointers needs sorted input |
| Top-K elements | Counter + sort: O(n log n) | Heap: O(n log k) | Heap wins when k << n |
| Frequency counting | Hash map: O(n) | N/A | Hash map is the only option |
| Merge K sorted | Heap: O(n log k) | Sort all: O(n log n) | Heap wins, also works for streaming |
