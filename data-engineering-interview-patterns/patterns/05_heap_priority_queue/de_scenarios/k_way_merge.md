# K-Way Merge of Sorted Partitions

**Run it:** `uv run python -m patterns.05_heap_priority_queue.de_scenarios.k_way_merge`

## Real-World Context

You have 100 sorted Parquet files from a date-partitioned table. You need a single sorted output for a downstream consumer. Or you're compacting SSTables in a storage engine. Or merging sorted results from multiple database shards.

K-way merge is one of the most common operations in data engineering. It's the merge step in external sort, the compaction algorithm in LSM trees (RocksDB, Cassandra, LevelDB) and the core operation when combining sorted partitions in distributed systems.

## The Problem

Given K sorted sequences, produce a single sorted output. The sequences might be lists in memory, files on disk or streams from remote services. The combined output might not fit in memory.

## Worked Example

K-way merge in data engineering: combining K sorted partitions (files, Kafka partitions, database shards) into a single sorted output. Same algorithm as Merge K Sorted Lists (problem 23).

```
3 sorted partition files:
  partition_0: [ts=100, ts=250, ts=400]
  partition_1: [ts=150, ts=300, ts=450]
  partition_2: [ts=200, ts=350, ts=500]

  heap initialized with first record from each: [(100,p0), (150,p1), (200,p2)]

  Pop 100 (p0) → write to output. Push next from p0 (250).
  Pop 150 (p1) → write. Push 300.
  Pop 200 (p2) → write. Push 350.
  Pop 250 (p0) → write. Push 400.
  Pop 300 (p1) → write. Push 450.
  Pop 350 (p2) → write. Push 500.
  Pop 400 (p0) → write. p0 exhausted.
  Pop 450 (p1) → write. p1 exhausted.
  Pop 500 (p2) → write. p2 exhausted.

  Output: [100, 150, 200, 250, 300, 350, 400, 450, 500]
  Heap never held more than 3 entries regardless of partition size.
```

## Why Heaps

| Approach | Time | Space | Works on Streams? |
|----------|------|-------|--------------------|
| Concat + sort | O(n log n) | O(n) | No |
| Sequential 2-way merge | O(n × k) | O(n) | No |
| Heap K-way merge | O(n log k) | O(k) + output | Yes |
| Lazy heap merge | O(n log k) | O(k) | Yes |

The lazy version is the key for DE: it yields one element at a time with O(k) memory. You can merge 1000 sorted files of 1GB each while holding only 1000 values in memory.

## Production Considerations

- **heapq.merge:** Python's standard library provides `heapq.merge(*iterables)` which does exactly this. Use it in production code.
- **File handles:** When merging sorted files, keep K file handles open simultaneously. OS limits on open file descriptors (typically 1024) cap K. For more files, merge in rounds.
- **Buffered reading:** Reading one element at a time from disk is slow. Buffer N elements per file to amortize I/O. The heap still holds K entries but each entry represents a buffer.
- **External sort:** This is the merge phase of external sort. The sort phase splits data into sorted chunks that fit in memory. The merge phase combines them with K-way merge.

## Connection to LeetCode

Direct application of problem 23 (Merge K Sorted Lists). The linked list version and the array version use the same heap algorithm. The lazy generator version is the DE extension.

## Benchmark

Running the script compares approaches at different K values (total elements fixed at 100K):

At K=1000 with 100 elements per partition, sequential merge slows down significantly because early elements get re-processed in every merge step. The heap approach scales with log(K).
