# Find Median from Data Stream (LeetCode #295)

🔗 [LeetCode 295: Find Median from Data Stream](https://leetcode.com/problems/find-median-from-data-stream/)

> **Difficulty:** Hard | **Interview Frequency:** Common

## Problem Statement

Design a data structure that supports adding integers from a data stream and finding the median of all elements added so far.

The median is the middle value in an ordered list. If the list has an even number of elements, the median is the average of the two middle values.

**Example:**
```
addNum(1)    → median = 1.0
addNum(2)    → median = 1.5   (average of 1 and 2)
addNum(3)    → median = 2.0   (middle of [1, 2, 3])
```

**Constraints:**
- -10^5 <= num <= 10^5
- At most 5 * 10^4 calls to addNum and findMedian
- findMedian is called only after at least one addNum

---

## Thought Process

1. **Clarify** - We need running median, not final median. Each addNum should be efficient.
2. **Brute force** - Keep a sorted list. `bisect.insort` is O(n) per insert due to shifting elements. `findMedian` is O(1) by indexing.
3. **Key insight** - We don't need the full sorted order. We only need the middle element(s). If we split the data into a lower half and an upper half, the median is at the boundary.
4. **Two heaps** - A max-heap for the lower half gives us the largest of the small elements. A min-heap for the upper half gives us the smallest of the large elements. The median is at one or both tops.

---

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

---

## Approaches

### Approach 1: Sorted List with bisect (Brute Force)

<details>
<summary>📝 Explanation</summary>

Maintain a list. On each `addNum`, append the value. On `findMedian`, sort the list and return the middle element(s).

**Time:** O(n log n) per findMedian call. O(1) per addNum.
**Space:** O(n).

Simple but expensive if findMedian is called frequently. Fine for sparse median queries on small streams.

</details>

<details>
<summary>💻 Code</summary>

```python
from bisect import insort

class MedianFinderSort:
    def __init__(self):
        self.sorted_list = []

    def add_num(self, num):
        insort(self.sorted_list, num)

    def find_median(self):
        n = len(self.sorted_list)
        if n % 2 == 1:
            return float(self.sorted_list[n // 2])
        return (self.sorted_list[n // 2 - 1] + self.sorted_list[n // 2]) / 2.0
```

</details>

---

### Approach 2: Two Heaps (Optimal)

<details>
<summary>💡 Hint 1</summary>

Split the numbers into a lower half and upper half. The median is at the boundary between them.

</details>

<details>
<summary>💡 Hint 2</summary>

What data structure gives you the maximum of a set in O(1)? What about the minimum? Can you use both?

</details>

<details>
<summary>📝 Explanation</summary>

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

</details>

<details>
<summary>💻 Code</summary>

```python
import heapq

class MedianFinder:
    def __init__(self):
        self.low = []   # max-heap (negated)
        self.high = []  # min-heap

    def add_num(self, num):
        heapq.heappush(self.low, -num)
        heapq.heappush(self.high, -heapq.heappop(self.low))
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))

    def find_median(self):
        if len(self.low) > len(self.high):
            return float(-self.low[0])
        return (-self.low[0] + self.high[0]) / 2.0
```

</details>

---

## Edge Cases

| Case | Stream | Expected Median | Why It Matters |
|------|--------|-----------------|----------------|
| Single element | `[5]` | `5.0` | Odd count, one heap |
| Two elements | `[1, 2]` | `1.5` | Even count, average |
| All same | `[5, 5, 5]` | `5.0` | Duplicates across heaps |
| Negatives | `[-1, -2, -3]` | `-2.0` | Negation of negatives |
| Large range | `[10000, -10000]` | `0.0` | Extreme values |
| Decreasing | `[5, 4, 3, 2, 1]` | `3.0` | Ordering doesn't matter |

---

## Common Pitfalls

1. **Negation confusion** - The max-heap stores negated values. When reading the top, negate again: `-self.low[0]` is the actual maximum of the lower half. Getting this wrong is the #1 bug.
2. **Wrong rebalancing** - The invariant is `len(low) >= len(high)` with at most 1 difference. If you allow high to be larger, findMedian breaks.
3. **Integer vs float median** - When the count is even, the median is the average of two integers. Return a float, not an integer.

---

## Interview Tips

**What to say:**
> "I'll split the stream into a lower half and upper half using two heaps. The max-heap tracks the lower half so I can see its largest element. The min-heap tracks the upper half so I can see its smallest element. The median is always at one or both tops."

**Common follow-ups:**
- "Can you extend this to find arbitrary percentiles?" → For the pth percentile, keep the lower heap at size ceil(p/100 * n). Same idea but the balance point shifts.
- "What about removing elements?" → You'd need a "lazy deletion" approach: mark elements as removed but don't pop them until they rise to the top. This is common in sliding window median problems.
- "What if you need the exact median of billions of records?" → Two heaps hold all elements in memory (O(n) space). For massive datasets, approximate methods like T-Digest or KLL sketch trade accuracy for bounded memory.

**What the interviewer evaluates:** The two-heap data structure is non-obvious and tests design creativity. Maintaining the balance invariant (size difference <= 1) at each insert is where bugs occur. The follow-up "what about distributed streams?" is a principal-level question. Mentioning t-digest or APPROX_QUANTILES shows production awareness.

---

## DE Application

The two-heap technique applies to:
- **Streaming percentiles:** P50, P95, P99 for latency monitoring (though production systems often use T-Digest for efficiency)
- **Real-time dashboards:** "What's the median order value in the last hour?"
- **Data quality checks:** Detecting when the median of a metric shifts significantly (anomaly detection)
- **SLA monitoring:** "Is our P50 latency below the SLA threshold?"

The key insight that transfers to production work: you don't need to sort everything to find the median. Two heaps give you O(log n) updates and O(1) queries. For exact streaming median in Python, this is the standard approach.

See: [Running Percentiles DE Scenario](../de_scenarios/running_percentiles.md)

## At Scale

Two heaps (max-heap for lower half, min-heap for upper half) give O(log n) insert and O(1) median. Memory is O(n) - every element is stored. For 1B elements, that's ~8GB. The streaming property is essential: you get the running median without sorting. At scale, exact median in a distributed setting is expensive: you need the element at position n/2 across all partitions, which requires a global sort or a multi-round selection algorithm. Approximate median is much cheaper: t-digest and GK-sketch provide epsilon-approximate quantiles in O(1/epsilon) memory. BigQuery's APPROX_QUANTILES and Spark's percentile_approx use these structures. In interviews, mentioning the exact vs approximate tradeoff for streaming median is a strong principal-level signal.

---

## Related Problems

- [703. Kth Largest Element in a Stream](703_kth_largest_stream.md) - Single heap for one percentile point
- [215. Kth Largest Element in an Array](215_kth_largest_array.md) - One-shot selection
- [480. Sliding Window Median](https://leetcode.com/problems/sliding-window-median/) - Two heaps + lazy deletion for a sliding window
