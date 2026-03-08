# Top-K Streaming Aggregations

**Run it:** `uv run python -m patterns.05_heap_priority_queue.de_scenarios.top_k_streaming`

## Real-World Context

"Show me the 10 slowest queries from yesterday." Sounds simple until yesterday had 50 million queries. Sorting 50M records to find 10 is wasteful. A min-heap of size 10 processes the entire stream while holding only 10 entries in memory.

This pattern shows up in monitoring dashboards, SLA reporting, data quality alerts and any "top N by metric" aggregation where N is small relative to the total dataset.

## The Problem

Given a stream of query log entries (each with a duration), find the K slowest queries. The stream is too large to sort in memory. Process it in a single pass with O(K) memory.

## Worked Example

Finding the top K items from a data stream without sorting the entire stream. A min-heap of size K holds the K largest values seen so far. New values smaller than the heap minimum are discarded in O(1). Larger values replace the minimum in O(log K).

```
Stream of query latencies (ms), finding top 5 slowest:
  heap capacity = 5

  Incoming: 120, 45, 230, 88, 310, 67, 195, 412, 56, 275

  120 → heap not full, push. heap=[120]
  45  → push. heap=[45, 120]
  230 → push. heap=[45, 120, 230]
  88  → push. heap=[45, 88, 120, 230]
  310 → push. heap=[45, 88, 120, 230, 310] (full, min=45)

  67  → 67 > 45? Yes → replace 45. heap=[67, 88, 120, 230, 310]
  195 → 195 > 67? Yes → replace 67. heap=[88, 120, 195, 230, 310]
  412 → 412 > 88? Yes → replace 88. heap=[120, 195, 230, 310, 412]
  56  → 56 > 120? No → discard. Heap unchanged.
  275 → 275 > 120? Yes → replace 120. heap=[195, 230, 275, 310, 412]

  Top 5 slowest queries: [195, 230, 275, 310, 412]
  Processed 10 values. Heap never exceeded 5 entries.
  For 10M queries: 10M comparisons, heap stays at 5. O(n log 5) ≈ O(n).
```

## Why Heaps

| Approach | Time | Space | Notes |
|----------|------|-------|-------|
| Sort all | O(n log n) | O(n) | Needs all data in memory |
| Min-heap of size K | O(n log k) | O(k) | Single pass, constant memory |
| heapq.nlargest | O(n log k) | O(k) | Same algorithm, cleaner API |

When K=10 and n=50M: log(50M) ≈ 26, log(10) ≈ 3.3. The heap approach does about 8x less work per element and uses 5,000,000x less memory.

## Production Considerations

- **Streaming vs batch:** The heap approach works element by element. You can process data from a file, Kafka consumer or database cursor without loading everything first.
- **Ties:** If multiple records tie for the Kth position, a min-heap keeps exactly K records. If you need all ties included, you'd need to track the Kth value separately and collect all records matching it.
- **Approximate top-K:** For extremely high throughput (millions of events/second), probabilistic structures like Count-Min Sketch + heap give approximate results with less CPU per event.
- **SQL equivalent:** `SELECT * FROM logs ORDER BY duration_ms DESC LIMIT 10`. The database query optimizer makes a similar decision internally about whether to sort or use a heap-based scan.

## Connection to LeetCode

Direct application of problem 703 (Kth Largest Element in a Stream). The min-heap of size K acts as a filter - anything smaller than the current Kth value gets discarded.

## Benchmark

Running the script processes 1M simulated query logs:

At n=1M and k=10, the heap approach typically runs 2-4x faster than sorting. The real win is memory: the heap holds 10 entries regardless of input size. Sorting requires all 1M records in memory.
