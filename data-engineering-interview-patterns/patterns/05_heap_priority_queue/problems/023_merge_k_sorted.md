# Merge K Sorted Lists (LeetCode #23)

🔗 [LeetCode 23: Merge K Sorted Lists](https://leetcode.com/problems/merge-k-sorted-lists/)

> **Difficulty:** Hard | **Interview Frequency:** Occasional

## Problem Statement

Given an array of k sorted linked lists, merge all lists into one sorted linked list.

**Example:**
```
Input: lists = [[1,4,5], [1,3,4], [2,6]]
Output: [1,1,2,3,4,4,5,6]
```

**Constraints:**
- k == lists.length
- 0 <= k <= 10^4
- 0 <= lists[i].length <= 500
- -10^4 <= lists[i][j] <= 10^4
- Each lists[i] is sorted in ascending order
- Total elements across all lists <= 10^4

---

## Thought Process

1. **Clarify** - Lists are already sorted individually. We need to produce one sorted output. Can lists be empty? (Yes.) Can k be 0? (Yes.)
2. **Brute force** - Concatenate everything, sort. O(n log n). Ignores the fact that inputs are already sorted.
3. **Sequential merge** - Merge list 0 with list 1, then result with list 2, etc. O(n * k) because early elements get re-merged multiple times.
4. **Key insight** - At any point, the next element in the output is the smallest unprocessed element across all k lists. A min-heap of size k gives us that in O(log k).

---

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

---

## Approaches

### Approach 1: Concatenate and Sort (Brute Force)

<details>
<summary>📝 Explanation</summary>

Dump all elements from all lists into one big list. Sort it.

**Time:** O(n log n) where n is the total number of elements across all lists.
**Space:** O(n).

Ignores the fact that the inputs are already sorted. Simple but wasteful for large k.

</details>

<details>
<summary>💻 Code</summary>

```python
def merge_k_sorted_brute(lists):
    combined = []
    for lst in lists:
        combined.extend(lst)
    return sorted(combined)
```

</details>

---

### Approach 2: Sequential Two-Way Merge

<details>
<summary>📝 Explanation</summary>

Merge the first two lists, then merge the result with the third, then the fourth, and so on.

This is equivalent to k-1 two-way merges. The problem: early elements get re-merged repeatedly. The first list's elements participate in every merge step.

**Time:** O(n × k) - in the worst case, each element is involved in O(k) merge operations.
**Space:** O(n) for the merged result.

Better than brute force when k is small. Degrades for large k.

</details>

<details>
<summary>💻 Code</summary>

```python
def merge_k_sorted_sequential(lists):
    if not lists:
        return []

    def merge_two(a, b):
        result, i, j = [], 0, 0
        while i < len(a) and j < len(b):
            if a[i] <= b[j]:
                result.append(a[i]); i += 1
            else:
                result.append(b[j]); j += 1
        result.extend(a[i:]); result.extend(b[j:])
        return result

    merged = lists[0]
    for i in range(1, len(lists)):
        merged = merge_two(merged, lists[i])
    return merged
```

</details>

---

### Approach 3: Min-Heap K-Way Merge (Optimal)

<details>
<summary>💡 Hint 1</summary>

The next element in the output is always the smallest unprocessed element across all k lists.

</details>

<details>
<summary>💡 Hint 2</summary>

You don't need to compare all k heads every time. A min-heap of size k does it in O(log k).

</details>

<details>
<summary>📝 Explanation</summary>

Initialize a min-heap with the first element from each of the K lists (along with which list it came from and its position in that list).

Repeatedly:
1. Pop the minimum element from the heap. Add it to the output.
2. If that element's list has more elements, push the next element from the same list onto the heap.

The heap always holds at most K entries (one per list). Each push/pop is O(log K). Every element across all lists gets pushed and popped exactly once.

**Time:** O(n log K) where n is total elements. Each element does one push and one pop, each O(log K).
**Space:** O(K) for the heap (plus O(n) for the output).

This is the optimal approach. In data engineering, this is the algorithm behind merging sorted partitions, K-way external sort and ordered stream merging.

</details>

<details>
<summary>💻 Code</summary>

```python
import heapq

def merge_k_sorted_arrays(lists):
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

</details>

---

### Approach 4: Lazy Generator Merge (DE-Specific)

<details>
<summary>📝 Explanation</summary>

Same heap algorithm but yields elements one at a time instead of building a result list. Memory usage is O(k) regardless of total data size.

This is the pattern for merging sorted files, database cursors or Kafka partitions when the combined output doesn't fit in memory.

**Time:** O(n log k)
**Space:** O(k) - no result list in memory

</details>

<details>
<summary>💻 Code</summary>

```python
import heapq

def merge_k_sorted_lazy(iterables):
    heap = []
    iterators = [iter(it) for it in iterables]
    for i, iterator in enumerate(iterators):
        first = next(iterator, None)
        if first is not None:
            heapq.heappush(heap, (first, i))

    while heap:
        val, src_idx = heapq.heappop(heap)
        yield val
        nxt = next(iterators[src_idx], None)
        if nxt is not None:
            heapq.heappush(heap, (nxt, src_idx))
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Empty outer list | `[]` | `[]` | No lists to merge |
| All empty lists | `[[], [], []]` | `[]` | Lists exist but have no data |
| Some empty | `[[1,3], [], [2,4]]` | `[1,2,3,4]` | Skip None/empty in heap init |
| Single list | `[[1,2,3]]` | `[1,2,3]` | Heap has k=1, effectively a passthrough |
| All single elements | `[[5], [2], [8]]` | `[2,5,8]` | One pop per list, no push-back |
| Duplicates across lists | `[[1,1], [1,1]]` | `[1,1,1,1]` | Tie-breaking must be deterministic |

---

## Common Pitfalls

1. **Comparing ListNodes directly** - Python can't compare custom objects in the heap. Use a tuple like `(value, list_index, node)` where `list_index` breaks ties.
2. **Forgetting to check for empty lists** - If a list is empty or None, don't push it onto the heap.
3. **Pushing from an exhausted list** - After popping, check that the list has a next element before pushing.

---

## Interview Tips

**What to say:**
> "I'll use a min-heap of size k to always find the next smallest element across all lists. Initialize with the first element from each list, then pop the minimum and push the next element from the same list. Each element is processed exactly once in O(log k) time."

**Common follow-ups:**
- "What if the lists are files on disk?" → Use the lazy generator approach. Read one element at a time from each file. The heap holds k elements regardless of file sizes.
- "How does this compare to merging two at a time?" → Sequential merge is O(n * k) because early elements get re-merged. The heap approach is O(n log k). For k=1000, that's 1000x vs 10x overhead.
- "What about `heapq.merge`?" → Python's standard library has `heapq.merge(*iterables)` which does exactly this. Mentioning it shows production awareness.

**What the interviewer evaluates:** k-way merge is a fundamental operation. The heap provides O(log k) per element extraction, making the total O(n log k). Understanding that this is the basis of external merge sort and sort-merge joins is the principal-level differentiator. The interviewer may ask "what if k is very large?" (answer: multi-level merge - merge groups of k' lists, then merge the results).

---

## DE Application

This is the core algorithm behind:
- **External sort:** Sort chunks that fit in memory, write to files, then K-way merge the sorted files
- **Merging sorted partitions:** Spark, Hive and BigQuery all use K-way merge when combining sorted partition output
- **CDC stream merge:** Combining change streams from multiple shards into a single ordered stream
- **Compaction in LSM trees:** RocksDB, LevelDB and Cassandra merge sorted SSTables using this exact algorithm
- **Multi-source ETL:** Merging time-series data from multiple APIs or databases into a single ordered feed

The lazy generator version is particularly important: it processes arbitrarily large data with O(k) memory.

Pattern 02 (Two Pointers) covered merging 2 sorted sequences. This generalizes to K sequences. When K=2, the heap approach reduces to the same two-pointer merge.

See: [K-Way Merge DE Scenario](../de_scenarios/k_way_merge.md)

## At Scale

The k-way merge with a heap is O(n log k) where n is total elements across all lists. This is the core algorithm for external merge sort and sort-merge joins in databases. Merging 1000 sorted files of 1GB each (1TB total) requires a heap of size 1000 and sequential reads from each file. Total comparisons: 1B * log(1000) = 10B. The heap is tiny (1000 entries) but I/O is the bottleneck: reading 1TB sequentially. The practical optimization is to use large read buffers per file to minimize disk seeks. In Spark, sort-merge joins merge sorted partitions using exactly this algorithm. Understanding k-way merge is essential for debugging slow sort-merge operations.

---

## Related Problems

- [088. Merge Sorted Array](../../02_two_pointers/problems/088_merge_sorted.md) - Two-way merge with two pointers (K=2 special case)
- [703. Kth Largest Element in a Stream](703_kth_largest_stream.md) - Different heap use (top-K vs merge)
- [295. Find Median from Data Stream](295_find_median_stream.md) - Two-heap technique
