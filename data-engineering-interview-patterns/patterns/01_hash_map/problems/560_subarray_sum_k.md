# Subarray Sum Equals K (LeetCode #560)

🔗 [LeetCode 560: Subarray Sum Equals K](https://leetcode.com/problems/subarray-sum-equals-k/)

> **Difficulty:** Medium | **Interview Frequency:** Common

## Problem Statement

Given an array of integers and an integer `k`, return the total number of contiguous subarrays whose sum equals `k`.

**Example:**
```
Input: nums = [1, 1, 1], k = 2
Output: 2
Explanation: [1,1] appears twice (indices 0-1 and 1-2)
```

**Constraints:**
- 1 <= nums.length <= 2 * 10^4
- -1000 <= nums[i] <= 1000
- -10^7 <= k <= 10^7

---

## Thought Process

1. **Brute force** - Check every subarray. O(n²) with running sums, O(n³) without.
2. **The prefix sum trick** - If `prefix[j] - prefix[i] = k`, then the subarray from `i+1` to `j` sums to k.
3. **This is Two Sum in disguise** - For each prefix sum, we're looking for a complement (`prefix_sum - k`). Store prefix sums in a hash map.
4. **Critical detail** - Initialize the map with `{0: 1}` because a prefix sum equal to k means the subarray from the start sums to k.

---

## Worked Example

This is the trickiest hash map problem in this section because the dict key is a *computed value* rather than something directly from the input.

The concept: a **prefix sum** at position i is the total of all elements from the start of the array through position i. If the prefix sum at position j minus the prefix sum at position i equals k, then the elements between positions i+1 and j sum to k. That's our subarray.

So the question at each position becomes: "is there an earlier position where the prefix sum was exactly `current_prefix_sum - k`?" A dict answers that in O(1). The key is the prefix sum value, and the value is how many times we've seen that prefix sum (because multiple earlier positions might have the same prefix sum, giving us multiple valid subarrays).

The dict starts with `{0: 1}` - a prefix sum of 0 has occurred once (before the array begins). This handles subarrays that start from index 0.

```
Input: nums = [1, 2, 1, 3, 1, 2], k = 3

  prefix=0, counts={0: 1}

  i=0, num=1: prefix = 0+1 = 1
    Need: prefix - k = 1 - 3 = -2
    Is -2 in counts? No (counts = {0:1}). No subarrays ending here sum to 3.
    Store: counts = {0:1, 1:1}

  i=1, num=2: prefix = 1+2 = 3
    Need: prefix - k = 3 - 3 = 0
    Is 0 in counts? YES, count = 1. Found 1 subarray ending here.
      That subarray is nums[0..1] = [1, 2]. Sum = 3. ✓
    Total so far: 1
    Store: counts = {0:1, 1:1, 3:1}

  i=2, num=1: prefix = 3+1 = 4
    Need: prefix - k = 4 - 3 = 1
    Is 1 in counts? YES, count = 1. Found 1 subarray ending here.
      That subarray is nums[1..2] = [2, 1]. Sum = 3. ✓
    Total so far: 2
    Store: counts = {0:1, 1:1, 3:1, 4:1}

  i=3, num=3: prefix = 4+3 = 7
    Need: prefix - k = 7 - 3 = 4
    Is 4 in counts? YES, count = 1. Found 1 subarray ending here.
      That subarray is nums[3..3] = [3]. Sum = 3. ✓
    Total so far: 3
    Store: counts = {0:1, 1:1, 3:1, 4:1, 7:1}

  i=4, num=1: prefix = 7+1 = 8
    Need: prefix - k = 8 - 3 = 5
    Is 5 in counts? No. No subarrays ending here sum to 3.
    Total so far: 3
    Store: counts = {0:1, 1:1, 3:1, 4:1, 7:1, 8:1}

  i=5, num=2: prefix = 8+2 = 10
    Need: prefix - k = 10 - 3 = 7
    Is 7 in counts? YES, count = 1. Found 1 subarray ending here.
      That subarray is nums[4..5] = [1, 2]. Sum = 3. ✓
    Total so far: 4
    Store: counts = {0:1, 1:1, 3:1, 4:1, 7:1, 8:1, 10:1}

  Answer: 4 subarrays sum to 3.

One pass, 6 dict lookups. The brute force alternative checks all 21
subarrays (every possible start/end pair). For an array of 10,000
elements, that's ~50 million subarrays vs 10,000 dict lookups.
```

---

## Approaches

### Approach 1: Brute Force

<details>
<summary>📝 Explanation</summary>

Check every possible subarray by trying every starting index and every ending index. For each pair (i, j), sum the elements from index i to j and check if the sum equals k.

1. For each starting index `i` from 0 to n-1:
   - Initialize a running sum = 0.
   - For each ending index `j` from `i` to n-1:
     - Add `nums[j]` to the running sum.
     - If running sum equals k, increment the count.
2. Return the count.

Using a running sum (adding one element at a time as `j` increases) avoids re-summing from scratch each time, but it's still O(n²) because of the two nested loops.

**Time:** O(n²) - two nested loops. Each subarray check is O(1) with the running sum optimization.
**Space:** O(1) - just the running sum and count variables.

This is simple and correct. In an interview, state it and its complexity, then say "I can do this in O(n) with prefix sums and a hash map."

</details>

<details>
<summary>💻 Code</summary>

```python
def subarray_sum_brute(nums: list[int], k: int) -> int:
    count = 0
    n = len(nums)
    for i in range(n):
        current_sum = 0
        for j in range(i, n):
            current_sum += nums[j]
            if current_sum == k:
                count += 1
    return count
```

</details>

---

### Approach 2: Prefix Sum + Hash Map (Optimal)

<details>
<summary>💡 Hint 1</summary>

If the sum from index 0 to j is `prefix[j]` and the sum from 0 to i is `prefix[i]`, then the sum from i+1 to j is `prefix[j] - prefix[i]`.

</details>

<details>
<summary>💡 Hint 2</summary>

For each j, you need to find how many previous prefix sums equal `prefix[j] - k`. This is the Two Sum complement pattern.

</details>

<details>
<summary>📝 Explanation</summary>

The core idea relies on **prefix sums**. A prefix sum at position j is the sum of all elements from index 0 through j. If we know the prefix sum at two positions i and j (where i < j), then the subarray sum from i+1 through j is `prefix[j] - prefix[i]`. We want that difference to equal k.

Rearranging: we need `prefix[i] = prefix[j] - k`. At each position j, we ask: "how many earlier positions had a prefix sum equal to `current_prefix - k`?" A dict counts exactly that.

Step by step:
1. Initialize `prefix_sum = 0` and a dict `counts = {0: 1}`. The `{0: 1}` seed means "a prefix sum of 0 has occurred once" (the empty prefix before the array starts). This lets us detect subarrays that start from index 0.
2. Walk through the array. At each index, add the current element to `prefix_sum`.
3. Check if `prefix_sum - k` exists as a key in `counts`. If yes, add `counts[prefix_sum - k]` to our result. Each occurrence represents a different earlier position where a subarray ending at the current index sums to k.
4. Add the current `prefix_sum` to `counts` (increment its count by 1).

Why the dict value is a count (not a single index): the same prefix sum can occur at multiple earlier positions. Each one represents a different valid subarray. For example, if prefix sums at indices 2, 5 and 8 are all 10, and the current prefix sum is 13 with k=3, then there are three subarrays ending at the current index that sum to 3.

**Time:** O(n) - one pass through the array. Each step does one dict lookup and one dict update, both O(1).
**Space:** O(n) - the dict stores up to n+1 distinct prefix sum values.

**Why `{0: 1}` matters:** without it, we'd miss subarrays starting from index 0. If the first three elements sum to k, the prefix sum at index 2 equals k. We need `prefix - k = 0` to be in the dict. Seeding `{0: 1}` ensures it is.

</details>

<details>
<summary>💻 Code</summary>

```python
from collections import defaultdict

def subarray_sum(nums: list[int], k: int) -> int:
    count = 0
    prefix_sum = 0
    seen: dict[int, int] = defaultdict(int)
    seen[0] = 1

    for num in nums:
        prefix_sum += num
        count += seen[prefix_sum - k]
        seen[prefix_sum] += 1

    return count
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Basic | `[1,1,1], 2` | `2` | Multiple overlapping subarrays |
| With negatives | `[1,-1,0], 0` | `3` | Negatives create more valid subarrays |
| Single match | `[5], 5` | `1` | Entire array is the subarray |
| All zeros | `[0,0,0], 0` | `6` | Every possible subarray matches |
| No match | `[1,2,3], 100` | `0` | No valid subarrays |
| Negative target | `[-1,-1,1], -2` | `1` | Target can be negative |

---

## Common Pitfalls

1. **Forgetting to initialize `{0: 1}`** - Without this, you miss subarrays starting at index 0
2. **Using sliding window instead** - Sliding window only works when all values are positive. This problem allows negatives, so prefix sums + hash map is required.
3. **Confusing "count of subarrays" with "find one subarray"** - We track counts in the hash map, not indices
4. **Order of operations** - Check the complement before adding the current prefix sum to the map (otherwise you'd count the empty subarray from an index to itself)

---

## Interview Tips

**What to say:**
> "This is the Two Sum pattern applied to prefix sums. For each position, I compute the running sum and check if I've seen a previous prefix sum that's exactly k less. The hash map tracks how many times each prefix sum has appeared."

**The `{0: 1}` initialization is a common interview question.** Be ready to explain it with a concrete example: if `nums = [3]` and `k = 3`, the prefix sum after index 0 is 3. We look for `3 - 3 = 0` in the map. Without `{0: 1}`, we'd miss this.

**Follow-up: "Why can't you use a sliding window?"**
→ Sliding window assumes adding elements increases the sum and removing them decreases it. With negative numbers, that assumption breaks. The prefix sum approach works regardless of sign.

**What the interviewer evaluates at each stage:** The brute force tests basic problem understanding. The prefix sum + hash map optimization tests whether you can see this as Two Sum in disguise - the deepest pattern recognition in this section. The `{0: 1}` initialization is a common interview trap that tests attention to detail. At principal level, discussing the streaming implications (unbounded hash map growth) shows production awareness.

---

## DE Application

Prefix sum patterns appear in data engineering when:
- Computing running totals over time windows (daily revenue, cumulative users)
- Finding date ranges where a metric exceeds a threshold
- Detecting periods of net zero change (sum = 0 subarrays)

In SQL, this maps to window functions: `SUM(val) OVER (ORDER BY ts ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)` gives prefix sums. Finding subarrays that sum to k is equivalent to a self-join on prefix sums.

---

## At Scale

The prefix sum hash map stores at most n entries (one per prefix sum). For 10M elements, that's ~800MB. This problem is inherently sequential - each prefix sum depends on all previous elements - so it doesn't parallelize trivially. For very large arrays, you can split into chunks: compute prefix sums within each chunk, then adjust cross-chunk sums at boundaries. In a streaming context, the hash map grows unboundedly (every new prefix sum is stored). If you only need recent subarrays, combine with a sliding window to bound memory.

---

## Related Problems

- [1. Two Sum](001_two_sum.md) - The same complement lookup pattern, applied to raw values instead of prefix sums
- [523. Continuous Subarray Sum](https://leetcode.com/problems/continuous-subarray-sum/) - Similar but checks divisibility by k
- [974. Subarray Sums Divisible by K](https://leetcode.com/problems/subarray-sums-divisible-by-k/) - Modular arithmetic variant
