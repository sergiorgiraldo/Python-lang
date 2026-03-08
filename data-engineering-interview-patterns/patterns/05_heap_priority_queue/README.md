# Heap / Priority Queue Pattern

## What Is It?

### The basics

A heap is a data structure that always gives you the smallest (or largest) element in O(1) and lets you add or remove elements in O(log n). In Python, the `heapq` module implements a **min-heap**: the smallest element is always at the top.

Think of it as a priority queue. Items go in with some priority (a number), and whenever you ask "what's the most important item?", you get the one with the lowest number instantly. Adding new items and removing the top item are both fast (O(log n)), but they're not instant like a dict lookup.

```python
import heapq

heap = []
heapq.heappush(heap, 5)    # add 5
heapq.heappush(heap, 2)    # add 2
heapq.heappush(heap, 8)    # add 8
heapq.heappush(heap, 1)    # add 1

heap[0]                     # peek at smallest → 1 (O(1), doesn't remove it)
heapq.heappop(heap)         # remove and return smallest → 1 (O(log n))
heap[0]                     # next smallest → 2
```

### How a heap is different from sorting

If you need the smallest element, why not just sort the data? Sorting works but costs O(n log n) upfront and you have to re-sort whenever new data arrives. A heap handles dynamic data: elements can arrive and leave at any time, and the heap always knows the current smallest.

| Operation | Sorted list | Heap |
|---|---|---|
| Find min/max | O(1) | O(1) |
| Insert | O(n) (shift elements) | O(log n) |
| Remove min/max | O(1) (pop from end) | O(log n) |
| Build from n items | O(n log n) | O(n) |

The heap wins when data is arriving over time (streaming) or when you only need the top k elements, not the full sorted order.

### Min-heap vs max-heap

Python's `heapq` only provides a min-heap (smallest on top). To get a max-heap (largest on top), negate the values:

```python
import heapq

# max-heap trick: negate values
max_heap = []
heapq.heappush(max_heap, -5)   # store -5 instead of 5
heapq.heappush(max_heap, -2)
heapq.heappush(max_heap, -8)

largest = -heapq.heappop(max_heap)  # pop -8, negate → 8
```

This is ugly but it works. You'll see this pattern in every Python heap solution. When pushing tuples, negate the element you want to sort by: `heappush(heap, (-priority, value))`.

### The "top K" pattern

The most common heap interview pattern: "find the K largest/smallest/most frequent elements." The trick: maintain a heap of size K.

For "K largest elements," use a **min-heap of size K**. The smallest element in the heap is always at the top. When a new element arrives:
- If it's smaller than the heap's minimum, it can't be in the top K. Skip it.
- If it's larger, it belongs in the top K. Push it, then pop the (now too small) minimum.

This keeps the heap at size K, so each push/pop is O(log K) instead of O(log n). After processing all n elements, the heap contains exactly the K largest.

```python
import heapq

def top_k_largest(stream, k):
    heap = []
    for val in stream:
        if len(heap) < k:
            heapq.heappush(heap, val)
        elif val > heap[0]:  # bigger than current smallest in top-K
            heapq.heapreplace(heap, val)  # pop smallest, push new
    return sorted(heap, reverse=True)  # heap contents are the top K
```

Why a min-heap for "largest"? Because the min-heap's top acts as a gatekeeper. It's the K-th largest element. Anything smaller doesn't make the cut. Anything larger bumps it out. At the end, everything in the heap beat the gatekeeper.

### The "merge K sorted lists" pattern

The second common pattern: merging K sorted sequences into one sorted output. Push the first element from each list onto a heap. Pop the smallest (that's the next output element). Push the next element from whichever list the popped element came from. Repeat.

The heap always holds at most K elements (one per list), so each pop/push is O(log K). Total: O(n log K) where n is the total number of elements.

This is used constantly in data engineering: merging sorted log files, consolidating sorted partitions, K-way external merge sort.

### Python heapq cheat sheet

```python
import heapq

heapq.heappush(heap, item)      # add item, O(log n)
heapq.heappop(heap)             # remove and return smallest, O(log n)
heap[0]                         # peek at smallest, O(1)
heapq.heapreplace(heap, item)   # pop then push (faster than separate calls)
heapq.heapify(list)             # convert list to heap in-place, O(n)
heapq.nlargest(k, iterable)     # return k largest, O(n log k)
heapq.nsmallest(k, iterable)    # return k smallest, O(n log k)
```

### Connection to data engineering

Heaps show up in DE work wherever you need the "best" or "worst" items from a stream:
- **Top-K queries** - "top 10 most expensive queries" from a stream of query logs
- **Merging sorted partitions** - consolidating pre-sorted files into one sorted output
- **Priority scheduling** - which task/job/event should be processed next?
- **Streaming medians** - finding the median of a data stream (two-heap approach)
- **Resource allocation** - always give the next job to the least-loaded worker

In SQL, many of these are `ORDER BY metric LIMIT K` or `PERCENTILE_CONT`. The heap is how you'd implement those efficiently in Python.

## When to Use It

**Recognition signals in interviews:**
- "Find the Kth largest/smallest..."
- "Merge K sorted..."
- "Top K most frequent..."
- "Running median/percentile..."
- "Priority-based processing..."
- Any time you need repeated access to the min or max without maintaining full sort order

**Recognition signals in DE work:**
- Top-N aggregations across large datasets
- Merging sorted partitions or files
- Priority queues for task scheduling
- Streaming percentile calculations

## Visual Aid

```
Top-K pattern: Find 3 largest from a stream

Stream: [12, 340, 5, 890, 23, 1200, 45, 67]
K = 3, using a min-heap (gatekeeper = smallest in top-3)

  12:   heap = [12]              (size < 3, just push)
  340:  heap = [12, 340]         (size < 3, push)
  5:    heap = [5, 340, 12]      (size < 3, push. 5 becomes new min)
  890:  890 > min(5) → push 890, pop 5.  heap = [12, 340, 890]
  23:   23 > min(12) → push 23, pop 12.  heap = [23, 340, 890]
  1200: 1200 > min(23) → push 1200, pop 23. heap = [340, 890, 1200]
  45:   45 < min(340) → skip (can't be in top 3)
  67:   67 < min(340) → skip

  Result: [340, 890, 1200] = the 3 largest values

The heap acted as a gatekeeper. Its minimum (top) was the threshold.
Values below the threshold were rejected in O(1).
Values above required O(log 3) ≈ O(1) to process.
```

## Python's heapq Module

Python only provides a min-heap. There's no built-in max-heap. Three ways to handle this:

```python
import heapq

# Min-heap (default)
heap = []
heapq.heappush(heap, 5)
heapq.heappush(heap, 3)
heapq.heappop(heap)  # returns 3 (smallest)

# Max-heap (negate values)
heap = []
heapq.heappush(heap, -5)
heapq.heappush(heap, -3)
-heapq.heappop(heap)  # returns 5 (largest)

# Production shortcut
heapq.nlargest(3, items)   # top 3 largest
heapq.nsmallest(3, items)  # top 3 smallest
```

`heapq.nlargest` and `heapq.nsmallest` use a heap internally. Use them in production code. Use explicit heap operations in interviews to show you understand the mechanics.

## Three Patterns You Need to Know

### 1. Top-K Selection (min-heap of size K)

Maintain a min-heap of size K. The smallest element in the heap is the Kth largest overall. If a new element is bigger than the heap's min, swap it in.

```python
def top_k(stream, k):
    heap = []
    for val in stream:
        heapq.heappush(heap, val)
        if len(heap) > k:
            heapq.heappop(heap)  # remove smallest
    return sorted(heap, reverse=True)
```

### 2. K-Way Merge (min-heap of K pointers)

Merge K sorted sequences by tracking the smallest unprocessed element from each. The heap always has at most K entries (one per sequence).

```python
def merge_k_sorted(lists):
    heap = []
    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst[0], i, 0))

    result = []
    while heap:
        val, list_idx, elem_idx = heapq.heappop(heap)
        result.append(val)
        if elem_idx + 1 < len(lists[list_idx]):
            next_val = lists[list_idx][elem_idx + 1]
            heapq.heappush(heap, (next_val, list_idx, elem_idx + 1))
    return result
```

### 3. Two-Heap (running median)

Split elements into two heaps: a max-heap for the lower half and a min-heap for the upper half. The median is always at one of the two tops.

```python
# max_heap stores lower half (negated for max-heap behavior)
# min_heap stores upper half
# Balance: len(max_heap) == len(min_heap) or len(max_heap) == len(min_heap) + 1
```

## Time/Space Complexity

| Operation | Complexity |
|-----------|------------|
| heappush | O(log n) |
| heappop | O(log n) |
| heap[0] (peek min) | O(1) |
| heapify (build from list) | O(n) |
| Top-K from n elements | O(n log k) |
| Merge K lists of total n elements | O(n log k) |

Space: O(k) for top-K, O(k) for K-way merge, O(n) for two-heap median.

## Trade-offs

**Heap vs full sort:** A heap is better when you need the top K out of N items (O(n log k) vs O(n log n)). When k is small relative to n (top 10 out of 10 million), the difference is significant. If you need the full sorted order, just sort.

**Heap vs hash map + sort:** For "top K frequent" problems, you need both: a hash map to count frequencies, then a heap to find the top K counts. The hash map can't tell you the K largest on its own. The heap can't count frequencies.

**Min-heap vs max-heap:** Use a min-heap when tracking the "top K largest" (the gatekeeper is the smallest of the K largest). Use a max-heap when tracking the "top K smallest" or when you need to repeatedly remove the largest element.

**When heaps don't help:**
- If you need random access to elements by value (use a hash map)
- If you need elements in fully sorted order (use sorting)
- If k ≈ n (the heap doesn't save much vs sorting)

### Scale characteristics

A min-heap of k elements uses O(k) memory and O(log k) per insert/extract. For top-k problems, k is usually small (top 10, top 100), so heap operations are essentially O(1) in practice.

| Operation | Full sort | Heap (size k) | Savings at n=1B, k=100 |
|---|---|---|---|
| Top-k selection | O(n log n) | O(n log k) | ~3x faster (log 100 vs log 1B) |
| Memory | O(n) | O(k) | 10M x less memory |
| Streaming capable | No (need all data) | Yes (process one at a time) | Fundamental difference |

The streaming property is the heap's killer feature at scale. A heap of size k can process an infinite stream and always hold the current top-k. A sort requires all data in memory first.

**Distributed equivalent:** Top-k across distributed partitions: each partition maintains a local heap of size k, then merge the partition heaps (at most P*k elements, where P is partition count) with a final heap of size k. MapReduce top-k follows this pattern. In Spark: `df.orderBy(desc("count")).limit(k)` uses a heap internally per partition, then merges.

**Merge k sorted streams:** The heap enables efficient k-way merge in O(n log k) where n is total elements and k is the number of streams. This is the core of external merge sort: merge k sorted runs from disk by maintaining a heap of the smallest element from each run. It's also how Spark merges sorted partitions in a sort-merge join.

### SQL equivalent

`ORDER BY metric DESC LIMIT k` is the SQL top-k pattern. Internally, the query engine uses a heap to avoid fully sorting the data. Window functions like `RANK() OVER (ORDER BY metric DESC)` with a filter on rank <= k achieve the same result. The SQL section's window functions and aggregation subsections cover these patterns. APPROX_TOP_COUNT in BigQuery uses probabilistic structures (similar to Pattern 11) for approximate top-k on very large datasets.

## Problems

| # | Problem | Difficulty | Key Concept |
|---|---------|------------|-------------|
| [703](https://leetcode.com/problems/kth-largest-element-in-a-stream/) | [Kth Largest Element in a Stream](problems/703_kth_largest_stream.md) | Easy | Min-heap of size K |
| [1046](https://leetcode.com/problems/last-stone-weight/) | [Last Stone Weight](problems/1046_last_stone_weight.md) | Easy | Max-heap (negate values) |
| [215](https://leetcode.com/problems/kth-largest-element-in-an-array/) | [Kth Largest Element in an Array](problems/215_kth_largest_array.md) | Medium | Selection problem, heap vs quickselect |
| [767](https://leetcode.com/problems/reorganize-string/) | [Reorganize String](problems/767_reorganize_string.md) | Medium | Greedy + max-heap |
| [23](https://leetcode.com/problems/merge-k-sorted-lists/) | [Merge K Sorted Lists](problems/023_merge_k_sorted.md) | Hard | K-way merge |
| [295](https://leetcode.com/problems/find-median-from-data-stream/) | [Find Median from Data Stream](problems/295_find_median_stream.md) | Hard | Two-heap technique |

**Suggested order:** 703, 1046 → 215 → 767 → 23 → 295

Start with 703 (cleanest min-heap example) and 1046 (introduces max-heap via negation). 215 adds the quickselect alternative. 767 combines heap with greedy logic. 23 and 295 are the two most important heap problems for DE interviews.

## DE Scenarios

| Scenario | What It Demonstrates |
|----------|---------------------|
| [Top-K Streaming](de_scenarios/top_k_streaming.md) | Finding top N records from large datasets |
| [K-Way Merge](de_scenarios/k_way_merge.md) | Merging sorted partitions or files |
| [Priority Task Scheduling](de_scenarios/priority_scheduling.md) | Processing items by priority/deadline |
| [Running Percentiles](de_scenarios/running_percentiles.md) | Streaming median and percentile calculations |

## Interview Tips

**What to say when you recognize this pattern:**
> "I need to efficiently track the top K elements. A min-heap of size K gives me O(n log k) instead of O(n log n) for a full sort. Each new element either gets discarded immediately or replaces the current minimum."

**Common follow-ups:**
- "Why a min-heap for finding the largest?" → The min-heap acts as a gatekeeper. Its top is the smallest of the K largest. Anything smaller than the top can't be in the top K, so we discard it in O(1).
- "What if K is close to N?" → Then sorting is simpler and about the same cost. The heap approach wins when K << N.
- "What about memory?" → The heap holds at most K elements. For top-10 out of a billion records, that's 10 elements in memory regardless of input size.

**Python-specific tips:**
- `heapq` is a min-heap. For max-heap, negate values.
- `heapq.heappush` and `heapq.heappop` are the core operations.
- `heapq.heappushpop(heap, val)` is faster than push then pop (single sift operation).
- `heapq.nlargest(k, iterable)` is the Pythonic production solution.
- Tuples are compared element by element: `(priority, data)` works naturally for priority queues.

**What the interviewer evaluates across heap problems:**

- **703 (Kth Largest Stream):** Understanding that a min-heap (not max-heap) of size k gives the kth largest is the core insight. Many candidates reach for a max-heap and process k elements, which is O(n log n). The min-heap approach is O(n log k). Explaining the streaming property (can handle infinite input in bounded memory) shows you think beyond batch processing.
- **1046 (Last Stone Weight):** This is a straightforward heap simulation. The interviewer expects quick, clean execution. The real test is whether you reach for a max-heap naturally (Python requires negation for max-heap behavior) and handle the re-insertion logic correctly. Finishing fast opens time for harder problems.
- **215 (Kth Largest):** This tests whether you know multiple selection algorithms. Quickselect (O(n) average) vs heap (O(n log k)) vs full sort (O(n log n)). Discussing the time-space-predictability tradeoff shows mature engineering judgment. The follow-up "what about distributed data?" tests system design thinking.
- **023 (Merge K Sorted):** k-way merge is a fundamental operation. The heap provides O(log k) per element extraction, making the total O(n log k). Understanding that this is the basis of external merge sort and sort-merge joins is the principal-level differentiator. The interviewer may ask "what if k is very large?" (answer: multi-level merge - merge groups of k' lists, then merge the results).
- **295 (Find Median Stream):** The two-heap data structure is non-obvious and tests design creativity. Maintaining the balance invariant (size difference <= 1) at each insert is where bugs occur. The follow-up "what about distributed streams?" is a principal-level question. Mentioning t-digest or APPROX_QUANTILES shows production awareness.

## Related Patterns

- **Hash Map** - Often combined: count frequencies with a hash map, then use a heap to select top K. See problem 347 in the hash map section.
- **Two Pointers** - Merging 2 sorted lists uses two pointers (O(n+m)). Merging K sorted lists uses a heap (O(n log k)) because tracking K pointers manually becomes unwieldy.
- **Sliding Window** - Sliding window maximum uses a monotonic deque instead of a heap. A heap can't efficiently evict elements that leave the window.
- **Binary Search** - Binary search on answer sometimes replaces heap-based optimization when you need a threshold rather than exact top-K.

## What's Next

After completing the heap problems, move to [Graph / Topological Sort](../06_graph_topological_sort/) for DAG ordering and dependency resolution - patterns that show up in every pipeline orchestration system.

