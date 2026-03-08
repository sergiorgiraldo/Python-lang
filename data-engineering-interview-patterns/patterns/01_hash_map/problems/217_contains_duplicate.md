# Contains Duplicate (LeetCode #217)

🔗 [LeetCode 217: Contains Duplicate](https://leetcode.com/problems/contains-duplicate/)

> **Difficulty:** Easy | **Interview Frequency:** Very Common

## Problem Statement

Given an integer array, return `true` if any value appears at least twice and `false` if every element is distinct.

**Example:**
```
Input: nums = [1, 2, 3, 1]
Output: true

Input: nums = [1, 2, 3, 4]
Output: false
```

**Constraints:**
- 1 <= nums.length <= 10^5
- -10^9 <= nums[i] <= 10^9

---

## Thought Process

1. **Clarify** - Are we looking for any duplicate or a specific one? (Any.)
2. **Brute force** - Compare every pair. O(n²). Works but slow.
3. **Better with sorting** - Sort, then check adjacent elements. O(n log n).
4. **Best with a set** - Track what we've seen. O(n) time, O(n) space.

The trade-off here is time vs space. The set approach is fastest but uses the most memory.

---

## Worked Example

The question is simple: does any value appear more than once? A set gives us O(1) "have I seen this before?" checks. We scan through the array, and for each number, check if it's already in the set. If yes, duplicate found. If we get through the whole array with no hit, every value is unique.

We use a set (not a dict) because we don't need to store any data alongside each number - we only care about membership: "is it in there or not?"

```
Input: nums = [5, 3, 8, 1, 3, 7, 2]

  num=5  seen={}              Is 5 in seen? No → add. seen={5}
  num=3  seen={5}             Is 3 in seen? No → add. seen={5, 3}
  num=8  seen={5, 3}          Is 8 in seen? No → add. seen={5, 3, 8}
  num=1  seen={5, 3, 8}       Is 1 in seen? No → add. seen={5, 3, 8, 1}
  num=3  seen={5, 3, 8, 1}    Is 3 in seen? YES → return True

  Stopped at index 4 out of 7 elements. The duplicate was found
  before we even looked at the last two values.

No-duplicate case: nums = [5, 3, 8, 1, 7, 2]
  Scan all 6 elements. None found in the set. Return False.
  Total work: 6 set checks + 6 set adds = 12 O(1) operations.

There's also a one-liner approach: compare len(nums) to len(set(nums)).
If they differ, there's a duplicate. That builds the full set either way
(no early exit), but it's simple and readable for production code.
```

---

## Approaches

### Approach 1: Set Length Comparison

<details>
<summary>💡 Hint</summary>

If there are duplicates, a set of the array will be smaller than the array itself.

</details>

<details>
<summary>📝 Explanation</summary>

The simplest possible approach: convert the array to a set and compare lengths. A set automatically removes duplicates, so if the set is smaller than the original array, at least one value appeared more than once.

```python
return len(nums) != len(set(nums))
```

That's the entire implementation. Python builds the set by hashing every element and discarding duplicates.

**Time:** O(n) - building the set iterates through all n elements.
**Space:** O(n) - the set stores up to n unique values.

The downside: this always processes the entire array, even if the very first two elements are identical. There's no way to bail out early. For the average case where duplicates exist and appear early, the early-exit approach below is faster in practice.

</details>

<details>
<summary>💻 Code</summary>

```python
def contains_duplicate(nums: list[int]) -> bool:
    return len(nums) != len(set(nums))
```

</details>

---

### Approach 2: Early-Exit Set

<details>
<summary>📝 Explanation</summary>

Build the set one element at a time instead of all at once. Before adding each number, check if it's already in the set. If it is, we found a duplicate and can return immediately without looking at the rest of the array.

1. Create an empty set called `seen`.
2. For each number in the array:
   - Check: `num in seen`. If yes, return `True`.
   - Otherwise: `seen.add(num)`.
3. If we finish the loop without finding a duplicate, return `False`.

The `in` check on a set is O(1) (same hashing mechanism as a dict). So each element costs O(1) to check and O(1) to add.

**Time:** O(n) worst case (all unique, scan everything). But if a duplicate exists early in the array - say at index 5 out of a million elements - we stop after just 5 checks.
**Space:** O(n) worst case (all unique).

This is almost always better than the one-liner set approach in practice, because real data often has duplicates and they often appear well before the end.

</details>

<details>
<summary>💻 Code</summary>

```python
def contains_duplicate_set(nums: list[int]) -> bool:
    seen: set[int] = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False
```

</details>

---

### Approach 3: Sorting

<details>
<summary>📝 Explanation</summary>

Sort the array first. After sorting, any duplicates will be adjacent to each other. Then scan through the sorted array checking if any element equals the one right after it.

1. Sort the array (or a copy of it).
2. Walk through indices 0 to n-2. If `nums[i] == nums[i+1]`, return `True`.
3. If no adjacent pair matches, return `False`.

**Time:** O(n log n) - dominated by the sort. The scan afterwards is O(n).
**Space:** O(1) if you sort in-place (modifies the input), O(n) if you use `sorted()` to create a copy.

This is slower than the set approach (O(n log n) vs O(n)) but uses less space if you can sort in-place. In practice, the set approach is preferred unless the interviewer specifically says "you can't use extra space."

</details>

<details>
<summary>💻 Code</summary>

```python
def contains_duplicate_sort(nums: list[int]) -> bool:
    nums_sorted = sorted(nums)
    for i in range(1, len(nums_sorted)):
        if nums_sorted[i] == nums_sorted[i - 1]:
            return True
    return False
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Has duplicates | `[1, 2, 3, 1]` | `true` | Basic case |
| All unique | `[1, 2, 3, 4]` | `false` | No false positives |
| Empty array | `[]` | `false` | Boundary condition |
| Single element | `[1]` | `false` | Can't have duplicates with one element |
| All same | `[1, 1, 1]` | `true` | Multiple duplicates |
| Negatives | `[-1, -2, -1]` | `true` | Sign doesn't affect hashing |

---

## Common Pitfalls

1. **Forgetting empty/single-element cases** - Both should return `false`
2. **Using a list instead of a set for lookups** - `x in list` is O(n), `x in set` is O(1)
3. **Sorting the original array** - If you need to preserve input, use `sorted()` not `.sort()`

---

## Interview Tips

**What to say:**
> "The simplest approach is comparing set length to array length. If they differ, there's a duplicate. For early termination, I can build the set incrementally and stop as soon as I find one."

**Common follow-ups:**
- "What if memory is limited?" → Sorting approach uses O(1) extra space
- "What if the array is huge and mostly unique?" → Set approach is fine, memory scales with input
- "What about a Bloom filter?" → Good for approximate dedup at massive scale (see probabilistic structures section)

**What the interviewer evaluates at each stage:** The set-length comparison tests whether you know the simplest tool for the job. The early-exit set tests optimization awareness. Knowing when a simpler structure (set vs map) suffices shows you pick the right tool, not the fanciest one. Follow-up questions about memory or Bloom filters test whether you think beyond the LeetCode constraints.

---

## DE Application

Deduplication is one of the most common data engineering tasks:
- Checking for duplicate record IDs before loading
- Verifying primary key uniqueness after a transformation
- Detecting duplicate events in a streaming pipeline

At small scale, a set works. At large scale, you'd look at Bloom filters (probabilistic, space-efficient) or database constraints (guaranteed, but slower).

See: [Deduplication in Streaming](../de_scenarios/deduplication_streaming.md)

---

## At Scale

The hash set approach stores every unique element. For 10M integers, that's ~400MB. For data with high cardinality (many unique values), memory grows linearly. If you only need to know WHETHER duplicates exist (not WHICH ones), a Bloom filter (Pattern 11) gives a probabilistic answer in fixed memory. For exact dedup at scale, sort the data externally and check adjacent elements - O(n log n) time but O(1) memory beyond the sort buffer. In production pipelines, dedup is often done with a GROUP BY in SQL rather than in-memory sets.

---

## Related Problems

- [1. Two Sum](001_two_sum.md) - Uses a hash map for complement lookup instead of just existence
- [128. Longest Consecutive Sequence](128_longest_consecutive.md) - Uses a set for O(1) neighbor checks
- [219. Contains Duplicate II](https://leetcode.com/problems/contains-duplicate-ii/) - Adds a distance constraint (sliding window variant)
