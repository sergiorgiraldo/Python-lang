# Sorting and Merging

## Pattern Connection

Maps to [`patterns/02_two_pointers/`](../../patterns/02_two_pointers/README.md)
(merge operations) and [`patterns/05_heap_priority_queue/`](../../patterns/05_heap_priority_queue/README.md)
(top-k without full sort).

In Python you merge two sorted arrays with two pointers in O(n+m) time. Spark's
sort-merge join does the same thing: sort both sides by the join key then scan
with a pointer merge. The difference is that Spark must first shuffle data across
the network to get matching keys on the same node before it can sort and merge.

## Key Concepts

**orderBy() vs sortWithinPartitions()**
- `orderBy()` triggers a full shuffle to range-partition the data then sorts each
  partition. The result is globally ordered.
- `sortWithinPartitions()` sorts within each partition without any shuffle. Useful
  when downstream only needs local order (e.g., writing sorted Parquet files).

**External Sort**
When a partition is too large for memory, Spark spills sorted runs to disk and
merges them back. This is the same external merge sort algorithm from databases.

**Top-K Optimization**
`orderBy(...).limit(k)` does not sort the entire DataFrame. Spark uses a distributed
top-k algorithm (each partition keeps its local top-k, then a final merge picks the
global top-k). The physical plan shows `TakeOrderedAndProject` instead of a full `Sort`.

## Interview Context

Sorting questions test whether you understand the cost of global ordering in a
distributed system. Interviewers want to hear:
- "orderBy is expensive because it requires a shuffle"
- "sortWithinPartitions avoids the shuffle when global order isn't needed"
- "For top-k, Spark optimizes to avoid a full sort"

## Files

| File | Description |
|---|---|
| `sort_merge_operations.py` | Sort-merge join, orderBy vs sortWithinPartitions |
| `topk_without_full_sort.py` | Heap-based top-k in Python vs Spark's TakeOrderedAndProject |
