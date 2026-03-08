# Kth Largest Element in an Array (LeetCode #215)

🔗 [LeetCode 215: Kth Largest Element in an Array](https://leetcode.com/problems/kth-largest-element-in-an-array/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

## Problem Statement

Given an integer array and an integer k, return the kth largest element. Note that it's the kth largest in sorted order, not the kth distinct element.

**Example:**
```
Input: nums = [3, 2, 1, 5, 6, 4], k = 2
Output: 5
Explanation: sorted descending = [6, 5, 4, 3, 2, 1], 2nd = 5
```

**Constraints:**
- 1 <= k <= nums.length <= 10^5
- -10^4 <= nums[i] <= 10^4

---

## Thought Process

1. **Clarify** - Are there duplicates? (Yes, and they count separately.) Is k always valid? (Yes, k <= n.)
2. **Brute force** - Sort descending, return index k-1. O(n log n). Simple.
3. **Better with heap** - We don't need full sorted order. A min-heap of size k gives us the kth largest in O(n log k).
4. **Theoretically optimal** - Quickselect finds the kth element in O(n) average time without sorting at all. But it's harder to implement correctly and has O(n^2) worst case.

---

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

---

## Approaches

### Approach 1: Sort (Brute Force)

<details>
<summary>📝 Explanation</summary>

Sort the array and return the element at index `n - k` (0-indexed). Simple and correct.

**Time:** O(n log n) - dominated by the sort.
**Space:** O(1) if sorting in-place, O(n) with `sorted()`.

Fine for a first answer. Then optimize with the heap or Quickselect approaches.

</details>

<details>
<summary>💻 Code</summary>

```python
def find_kth_largest_sort(nums: list[int], k: int) -> int:
    return sorted(nums, reverse=True)[k - 1]
```

</details>

---

### Approach 2: Min-Heap of Size K

<details>
<summary>💡 Hint</summary>

Same idea as problem 703 (streaming version) but applied to a fixed array.

</details>

<details>
<summary>📝 Explanation</summary>

Same approach as the Kth Largest in Stream problem: maintain a min-heap of size K. Process all elements through the gatekeeper. The heap's minimum at the end is the Kth largest.

**Time:** O(n log k) - each of the n elements does at most one heap push/pop (O(log k) each).
**Space:** O(k) - heap holds exactly k elements.

Better than sorting when k is much smaller than n. For k=10 and n=10 million: O(10M × log 10) ≈ O(10M × 3) vs O(10M × log 10M) ≈ O(10M × 23).

</details>

<details>
<summary>💻 Code</summary>

```python
import heapq

def find_kth_largest(nums: list[int], k: int) -> int:
    heap: list[int] = []
    for num in nums:
        if len(heap) < k:
            heapq.heappush(heap, num)
        elif num > heap[0]:
            heapq.heapreplace(heap, num)
    return heap[0]
```

</details>

---

### Approach 3: Quickselect (Optimal Average)

<details>
<summary>💡 Hint</summary>

You don't need the top k elements sorted. You just need the kth. Can you find it without sorting?

</details>

<details>
<summary>📝 Explanation</summary>

Quickselect is a partition-based algorithm (related to Quicksort) that finds the Kth element without fully sorting. It picks a pivot, partitions the array so elements smaller than the pivot are on the left and larger on the right, then recurses into whichever side contains the Kth position.

On average, each step halves the problem (like binary search on the array). But unlike binary search, it rearranges elements.

**Time:** O(n) average (each step does O(n) work on a halved partition). O(n²) worst case (bad pivot choices, rare with randomization).
**Space:** O(1) extra - in-place partitioning.

Quickselect is the theoretically optimal approach (O(n) average) but the worst case and implementation complexity make the heap approach more practical in interviews. Mention Quickselect to show you know it exists, but implement the heap unless the interviewer asks for it.

</details>

<details>
<summary>💻 Code</summary>

```python
import random

def find_kth_largest_quickselect(nums: list[int], k: int) -> int:
    target_idx = len(nums) - k

    def quickselect(left: int, right: int) -> int:
        if left == right:
            return nums[left]

        pivot_idx = random.randint(left, right)
        nums[pivot_idx], nums[right] = nums[right], nums[pivot_idx]
        pivot = nums[right]

        store = left
        for i in range(left, right):
            if nums[i] < pivot:
                nums[store], nums[i] = nums[i], nums[store]
                store += 1
        nums[store], nums[right] = nums[right], nums[store]

        if store == target_idx:
            return nums[store]
        elif store < target_idx:
            return quickselect(store + 1, right)
        else:
            return quickselect(left, store - 1)

    return quickselect(0, len(nums) - 1)
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| k=1 (max) | `[3, 2, 1, 5, 6, 4], 1` | `6` | Finding the maximum |
| k=n (min) | `[3, 2, 1, 5, 6, 4], 6` | `1` | Finding the minimum |
| All duplicates | `[3, 3, 3, 3], 2` | `3` | Duplicates count |
| Negatives | `[-1, -2, -3, -4], 2` | `-2` | Heap comparison still works |
| Single element | `[1], 1` | `1` | Trivial case |

---

## Common Pitfalls

1. **Off-by-one in quickselect** - The kth largest is the (n-k)th smallest (0-indexed). Getting this conversion wrong is the most common bug.
2. **Not using random pivot** - Without randomization, quickselect degrades to O(n^2) on sorted or nearly-sorted input.
3. **Choosing the wrong approach for the interview** - Quickselect is theoretically faster but harder to implement correctly. The heap approach is simpler, still efficient and easier to explain. Start with heap unless the interviewer specifically asks for O(n).

---

## Interview Tips

**What to say:**
> "There are three approaches. Sorting is O(n log n). A min-heap of size k gives O(n log k), which is better when k is small. Quickselect achieves O(n) average but is harder to implement. I'll go with the heap approach for clarity, then we can discuss quickselect if there's time."

**Common follow-ups:**
- "Can you do better than O(n log k)?" → Quickselect is O(n) average. The `introselect` variant is O(n) worst case (Python's `statistics.median` uses it internally).
- "What if the array is too large to fit in memory?" → Stream through it with a heap of size k. Only k elements in memory at any time.
- "How does this relate to percentiles?" → The median is the n/2-th largest. The 99th percentile is the ceil(0.01*n)-th largest. Same algorithm, different k.

**What the interviewer evaluates:** This tests whether you know multiple selection algorithms. Quickselect (O(n) average) vs heap (O(n log k)) vs full sort (O(n log n)). Discussing the time-space-predictability tradeoff shows mature engineering judgment. The follow-up "what about distributed data?" tests system design thinking.

---

## DE Application

The selection problem comes up in data engineering for:
- Computing percentiles without sorting the full dataset
- Approximate quantile estimation in streaming systems (see T-Digest, KLL sketch)
- "Top N" queries implemented in Python when SQL isn't available
- Sampling the k most representative records from a large dataset

The heap approach is preferred in DE because it works on streams (don't need the full dataset in memory) and has predictable O(k) memory usage.

## At Scale

Quickselect is O(n) average but O(n^2) worst case. The heap approach is O(n log k) with no worst case. For n=1B and k=100, quickselect does ~1B comparisons, the heap does ~1B * 7 = 7B comparisons. Quickselect is faster in practice but has unpredictable performance. In distributed settings, finding the kth largest across partitions uses a multi-round approach: each partition finds local candidates, then merge and refine. Spark's `percentile_approx` uses t-digest (a probabilistic structure) for approximate quantiles on distributed data. For exact results, you need a distributed selection algorithm that narrows the candidate range across rounds.

---

## Related Problems

- [703. Kth Largest Element in a Stream](703_kth_largest_stream.md) - Streaming version of this problem
- [347. Top K Frequent Elements](../../01_hash_map/problems/347_top_k_frequent.md) - Count first, then select top K
- [295. Find Median from Data Stream](295_find_median_stream.md) - Streaming median using two heaps
