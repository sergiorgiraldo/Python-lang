# Sort Colors - Dutch National Flag (LeetCode #75)

🔗 [LeetCode 75: Sort Colors - Dutch National Flag](https://leetcode.com/problems/sort-colors/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

## Problem Statement

Given an array with `n` objects colored red (0), white (1) and blue (2), sort them **in place** so that objects of the same color are adjacent, in order 0, 1, 2.

Cannot use the library's sort function.

**Example:**
```
Input: nums = [2, 0, 2, 1, 1, 0]
Output: [0, 0, 1, 1, 2, 2]
```

**Constraints:**
- n == nums.length
- 1 <= n <= 300
- nums[i] is 0, 1 or 2

---

## Thought Process

1. **Counting sort is the obvious approach** - Count 0s, 1s, 2s, then overwrite. Two passes, O(n) time.
2. **Can we do it in one pass?** - The Dutch National Flag algorithm uses three pointers to partition in a single scan.
3. **Three regions** - Maintain invariants: everything before `low` is 0, everything after `high` is 2, `mid` scans the unknown region.
4. **When mid finds a 0** - Swap it to the low region, advance both low and mid.
5. **When mid finds a 2** - Swap it to the high region, decrement high. Don't advance mid because the swapped element hasn't been examined yet.
6. **When mid finds a 1** - It's already in the right place, just advance mid.

---

## Worked Example

Dutch National Flag: three pointers partition the array into [0s | 1s | unprocessed | 2s]. `low` marks where the next 0 goes, `high` marks where the next 2 goes, `mid` scans the unprocessed region. When mid sees 0, swap with low. When mid sees 2, swap with high (but DON'T advance mid because the swapped-in value hasn't been inspected). When mid sees 1, just advance.

```
Input: nums = [2, 0, 1, 2, 1, 0, 2, 0]
  low=0, mid=0, high=7

  mid=0: val=2 → swap(0,7): [0,0,1,2,1,0,2,2]. high=6. Don't advance mid.
  mid=0: val=0 → swap(0,0): no change. low=1, mid=1.
  mid=1: val=0 → swap(1,1): no change. low=2, mid=2.
  mid=2: val=1 → already correct. mid=3.
  mid=3: val=2 → swap(3,6): [0,0,1,2,1,0,2,2]. high=5. Don't advance mid.
  mid=3: val=2 → swap(3,5): [0,0,1,0,1,2,2,2]. high=4. Don't advance mid.
  mid=3: val=0 → swap(2,3): [0,0,0,1,1,2,2,2]. low=3, mid=4.
  mid=4: val=1 → correct. mid=5.
  mid=5 > high=4 → done.

  Result: [0, 0, 0, 1, 1, 2, 2, 2]. One pass, O(1) space.
```

---

## Approaches

### Approach 1: Counting Sort (Two Pass)

<details>
<summary>📝 Explanation</summary>

Two passes. First pass: count how many 0s, 1s and 2s exist. Second pass: overwrite the array using those counts - fill in all the 0s first, then all 1s, then all 2s.

This works because there are only three distinct values. The three counters tell you exactly how many of each to write back.

**Time:** O(n) - two passes. **Space:** O(1) - three counters.

Simple and correct but touches every element twice regardless of how sorted the array already is. The Dutch National Flag approach does it in a single pass with swaps, preserving elements that are already in the right position.

</details>

<details>
<summary>💻 Code</summary>

```python
def sort_colors_counting(nums: list[int]) -> None:
    counts = [0, 0, 0]
    for num in nums:
        counts[num] += 1
    idx = 0
    for val in range(3):
        for _ in range(counts[val]):
            nums[idx] = val
            idx += 1
```

</details>

---

### Approach 2: Dutch National Flag (One Pass)

<details>
<summary>💡 Hint</summary>

Three pointers: `low` marks where the next 0 goes, `high` marks where the next 2 goes, `mid` scans from left to right. What happens at each step?

</details>

<details>
<summary>📝 Explanation</summary>

Three pointers: `low` (boundary of 0s), `mid` (scanner), `high` (boundary of 2s).

- `nums[mid] == 0`: swap with low, advance both low and mid. The swapped-in value from low is always 1 (already processed region), so it's safe to advance mid.
- `nums[mid] == 1`: correct region. Advance mid only.
- `nums[mid] == 2`: swap with high, decrement high. Do NOT advance mid because the swapped-in value hasn't been inspected.

Stop when mid > high.

**Time:** O(n) - each element inspected at most twice.
**Space:** O(1) - three pointers.

The "don't advance mid after high swap" is the most common bug and the most common interview follow-up.

</details>

<details>
<summary>💻 Code</summary>

```python
def sort_colors(nums: list[int]) -> None:
    low, mid, high = 0, 0, len(nums) - 1
    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1
            mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Basic | `[2,0,2,1,1,0]` | `[0,0,1,1,2,2]` | Standard case |
| Already sorted | `[0,0,1,1,2,2]` | `[0,0,1,1,2,2]` | No swaps needed |
| Reverse | `[2,2,1,1,0,0]` | `[0,0,1,1,2,2]` | Maximum swaps |
| All same | `[1,1,1]` | `[1,1,1]` | Mid advances through all |
| No middle value | `[2,0,2,0]` | `[0,0,2,2]` | Only low and high active |
| Single | `[0]` | `[0]` | Boundary |

---

## Common Pitfalls

1. **Advancing mid after swapping with high** - The element swapped from the high position hasn't been examined. If you advance mid, you'll miss it. This is the most common bug.
2. **Using `mid < high` instead of `mid <= high`** - Need `<=` because the element at `high` might still need to be examined.
3. **Not advancing mid after swapping with low** - Safe to advance because the element from low was already in the `[low, mid)` zone (it was a 1).

---

## Interview Tips

**What to say:**
> "I'll use the Dutch National Flag algorithm. Three pointers partition the array into four regions: 0s, 1s, unknown and 2s. The mid pointer scans through the unknown region, swapping elements to the correct partition."

**Name-dropping "Dutch National Flag" shows you know the classical algorithm.** It's attributed to Dijkstra. Mentioning the origin is a nice touch but not required.

**Follow-up: "What if there are K colors instead of 3?"**
→ For small K, you can extend to multiple pivots. For larger K, counting sort generalizes naturally in O(n + K).

**What the interviewer evaluates:** Single-pass with three pointers tests your ability to manage complex state. The partition invariant (everything left of low is 0, everything right of high is 2) must be maintained at every step. Mentioning quicksort's partition step connects this to a foundational algorithm.

---

## DE Application

Three-way partitioning shows up when:
- Separating data into categories (hot/warm/cold storage tiers)
- Routing records to different processing paths (valid/needs-review/invalid)
- Partitioning data quality results (pass/warn/fail)

The general principle - partition in one pass using swap pointers - is useful whenever you're categorizing data into a small number of buckets without extra memory.

---

## At Scale

Dutch National Flag uses O(1) memory and a single pass. It's a three-way partition: elements less than pivot, equal to pivot, greater than pivot. For 1B elements, this takes ~10 seconds. The partition operation is the core of quicksort and appears in distributed systems as the shuffle phase: partition data into buckets by key range. In Spark, `repartitionByRange` does a multi-way partition. The three-way variant is important when many elements equal the pivot (common with low-cardinality columns like status codes or country codes). Without three-way partitioning, quicksort degrades to O(n^2) on inputs with many duplicates.

---

## Related Problems

- [283. Move Zeroes](283_move_zeroes.md) - Two-way partition (simpler version)
- [324. Wiggle Sort II](https://leetcode.com/problems/wiggle-sort-ii/) - Uses Dutch National Flag as a building block
