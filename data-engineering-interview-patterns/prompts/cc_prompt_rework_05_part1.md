# CC Prompt: Full Rework - Pattern 05 Heap (Part 1 of 2)

## What This Prompt Does

Rewrites the README "What Is It?", "Visual Aid" and "Trade-offs" sections, plus `## Worked Example` and `📝 Explanation` blocks for the first 3 problems.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

Same as all previous patterns. Only `.md` files. NO Oxford commas, NO em dashes, NO exclamation points.

---

## Task 1: Rewrite README Sections

### Replace `## What Is It?` (everything up to `## When to Use It`)

```markdown
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
```

### Replace `## Visual Aid` (up to `## Template`)

```markdown
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
```

### Replace `## Trade-offs` (up to `## Problems in This Section`)

```markdown
## Trade-offs

**Heap vs full sort:** A heap is better when you need the top K out of N items (O(n log k) vs O(n log n)). When k is small relative to n (top 10 out of 10 million), the difference is significant. If you need the full sorted order, just sort.

**Heap vs hash map + sort:** For "top K frequent" problems, you need both: a hash map to count frequencies, then a heap to find the top K counts. The hash map can't tell you the K largest on its own. The heap can't count frequencies.

**Min-heap vs max-heap:** Use a min-heap when tracking the "top K largest" (the gatekeeper is the smallest of the K largest). Use a max-heap when tracking the "top K smallest" or when you need to repeatedly remove the largest element.

**When heaps don't help:**
- If you need random access to elements by value (use a hash map)
- If you need elements in fully sorted order (use sorting)
- If k ≈ n (the heap doesn't save much vs sorting)
```

---

## Task 2: Problems 1-3

### Kth Largest Element in a Stream (703)

**Worked Example:**

```markdown
## Worked Example

Maintain a min-heap of size K. The top of the heap is always the Kth largest element overall. When a new element arrives, compare it to the heap's minimum. If it's larger, it enters the top K and the previous Kth largest gets bumped out. If it's smaller, it can't affect the top K.

The heap key is just the number itself. We want the smallest of the top-K group to stay at the top as the gatekeeper.

```
KthLargest(k=3, nums=[4, 5, 8, 2])

  Initialize: push all, maintain heap size 3.
    Push 4: heap = [4]
    Push 5: heap = [4, 5]
    Push 8: heap = [4, 5, 8]
    Push 2: 2 < heap min (4) → skip (not in top 3).
  heap = [4, 5, 8]. Kth largest = heap[0] = 4.

  add(3): 3 < 4 → skip. Return 4.
  add(5): 5 > 4 → push 5, pop 4. heap = [5, 5, 8]. Return 5.
  add(10): 10 > 5 → push 10, pop 5. heap = [5, 8, 10]. Return 5.
  add(9): 9 > 5 → push 9, pop 5. heap = [8, 9, 10]. Return 8.
  add(4): 4 < 8 → skip. Return 8.

  The heap always holds the 3 largest elements seen so far.
  heap[0] is always the 3rd largest (the smallest of the top 3).
```
```

**Approach 1: Sort on Every Add - replace explanation:**

```
Keep all elements in a sorted list. After each add, re-sort and return the element at index len-k.

**Time:** O(n log n) per add (re-sorting the full list).
**Space:** O(n) - storing all elements.

This works for small inputs but doesn't scale. After 10,000 adds, each add sorts a list of 10,000+ elements.
```

**Approach 2: Min-Heap of Size K - replace explanation:**

```
Maintain a min-heap of exactly K elements. The heap's minimum (top) is always the Kth largest element overall.

On initialization: push all elements, keeping only the K largest (pop the smallest whenever heap size exceeds K).

On each add:
- If the new element <= heap minimum: it can't be in the top K. Return heap[0].
- If the new element > heap minimum: push it, pop the smallest (which was the old Kth largest but is now K+1th). Return the new heap[0].

Why a min-heap and not max-heap? The min-heap's top IS the answer (the Kth largest = the smallest of the top K). A max-heap's top would be the 1st largest, which is not what we need.

**Time:** O(log K) per add (heap push/pop). Initialization: O(n log K).
**Space:** O(K) - the heap holds exactly K elements.

When K=10 and we've processed 10 million elements, each add does O(log 10) ≈ O(1) work. Much better than re-sorting 10 million elements.
```

### Last Stone Weight (1046)

**Worked Example:**

```markdown
## Worked Example

Repeatedly pick the two heaviest stones, smash them together, and if they're different weights, the remainder goes back. A max-heap (negate values for Python's min-heap) gives O(log n) access to the two heaviest stones at each step.

```
Input: stones = [2, 7, 4, 1, 8, 1]

  Max-heap (stored as negated): [-8, -7, -4, -2, -1, -1]
  (heap[0] = -8, so the heaviest stone is 8)

  Round 1: Pop two heaviest: 8 and 7. |8-7| = 1. Push 1 back.
    heap: [-4, -2, -1, -1, -1]

  Round 2: Pop 4 and 2. |4-2| = 2. Push 2.
    heap: [-2, -1, -1, -1]

  Round 3: Pop 2 and 1. |2-1| = 1. Push 1.
    heap: [-1, -1, -1]

  Round 4: Pop 1 and 1. |1-1| = 0. Both destroyed.
    heap: [-1]

  Only 1 stone left. Return 1.
```
```

**Approach 1: Sort Each Round - replace explanation:**

```
Sort the stones, pop the two largest, compute the result, add it back if non-zero. Repeat until one or zero stones remain.

Each round: sort the entire list (O(n log n)), pop twice (O(1)), and potentially insert (O(1) append + re-sort next round).

**Time:** O(n² log n) - up to n rounds, each requiring an O(n log n) sort.
**Space:** O(1) extra (sorting in-place).
```

**Approach 2: Max-Heap - replace explanation:**

```
Build a max-heap from the stones. Repeatedly pop the two largest, compute the difference, and push it back if non-zero. Stop when one or zero stones remain.

Python's heapq is a min-heap, so negate all values. Push `-stone` to simulate a max-heap. Pop gives the most negative value (= largest stone).

1. `heap = [-s for s in stones]`, then `heapify(heap)`.
2. While `len(heap) > 1`:
   - Pop twice: `first = -heappop(heap)`, `second = -heappop(heap)`.
   - If `first != second`: push `-(first - second)`.
3. Return `-heap[0]` if heap is non-empty, else 0.

**Time:** O(n log n) - up to n rounds, each doing O(log n) heap operations.
**Space:** O(n) - the heap.

Much better than re-sorting each round. The heap maintains the "who's heaviest?" property automatically as stones are removed and remainders added.
```

### Kth Largest Element in an Array (215)

**Worked Example:**

```markdown
## Worked Example

Find the Kth largest element. This is the same "maintain a min-heap of size K" pattern, but applied to a fixed array (not a stream). The heap acts as a gatekeeper that keeps exactly the K largest elements.

```
Input: nums = [3, 2, 1, 5, 6, 4], k = 2

  Min-heap of size 2:
    Push 3: heap = [3]
    Push 2: heap = [2, 3]      (size = k = 2, full)
    Push 1: 1 < min(2) → skip. heap = [2, 3]
    Push 5: 5 > min(2) → push 5, pop 2. heap = [3, 5]
    Push 6: 6 > min(3) → push 6, pop 3. heap = [5, 6]
    Push 4: 4 < min(5) → skip. heap = [5, 6]

  The 2nd largest = heap[0] = 5. (The two largest are 5 and 6.)

Full sort for comparison: sorted = [1, 2, 3, 4, 5, 6]
  Index n-k = 6-2 = 4 → value 5. Same answer.
```
```

**Approach 1: Sort - replace explanation:**

```
Sort the array and return the element at index `n - k` (0-indexed). Simple and correct.

**Time:** O(n log n) - dominated by the sort.
**Space:** O(1) if sorting in-place, O(n) with `sorted()`.

Fine for a first answer. Then optimize with the heap or Quickselect approaches.
```

**Approach 2: Min-Heap of Size K - replace explanation:**

```
Same approach as the Kth Largest in Stream problem: maintain a min-heap of size K. Process all elements through the gatekeeper. The heap's minimum at the end is the Kth largest.

**Time:** O(n log k) - each of the n elements does at most one heap push/pop (O(log k) each).
**Space:** O(k) - heap holds exactly k elements.

Better than sorting when k is much smaller than n. For k=10 and n=10 million: O(10M × log 10) ≈ O(10M × 3) vs O(10M × log 10M) ≈ O(10M × 23).
```

**Approach 3: Quickselect - replace explanation:**

```
Quickselect is a partition-based algorithm (related to Quicksort) that finds the Kth element without fully sorting. It picks a pivot, partitions the array so elements smaller than the pivot are on the left and larger on the right, then recurses into whichever side contains the Kth position.

On average, each step halves the problem (like binary search on the array). But unlike binary search, it rearranges elements.

**Time:** O(n) average (each step does O(n) work on a halved partition). O(n²) worst case (bad pivot choices, rare with randomization).
**Space:** O(1) extra - in-place partitioning.

Quickselect is the theoretically optimal approach (O(n) average) but the worst case and implementation complexity make the heap approach more practical in interviews. Mention Quickselect to show you know it exists, but implement the heap unless the interviewer asks for it.
```

---

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

git diff --name-only | grep -v '.md$'
uv run pytest patterns/05_heap/ -v --tb=short 2>&1 | tail -5

for section in "The basics" "How a heap is different" "Min-heap vs max-heap" "top K" "merge K sorted" "heapq cheat sheet"; do
    grep -q "$section" patterns/05_heap/README.md && echo "✅ $section" || echo "❌ $section"
done
```
