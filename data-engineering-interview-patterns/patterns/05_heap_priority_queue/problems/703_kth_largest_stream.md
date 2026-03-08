# Kth Largest Element in a Stream (LeetCode #703)

🔗 [LeetCode 703: Kth Largest Element in a Stream](https://leetcode.com/problems/kth-largest-element-in-a-stream/)

> **Difficulty:** Easy | **Interview Frequency:** Occasional

## Problem Statement

Design a class that finds the kth largest element in a stream. It should support two operations: initializing with an array and adding new elements.

Each time `add` is called, return the kth largest element in the stream so far.

**Example:**
```
KthLargest(3, [4, 5, 8, 2])
add(3)  → 4   (sorted: [2, 3, 4, 5, 8], 3rd largest = 4)
add(5)  → 5   (sorted: [2, 3, 4, 5, 5, 8], 3rd largest = 5)
add(10) → 5   (sorted: [2, 3, 4, 5, 5, 8, 10], 3rd largest = 5)
add(9)  → 8   (sorted: [2, 3, 4, 5, 5, 8, 9, 10], 3rd largest = 8)
add(4)  → 8   (sorted: [2, 3, 4, 4, 5, 5, 8, 9, 10], 3rd largest = 8)
```

**Constraints:**
- 1 <= k <= 10^4
- 0 <= nums.length <= 10^4
- -10^4 <= nums[i] <= 10^4
- At most 10^4 calls to add

---

## Thought Process

1. **Clarify** - Is k fixed for the lifetime of the object? (Yes.) Can the initial array be empty? (Yes.) Can it have fewer than k elements? (Yes, but add will be called enough times to fill it.)
2. **Brute force** - Keep all elements, sort on each add, return the kth. O(n log n) per add.
3. **Spot the waste** - We don't need the full sorted order. We only need the kth largest.
4. **Key insight** - A min-heap of size k always has the kth largest at its top. Elements smaller than the top can never be in the top k, so we discard them.

---

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

---

## Approaches

### Approach 1: Sort on Every Add (Brute Force)

<details>
<summary>💡 Hint</summary>

Keep all elements in a list. Sort after each add. Return the kth from the end.

</details>

<details>
<summary>📝 Explanation</summary>

Keep all elements in a sorted list. After each add, re-sort and return the element at index len-k.

**Time:** O(n log n) per add (re-sorting the full list).
**Space:** O(n) - storing all elements.

This works for small inputs but doesn't scale. After 10,000 adds, each add sorts a list of 10,000+ elements.

</details>

<details>
<summary>💻 Code</summary>

```python
class KthLargestSort:
    def __init__(self, k: int, nums: list[int]) -> None:
        self.k = k
        self.nums = sorted(nums, reverse=True)

    def add(self, val: int) -> int:
        self.nums.append(val)
        self.nums.sort(reverse=True)
        return self.nums[self.k - 1]
```

</details>

---

### Approach 2: Min-Heap of Size K (Optimal)

<details>
<summary>💡 Hint 1</summary>

You don't need the full sorted order. You only need to know the kth largest.

</details>

<details>
<summary>💡 Hint 2</summary>

If you keep exactly k elements and the smallest of those k is at the top, what does the top represent?

</details>

<details>
<summary>📝 Explanation</summary>

Maintain a min-heap of exactly K elements. The heap's minimum (top) is always the Kth largest element overall.

On initialization: push all elements, keeping only the K largest (pop the smallest whenever heap size exceeds K).

On each add:
- If the new element <= heap minimum: it can't be in the top K. Return heap[0].
- If the new element > heap minimum: push it, pop the smallest (which was the old Kth largest but is now K+1th). Return the new heap[0].

Why a min-heap and not max-heap? The min-heap's top IS the answer (the Kth largest = the smallest of the top K). A max-heap's top would be the 1st largest, which is not what we need.

**Time:** O(log K) per add (heap push/pop). Initialization: O(n log K).
**Space:** O(K) - the heap holds exactly K elements.

When K=10 and we've processed 10 million elements, each add does O(log 10) ≈ O(1) work. Much better than re-sorting 10 million elements.

</details>

<details>
<summary>💻 Code</summary>

```python
import heapq

class KthLargest:
    def __init__(self, k: int, nums: list[int]) -> None:
        self.k = k
        self.heap: list[int] = []
        for num in nums:
            self._push(num)

    def _push(self, val: int) -> None:
        if len(self.heap) < self.k:
            heapq.heappush(self.heap, val)
        elif val > self.heap[0]:
            heapq.heapreplace(self.heap, val)

    def add(self, val: int) -> int:
        self._push(val)
        return self.heap[0]
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Empty init | `k=2, nums=[], add(1), add(2)` | `1, 1` then `2` | Heap fills gradually |
| k=1 | `k=1, nums=[], add(5), add(3), add(10)` | `5, 5, 10` | Always tracking the max |
| All same values | `k=2, nums=[5,5,5], add(5)` | `5` | Duplicates are valid |
| Negative numbers | `k=2, nums=[-1,-2,-3], add(0)` | `-1` | Negatives work the same way |
| Init larger than k | `k=2, nums=[10,20,30,40], add(5)` | `30` | Init must also prune to size k |

---

## Common Pitfalls

1. **Using a max-heap instead of min-heap** - You want the kth largest, which is the *minimum* of the top k. A min-heap gives you that in O(1).
2. **Not handling init arrays larger than k** - If the initial array has more than k elements, you need to prune the heap down to size k during initialization.
3. **Forgetting heapq is a min-heap** - Python's heapq always pops the smallest. This is what you want for top-K largest.

---

## Interview Tips

**What to say:**
> "I'll maintain a min-heap of size k. The top of the heap is always the kth largest element. New elements smaller than the top get discarded in O(1). Larger elements replace the top in O(log k). This gives me constant-time access to the kth largest."

**Common follow-ups:**
- "What if k changes?" → You'd need to grow or shrink the heap. Growing means you need access to discarded elements (would need to keep them).
- "What if memory is limited?" → The heap uses O(k) memory. For top-10 out of a billion records, that's 10 elements.
- "Can you use this for percentiles?" → Yes. For the 99th percentile of n elements, maintain a min-heap of size ceil(0.01 * n). But the size grows with n, so the two-heap approach (problem 295) is better for streaming percentiles.

**What the interviewer evaluates:** Understanding that a min-heap (not max-heap) of size k gives the kth largest is the core insight. Many candidates reach for a max-heap and process k elements, which is O(n log n). The min-heap approach is O(n log k). Explaining the streaming property (can handle infinite input in bounded memory) shows you think beyond batch processing.

---

## DE Application

This pattern shows up constantly in data engineering:
- "Show me the top 10 most expensive queries" from a stream of query logs
- "What are the top 5 products by revenue?" without sorting a 100M row table
- Monitoring: "Alert if a value enters the top-K for a metric"
- Any aggregation where you need top-N and the full dataset is too large to sort

In SQL, this is `ORDER BY metric DESC LIMIT K`. The heap approach is how you'd implement that efficiently in Python when processing data that doesn't fit in a database.

See: [Top-K Streaming](../de_scenarios/top_k_streaming.md)

## At Scale

A min-heap of size k processes an infinite stream using O(k) memory. For k=100, that's a few KB regardless of whether 1M or 1B elements flow through. This is the canonical streaming top-k structure. In production, this powers real-time leaderboards, "trending now" features and anomaly detection thresholds. Kafka Streams and Flink both use heap-based structures for their top-k operators. The key limitation: the heap gives you the kth largest, but not the exact rank of arbitrary elements. For that, you need an order-statistic tree or approximate rank structures.

---

## Related Problems

- [215. Kth Largest Element in an Array](215_kth_largest_array.md) - Same concept but one-shot (not streaming)
- [347. Top K Frequent Elements](../../01_hash_map/problems/347_top_k_frequent.md) - Hash map for counting + heap or bucket sort for selection
- [295. Find Median from Data Stream](295_find_median_stream.md) - Two-heap technique for streaming median
