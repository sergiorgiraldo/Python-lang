# CC Prompt: Full Rework - Pattern 05 Heap (Part 2 of 2)

## What This Prompt Does

Continues from Part 1. Rewrites worked examples + approach explanations for problems 767, 023, 295 and all 4 DE scenarios.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- Only modify `.md` files. REPLACE `## Worked Example` sections and `📝 Explanation` content.
- Leave `💡 Hint` and `💻 Code` blocks untouched.
- NO Oxford commas, NO em dashes, NO exclamation points

---

## 767_reorganize_string.md

**Replace `## Worked Example` with:**

```markdown
## Worked Example

To avoid adjacent duplicates, always place the most frequent character next. A max-heap tracks character frequencies. At each step, pop the most frequent character, place it, decrement its count and push the previously popped character back (the one placed in the prior step). Holding one character back prevents placing the same character twice in a row.

```
Input: s = "aababcc"
Counts: a=3, b=2, c=2. Total=7.

Max-heap (negate for Python min-heap): [(-3,'a'), (-2,'b'), (-2,'c')]

  Step 1: pop (-3,'a') → place 'a'. prev=None. Result: "a"
          Hold 'a' (count now 2) for next step.
  Step 2: pop (-2,'b') → place 'b'. Push back prev ('a',2). Result: "ab"
          Heap: [(-2,'a'), (-2,'c')]. Hold 'b' (count 1).
  Step 3: pop (-2,'a') → place 'a'. Push back 'b' (1). Result: "aba"
          Heap: [(-1,'b'), (-2,'c')]. Hold 'a' (count 1).
  Step 4: pop (-2,'c') → place 'c'. Push back 'a' (1). Result: "abac"
          Heap: [(-1,'a'), (-1,'b')]. Hold 'c' (count 1).
  Step 5: pop (-1,'a') → place 'a'. Push back 'c' (1). Result: "abaca"
          Heap: [(-1,'c'), (-1,'b')]. Hold 'a' (count 0, don't push).
  Step 6: pop (-1,'b') → place 'b'. Push back nothing. Result: "abacab"
          Heap: [(-1,'c')]. Hold 'b' (count 0).
  Step 7: pop (-1,'c') → place 'c'. Result: "abacabc"
          Heap empty. Done.

No adjacent duplicates. The greedy choice (most frequent first) works
because it spreads the most common character as widely as possible.
If any character count > (n+1)/2, it's impossible.
```
```

**Replace approach explanations:**

Approach 1 (Sort/Interleave) `📝 Explanation`:
```
Sort by frequency. Place the most frequent characters at even indices (0, 2, 4...) and the rest at odd indices (1, 3, 5...). This guarantees no adjacent duplicates if a valid arrangement exists.

**Time:** O(n log n) for sorting (or O(n) if using counting sort for bounded alphabet).
**Space:** O(n) - the result array.

Simpler to implement than the heap approach but less intuitive for variable-length strings.
```

Approach 2 (Max-Heap Greedy) `📝 Explanation`:
```
Use a max-heap (negate counts for Python's min-heap) to always place the most frequent remaining character. The trick: after placing a character, don't push it back immediately. Hold it for one round and push it back at the *next* step. This prevents placing the same character consecutively.

1. Count character frequencies with Counter.
2. Build a max-heap of (-count, char) pairs.
3. Track the previously placed character. At each step: pop the most frequent, place it, push the previous character back (if its count > 0), save current as previous.
4. If the heap is empty but we haven't placed all characters, return "" (impossible).

The arrangement is impossible when any single character appears more than ⌈n/2⌉ times (there aren't enough "spacer" positions between its occurrences).

**Time:** O(n log k) where k is the number of unique characters (at most 26 for lowercase letters, so effectively O(n)).
**Space:** O(k) for the heap.
```

---

## 023_merge_k_sorted.md

**Replace `## Worked Example` with:**

```markdown
## Worked Example

Merging K sorted lists is the multi-way version of the two-pointer merge from Pattern 02. Instead of two pointers (one per list), we use a min-heap of size K. The heap always holds the smallest unprocessed element from each list. Pop the minimum, add it to the output, push the next element from that same list.

The heap replaces the "compare all K current elements" step (which would be O(K) per element) with an O(log K) operation. Total: O(n log K) instead of O(nK).

```
Input: lists = [[1, 4, 7], [2, 5, 8], [3, 6, 9]]

Initialize heap with first element from each list:
  heap = [(1, list0), (2, list1), (3, list2)]

  Pop min=1 (list0). Output: [1]. Push next from list0 (4).
    heap = [(2, list1), (3, list2), (4, list0)]

  Pop min=2 (list1). Output: [1,2]. Push next from list1 (5).
    heap = [(3, list2), (4, list0), (5, list1)]

  Pop min=3 (list2). Output: [1,2,3]. Push next from list2 (6).
    heap = [(4, list0), (5, list1), (6, list2)]

  Pop 4 → push 7. Output: [1,2,3,4]
  Pop 5 → push 8. Output: [1,2,3,4,5]
  Pop 6 → push 9. Output: [1,2,3,4,5,6]
  Pop 7 → list0 exhausted. Output: [1,2,3,4,5,6,7]
  Pop 8 → list1 exhausted. Output: [1,2,3,4,5,6,7,8]
  Pop 9 → list2 exhausted. Output: [1,2,3,4,5,6,7,8,9]

Heap never held more than 3 entries (one per list).
9 elements × O(log 3) per operation ≈ 14 total operations.
```
```

**Replace approach explanations:**

Approach 1 (Flatten and Sort) `📝 Explanation`:
```
Dump all elements from all lists into one big list. Sort it.

**Time:** O(n log n) where n is the total number of elements across all lists.
**Space:** O(n).

Ignores the fact that the inputs are already sorted. Simple but wasteful for large k.
```

Approach 2 (Sequential Merge) `📝 Explanation`:
```
Merge the first two lists, then merge the result with the third, then the fourth, and so on.

This is equivalent to k-1 two-way merges. The problem: early elements get re-merged repeatedly. The first list's elements participate in every merge step.

**Time:** O(n × k) - in the worst case, each element is involved in O(k) merge operations.
**Space:** O(n) for the merged result.

Better than brute force when k is small. Degrades for large k.
```

Approach 3 (K-Way Heap Merge) `📝 Explanation`:
```
Initialize a min-heap with the first element from each of the K lists (along with which list it came from and its position in that list).

Repeatedly:
1. Pop the minimum element from the heap. Add it to the output.
2. If that element's list has more elements, push the next element from the same list onto the heap.

The heap always holds at most K entries (one per list). Each push/pop is O(log K). Every element across all lists gets pushed and popped exactly once.

**Time:** O(n log K) where n is total elements. Each element does one push and one pop, each O(log K).
**Space:** O(K) for the heap (plus O(n) for the output).

This is the optimal approach. In data engineering, this is the algorithm behind merging sorted partitions, K-way external sort and ordered stream merging.
```

---

## 295_find_median_stream.md

**Replace `## Worked Example` with:**

```markdown
## Worked Example

Finding the median of a stream requires constant access to the middle element(s). Two heaps do this: a max-heap for the smaller half and a min-heap for the larger half. The median is either the top of the max-heap (odd count) or the average of both tops (even count).

The balancing rule: the max-heap can have at most one more element than the min-heap. After every insertion, rebalance if the sizes differ by more than 1.

```
Stream: 5, 3, 8, 1, 7, 2

  add 5: max_heap=[5], min_heap=[]
         Odd count → median = top of max = 5

  add 3: 3 ≤ 5 → goes to max_heap. max_heap=[5,3], min_heap=[]
         max_heap too big (size 2 vs 0). Move max top to min.
         max_heap=[3], min_heap=[5]
         Even count → median = (3+5)/2 = 4.0

  add 8: 8 > 5 (min top) → goes to min_heap. max_heap=[3], min_heap=[5,8]
         min_heap bigger. Move min top to max.
         max_heap=[5,3], min_heap=[8]
         Odd → median = top of max = 5

  add 1: 1 ≤ 5 → max_heap. max_heap=[5,3,1], min_heap=[8]
         max_heap too big (3 vs 1). Move top to min.
         max_heap=[3,1], min_heap=[5,8]
         Even → median = (3+5)/2 = 4.0

  add 7: 7 > 5? No, 7 > 3 (max top)? Yes → min_heap. max=[3,1], min=[5,7,8]
         min bigger. Move min top to max.
         max_heap=[5,3,1], min_heap=[7,8]
         Odd → median = 5

  add 2: 2 ≤ 5 → max_heap. max=[5,3,2,1], min=[7,8]
         max too big (4 vs 2). Move top to min.
         max_heap=[3,2,1], min_heap=[5,7,8]
         Even → median = (3+5)/2 = 4.0

Sorted stream would be [1,2,3,5,7,8]. Median = (3+5)/2 = 4.0. Correct.
Each insertion: O(log n). Finding median: O(1).
```
```

**Replace approach explanations:**

Approach 1 (Sort on Demand) `📝 Explanation`:
```
Maintain a list. On each `addNum`, append the value. On `findMedian`, sort the list and return the middle element(s).

**Time:** O(n log n) per findMedian call. O(1) per addNum.
**Space:** O(n).

Simple but expensive if findMedian is called frequently. Fine for sparse median queries on small streams.
```

Approach 2 (Two Heaps) `📝 Explanation`:
```
Split the stream into two halves using two heaps:
- **max-heap** (stores the smaller half, largest of the small half at top)
- **min-heap** (stores the larger half, smallest of the large half at top)

Insertion rule: if the new value ≤ max-heap's top, it belongs in the smaller half (push to max-heap). Otherwise it belongs in the larger half (push to min-heap).

Balancing rule: after each insertion, if the heaps' sizes differ by more than 1, move the top element from the bigger heap to the smaller one. The max-heap is allowed to have one extra element (for odd-length streams).

Finding median:
- Odd count: top of max-heap (the larger half's boundary element).
- Even count: average of both tops.

**Time:** O(log n) per addNum (one or two heap operations). O(1) per findMedian.
**Space:** O(n) - all elements stored across both heaps.

The two-heap approach is one of the most elegant data structure combinations in algorithm design. It maintains a "live partition" of the data where the median is always at the boundary.
```

---

## DE Scenarios

### de_scenarios/top_k_streaming.md

```markdown
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
```

### de_scenarios/k_way_merge.md

```markdown
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
```

### de_scenarios/priority_scheduling.md

```markdown
## Worked Example

Job scheduling with priorities. A min-heap (priority = urgency) ensures the highest-priority job is always processed next. Jobs can arrive at any time and get inserted in O(log n).

```
Job queue (lower number = higher priority):
  submit(priority=3, "daily_report")    → heap: [(3, daily_report)]
  submit(priority=1, "hotfix_deploy")   → heap: [(1, hotfix), (3, daily)]
  submit(priority=5, "weekly_cleanup")  → heap: [(1, hotfix), (3, daily), (5, weekly)]

  process_next() → pop (1, hotfix_deploy). Run it.
    heap: [(3, daily_report), (5, weekly_cleanup)]

  submit(priority=2, "data_backfill")   → heap: [(2, backfill), (3, daily), (5, weekly)]

  process_next() → pop (2, data_backfill). Run it.
    heap: [(3, daily_report), (5, weekly_cleanup)]

  process_next() → pop (3, daily_report). Run it.

Each submit: O(log n). Each process_next: O(log n).
Compared to a sorted list: insert is O(n) (shift elements).
```
```

### de_scenarios/running_percentiles.md

```markdown
## Worked Example

Tracking the median (or any percentile) of a data stream in real-time using two heaps. Same as Find Median from Data Stream (problem 295) applied to monitoring.

```
Monitoring API response times (ms), tracking live median:

  t=1: latency=45   max_heap=[45], min_heap=[]         median=45
  t=2: latency=120  max_heap=[45], min_heap=[120]       median=(45+120)/2=82.5
  t=3: latency=67   max_heap=[67,45], min_heap=[120]    median=67
  t=4: latency=200  max_heap=[67,45], min_heap=[120,200] median=(67+120)/2=93.5
  t=5: latency=55   max_heap=[67,55,45], min_heap=[120,200] median=67

  Dashboard shows: "Current median response time: 67ms"

  Each update: O(log n). Query median: O(1).
  For a sliding window variant (last N requests), combine with
  a mechanism to expire old values from the heaps.
```
```

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns
git diff --name-only | grep -v '.md$'
uv run pytest patterns/05_heap_priority_queue/ -v --tb=short 2>&1 | tail -5

echo "=== Worked Example count ==="
grep -rl "## Worked Example" patterns/05_heap_priority_queue/ | wc -l
echo "(should be 10: 6 problems + 4 DE scenarios)"
```
