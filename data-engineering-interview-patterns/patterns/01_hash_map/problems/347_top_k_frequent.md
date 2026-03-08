# Top K Frequent Elements (LeetCode #347)

🔗 [LeetCode 347: Top K Frequent Elements](https://leetcode.com/problems/top-k-frequent-elements/)

> **Difficulty:** Medium | **Interview Frequency:** Very Common

## Problem Statement

Given an integer array and an integer `k`, return the `k` most frequent elements. You may return the answer in any order.

**Example:**
```
Input: nums = [1,1,1,2,2,3], k = 2
Output: [1,2]
```

**Constraints:**
- 1 <= nums.length <= 10^5
- -10^4 <= nums[i] <= 10^4
- k is in the range [1, number of unique elements]
- The answer is guaranteed to be unique

---

## Thought Process

1. **Two-phase problem** - First count frequencies, then select the top k.
2. **Counting is O(n)** - Hash map or Counter handles this.
3. **Selection is the interesting part:**
   - Sort all frequencies: O(n log n)
   - Heap of size k: O(n log k)
   - Bucket sort by frequency: O(n)

---

## Worked Example

This is a two-step problem. Step 1: count how often each element appears (dict where key = number, value = count). Step 2: find the k elements with the highest counts. The counting step is always O(n). The selection step has two good options: a heap (O(n log k), pattern 05) or bucket sort (O(n)).

The bucket sort approach is clever: create an array where index i holds all elements that appeared exactly i times. Then walk backwards from the highest index, collecting elements until you have k. The maximum possible frequency is n (the length of the input), so the bucket array is bounded.

```
Input: nums = [4, 1, 1, 2, 4, 4, 3, 2, 1, 1], k = 2

Step 1 - Count frequencies (single pass with a dict):
  4 → {4:1}
  1 → {4:1, 1:1}
  1 → {4:1, 1:2}
  2 → {4:1, 1:2, 2:1}
  4 → {4:2, 1:2, 2:1}
  4 → {4:3, 1:2, 2:1}
  3 → {4:3, 1:2, 2:1, 3:1}
  2 → {4:3, 1:2, 2:2, 3:1}
  1 → {4:3, 1:3, 2:2, 3:1}
  1 → {4:3, 1:4, 2:2, 3:1}
  Final counts: {4: 3, 1: 4, 2: 2, 3: 1}

Step 2 - Find top k=2 using bucket sort:
  Max possible frequency = 10 (length of input)
  Create buckets (index = frequency, value = list of numbers):
    freq 1: [3]         (3 appeared once)
    freq 2: [2]         (2 appeared twice)
    freq 3: [4]         (4 appeared three times)
    freq 4: [1]         (1 appeared four times)
    freq 5-10: empty

  Walk from highest bucket down, collecting until we have k=2:
    freq 4 → collect [1]. Count: 1.
    freq 3 → collect [4]. Count: 2. Done.
  Result: [1, 4]

Both steps are O(n). The heap alternative for step 2 is O(n log k),
which matters when k is small relative to n (common in practice -
"find the top 10 out of millions").
```

---

## Approaches

### Approach 1: Counter + Sort

<details>
<summary>📝 Explanation</summary>

The most direct approach: count how often each element appears, then sort by frequency and take the top k.

1. Use `Counter(nums)` to build a frequency map: `{value: count}`.
2. Sort the items by count in descending order.
3. Take the first k elements.

Python's `Counter` has a built-in `most_common(k)` method that does steps 2 and 3 together. Under the hood it sorts all unique elements by frequency.

**Time:** O(n log n) in the worst case. Counting is O(n). Sorting the unique elements is O(u log u) where u is the number of unique values. In the worst case (all unique), u = n.
**Space:** O(n) - the Counter stores up to n unique values.

This is a fine starting point in an interview. State it, note the O(n log n), then say "we can avoid the full sort since we only need the top k, not the full sorted order."

</details>

<details>
<summary>💻 Code</summary>

```python
from collections import Counter

def top_k_frequent(nums: list[int], k: int) -> list[int]:
    counts = Counter(nums)
    return [num for num, _ in counts.most_common(k)]
```

</details>

---

### Approach 2: Heap

<details>
<summary>💡 Hint</summary>

You don't need to sort all elements. You only need the top k. A heap can do this more efficiently.

</details>

<details>
<summary>📝 Explanation</summary>

We don't need to sort *all* elements by frequency - we only need the top k. A min-heap of size k lets us find the top k elements without sorting everything.

1. Count frequencies: `Counter(nums)` → `{value: count}`.
2. Build a min-heap of size k. The heap stores `(count, value)` pairs. The smallest count is always at the top.
3. For each entry in the frequency map:
   - If the heap has fewer than k elements, push the entry.
   - If the current count is larger than the heap's minimum, pop the minimum and push the current entry. (This means the current element deserves to be in the top k more than whatever was at the bottom.)
   - If the current count is smaller or equal, skip it.
4. The heap now contains exactly the k most frequent elements.

Python's `heapq.nlargest(k, counts.keys(), key=counts.get)` does this in one call.

**Time:** O(n log k) - counting is O(n), and each of the u unique elements does at most one heap push/pop, each costing O(log k). Since k is usually much smaller than n, this is significantly better than O(n log n).
**Space:** O(n) for the counter + O(k) for the heap.

This approach shines when k is small relative to n. Finding the top 10 elements out of 10 million is O(n log 10) ≈ O(n) - essentially linear.

</details>

<details>
<summary>💻 Code</summary>

```python
import heapq
from collections import Counter

def top_k_frequent_heap(nums: list[int], k: int) -> list[int]:
    counts = Counter(nums)
    return heapq.nlargest(k, counts, key=counts.get)
```

</details>

---

### Approach 3: Bucket Sort (Optimal)

<details>
<summary>💡 Hint</summary>

The maximum possible frequency is n (the array length). That means frequency is bounded.

</details>

<details>
<summary>📝 Explanation</summary>

The key observation: the maximum possible frequency of any element is n (the length of the array). That means we can use frequency as an array index instead of sorting.

1. Count frequencies: `Counter(nums)`.
2. Create an array of n+1 empty lists (buckets), indexed 0 through n. Index i will hold all elements that appeared exactly i times.
3. For each element and its count, append the element to `buckets[count]`.
4. Walk the buckets array from the end (highest frequency) to the start, collecting elements until we have k.

For example, with `[1,1,1,2,2,3]` and k=2:
  - Counts: {1:3, 2:2, 3:1}
  - Buckets: index 1→[3], index 2→[2], index 3→[1]
  - Walk backwards: index 3 has [1], index 2 has [2]. Collected 2 elements. Done.

**Time:** O(n) - counting is O(n), building buckets is O(n) and walking buckets is O(n) in total. No sorting involved.
**Space:** O(n) - the bucket array has n+1 slots.

This is the optimal solution. The trade-off compared to the heap approach: it uses more memory (the full bucket array) but avoids the O(log k) heap operations. In practice, both are fast. The bucket sort approach is worth knowing because it demonstrates a general technique: when values are bounded by n, you can often avoid sorting entirely.

</details>

<details>
<summary>💻 Code</summary>

```python
from collections import Counter

def top_k_frequent_bucket(nums: list[int], k: int) -> list[int]:
    counts = Counter(nums)
    buckets: list[list[int]] = [[] for _ in range(len(nums) + 1)]
    for num, freq in counts.items():
        buckets[freq].append(num)

    result: list[int] = []
    for freq in range(len(buckets) - 1, 0, -1):
        for num in buckets[freq]:
            result.append(num)
            if len(result) == k:
                return result
    return result
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Standard | `[1,1,1,2,2,3], 2` | `[1,2]` | Happy path |
| Single element | `[1], 1` | `[1]` | Minimum input |
| All unique | `[1,2,3], 3` | `[1,2,3]` | k equals unique count |
| All same | `[5,5,5,5], 1` | `[5]` | One unique element |
| Ties | `[1,2,3,4], 2` | any 2 of them | Frequency ties are valid |

---

## Common Pitfalls

1. **Comparing by value instead of frequency** - The heap/sort key must be the count, not the element value
2. **Off-by-one in bucket sort** - Bucket indices go from 0 to n. Frequency 0 is unused (no element appears 0 times in the input).
3. **Not handling ties** - When multiple elements have the same frequency, any selection among them is valid

---

## Interview Tips

**What to say:**
> "This is a two-phase problem: count frequencies, then select top k. Counting is O(n) with a hash map. For selection, I can sort in O(n log n), use a heap for O(n log k) or bucket sort for O(n) since frequency is bounded by array length."

**The bucket sort insight is what separates good from great answers.** Most candidates stop at the heap approach. Mentioning bucket sort shows you think about the problem's structure, not just reaching for standard tools.

**Follow-up: "What if the data is streaming?"**
→ You can't use bucket sort (don't know the final array length). A min-heap of size k works well for streaming top-k. See the Heap pattern section.

**What the interviewer evaluates at each stage:** The sort approach tests whether you can decompose the problem into counting + selection. The heap approach tests whether you recognize that partial sorting (top-k) is cheaper than full sorting. The bucket sort insight tests whether you analyze the problem's constraints (frequency is bounded by n). At principal level, discussing approximate alternatives (Count-Min Sketch) for streaming data shows systems awareness.

---

## DE Application

Top-K is everywhere in data engineering:
- Most active users in the last hour
- Top error messages by frequency
- Heaviest tables by row count or storage
- Most common query patterns for optimization

At scale, exact top-k gets expensive. That's where approximate data structures like Count-Min Sketch come in (see probabilistic structures section). For most analytics use cases, approximate answers are fine.

---

## At Scale

The Counter stores one entry per unique element. For high-cardinality data (10M unique values), that's ~1GB. The heap holds only k elements - negligible. For very large datasets, this decomposes naturally: count frequencies per partition (map phase), merge frequency maps, then extract top-k (reduce phase). This is essentially what `GROUP BY value ORDER BY count DESC LIMIT k` does in SQL. Approximate alternatives: Count-Min Sketch (Pattern 11) for frequency estimation in fixed memory, or sampling. In Spark: `df.groupBy("value").count().orderBy(desc("count")).limit(k)`.

---

## Related Problems

- [692. Top K Frequent Words](https://leetcode.com/problems/top-k-frequent-words/) - Same pattern but with string sorting for ties
- [215. Kth Largest Element](https://leetcode.com/problems/kth-largest-element-in-an-array/) - Selection without the counting phase
- [451. Sort Characters By Frequency](https://leetcode.com/problems/sort-characters-by-frequency/) - Bucket sort on character frequencies
