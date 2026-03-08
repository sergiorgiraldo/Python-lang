# DE Scenario: Merging Sorted Files

**Run it:** `uv run python -m patterns.02_two_pointers.de_scenarios.merging_sorted_files`

## Real-World Context

You have multiple sorted files (or sorted partitions) that need to be combined into a single sorted output. This is the merge phase of external sort - the same operation that happens when compacting SSTable files in LSM-tree databases, merging sorted runs from a distributed sort or combining pre-sorted export files from different sources.

The two-file case is the building block. Once you can merge two sorted sequences, you can extend to K sequences with a heap (covered in the heap pattern).

## The Problem

```python
# Two sorted streams of timestamped events
stream_a = [
    {"ts": "2024-01-01T00:01", "event": "login", "user": "alice"},
    {"ts": "2024-01-01T00:05", "event": "click", "user": "alice"},
    {"ts": "2024-01-01T00:12", "event": "purchase", "user": "alice"},
]

stream_b = [
    {"ts": "2024-01-01T00:03", "event": "login", "user": "bob"},
    {"ts": "2024-01-01T00:07", "event": "click", "user": "bob"},
    {"ts": "2024-01-01T00:15", "event": "logout", "user": "bob"},
]

# Goal: single sorted stream by timestamp
```

## Worked Example

Merging two sorted files is the fundamental two-pointer operation in data engineering. One pointer per file, always output the smaller current value. Each file read exactly once.

```
File A (sorted timestamps): [08:01, 08:15, 08:42, 09:10, 09:30]
File B (sorted timestamps): [08:05, 08:20, 08:55, 09:25]

  pA→08:01 < pB→08:05 → output 08:01. Advance pA.
  pA→08:15 > pB→08:05 → output 08:05. Advance pB.
  pA→08:15 < pB→08:20 → output 08:15. Advance pA.
  pA→08:42 > pB→08:20 → output 08:20. Advance pB.
  pA→08:42 < pB→08:55 → output 08:42. Advance pA.
  pA→09:10 > pB→08:55 → output 08:55. Advance pB.
  pA→09:10 < pB→09:25 → output 09:10. Advance pA.
  pA→09:30 > pB→09:25 → output 09:25. Advance pB.
  B exhausted → output 09:30.

9 elements, 8 comparisons. Merging two 100M-row sorted files: 200M
steps. Concatenating and re-sorting: ~5 billion comparisons.
```

## Why Two Pointers

Both inputs are already sorted. A naive approach would concatenate and re-sort - O((n+m) log(n+m)). Two pointers merges in O(n+m) by comparing the heads of both sequences and always taking the smaller one.

A practical note: in Python, Timsort is C-implemented and specifically optimized for merging sorted runs. For in-memory data, `sorted(a + b)` is often faster in wall-clock time than a pure-Python two-pointer merge. The two-pointer approach wins on a different axis - it works as a streaming operation. The generator-based merge holds only two records in memory at a time, which means it can process files far larger than available RAM. When your sorted inputs are on disk or coming from a network stream, concat+sort isn't an option.

In other languages (Java, C++, Rust) where the merge is also compiled, the two-pointer approach matches or beats re-sorting on speed too. The pattern is language-agnostic even if the Python performance characteristics have a wrinkle.

## Production Considerations

**Stability matters.** When timestamps are equal, you may want a consistent tiebreaker (e.g., source file name, event type). Otherwise the output order is arbitrary for ties, which makes testing and debugging harder.

**Streaming-friendly.** Unlike concatenate-and-sort, the merge approach works with generators and file iterators. You never need the full dataset in memory. This makes it suitable for files that are individually larger than available RAM.

**Generalization to K files.** Two-way merge handles two files. For K files, use a heap-based K-way merge (see the heap pattern). Or chain two-way merges in a tournament tree structure - this is how external sort implementations often work.

## Connection to LeetCode

This is LeetCode 88 (Merge Sorted Array) applied to real data. Same two-pointer merge logic, different context.

See: [88. Merge Sorted Array](../problems/088_merge_sorted.md)

## Benchmark

See the `.py` file for a three-way comparison at scale. At 1M total records: two-pointer merge runs in ~0.2s, concat+sort in ~0.2s (Timsort is C-optimized for sorted runs), generator merge in ~0.2s with O(1) memory. The generator variant is the key win - it processes files larger than RAM.
