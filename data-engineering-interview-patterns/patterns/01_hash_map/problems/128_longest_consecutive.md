# Longest Consecutive Sequence (LeetCode #128)

🔗 [LeetCode 128: Longest Consecutive Sequence](https://leetcode.com/problems/longest-consecutive-sequence/)

> **Difficulty:** Medium | **Interview Frequency:** Common

## Problem Statement

Given an unsorted array of integers, find the length of the longest consecutive elements sequence.

Must run in O(n) time.

**Example:**
```
Input: nums = [100, 4, 200, 1, 3, 2]
Output: 4
Explanation: The longest consecutive sequence is [1, 2, 3, 4].
```

**Constraints:**
- 0 <= nums.length <= 10^5
- -10^9 <= nums[i] <= 10^9

---

## Thought Process

1. **The O(n) constraint is the challenge.** Sorting would give O(n log n), which is too slow.
2. **We need O(1) lookups** - Put everything in a set.
3. **Avoid redundant counting** - If we try to count the sequence starting from every element, we're back to O(n²) in the worst case.
4. **Key insight** - Only start counting from the beginning of a sequence. A number is a sequence start if `num - 1` is not in the set.
5. **Why it's still O(n)** - Each element is visited at most twice: once in the outer loop, once in a while loop expansion. Total work is proportional to n.

---

## Worked Example

We need to find the longest run of consecutive numbers (like 1, 2, 3, 4, 5) in an unsorted array. The sort-first approach works (O(n log n)) but we can do O(n) with a set.

The key insight: a consecutive sequence has a clear starting point - a number whose predecessor (number - 1) is NOT in the set. The number 3 in the sequence 1, 2, 3, 4, 5 is not a starting point because 2 exists. But 1 is a starting point because 0 doesn't exist. We only count forward from starting points, which prevents us from recounting elements that belong to the same sequence.

The set key is just the number itself. We use a set (not a dict) because we only need the "is this number in here?" check - no associated data needed.

```
Input: nums = [100, 4, 200, 1, 3, 2, 5]

Step 1 - Build a set for O(1) lookups:
  num_set = {100, 4, 200, 1, 3, 2, 5}

Step 2 - Find sequence starts and count forward:
  num=100: Is 99 in the set? No → 100 is a sequence START.
    Count forward: 101 in set? No. Length = 1.

  num=4: Is 3 in the set? Yes → 4 is NOT a start (it's in the
    middle of a sequence). Skip it. We'll count it when we
    process the actual start of its sequence.

  num=200: Is 199 in the set? No → 200 is a sequence START.
    Count forward: 201 in set? No. Length = 1.

  num=1: Is 0 in the set? No → 1 is a sequence START.
    Count forward:
      2 in set? Yes → keep going
      3 in set? Yes → keep going
      4 in set? Yes → keep going
      5 in set? Yes → keep going
      6 in set? No → stop. Length = 5.

  num=3: Is 2 in set? Yes → not a start, skip.
  num=2: Is 1 in set? Yes → not a start, skip.
  num=5: Is 4 in set? Yes → not a start, skip.

  Longest: 5 (the sequence 1, 2, 3, 4, 5)

Why is this O(n) and not O(n^2)? It looks like the "count forward"
inner loop could be expensive. But each element belongs to exactly
one sequence, and we only count from the start of each sequence. The
total work across ALL inner loops is at most n (we touch each element
at most once during counting). Combined with the outer scan (also n),
the total is O(n) + O(n) = O(n).
```

---

## Approaches

### Approach 1: Sorting

<details>
<summary>📝 Explanation</summary>

Sort the array, then scan for consecutive runs. After sorting, consecutive numbers are adjacent, so we walk through the sorted array tracking the current run length and the longest run we've found.

1. Sort the array.
2. Initialize `current_length = 1` and `max_length = 1`.
3. Walk through the sorted array from index 1:
   - If `nums[i] == nums[i-1] + 1`, extend the current run: `current_length += 1`.
   - If `nums[i] == nums[i-1]`, skip (duplicate, doesn't break or extend the run).
   - Otherwise, the run broke. Update `max_length` if needed, reset `current_length = 1`.
4. Return `max_length`.

The duplicate handling is the one subtlety. `[1, 2, 2, 3]` has a consecutive run of length 3 (1, 2, 3), not length 2. Duplicates don't break the sequence, they just don't contribute to it.

**Time:** O(n log n) - dominated by the sort. The scan is O(n).
**Space:** O(1) if sorting in-place, O(n) with `sorted()`.

This doesn't meet the O(n) requirement the problem asks for, but it's a solid first answer in an interview. State it, note the limitation, then optimize.

</details>

<details>
<summary>💻 Code</summary>

```python
def longest_consecutive_sort(nums: list[int]) -> int:
    if not nums:
        return 0
    nums_sorted = sorted(set(nums))
    longest = 1
    streak = 1
    for i in range(1, len(nums_sorted)):
        if nums_sorted[i] == nums_sorted[i - 1] + 1:
            streak += 1
            longest = max(longest, streak)
        else:
            streak = 1
    return longest
```

</details>

---

### Approach 2: Set with Sequence Start Detection (Optimal)

<details>
<summary>💡 Hint 1</summary>

Put all numbers in a set for O(1) lookups.

</details>

<details>
<summary>💡 Hint 2</summary>

Don't start counting from every number. Only start from the beginning of a sequence. How do you know if a number is the start?

</details>

<details>
<summary>📝 Explanation</summary>

The insight: we only need to count forward from the *start* of each sequence, not from every element. A number is a sequence start if its predecessor (number - 1) doesn't exist in the data. If the predecessor exists, this number is in the middle of some sequence and we'll count it when we process its sequence's start.

1. Put all numbers into a set for O(1) lookups.
2. For each number in the set:
   - Check if `num - 1` is in the set. If yes, this isn't a sequence start - skip it.
   - If `num - 1` is NOT in the set, this is a start. Count forward: check `num + 1`, `num + 2`, etc., incrementing a length counter as long as the next number exists in the set.
   - Update the max length if this sequence is longer than the previous best.
3. Return the max length.

The "skip if predecessor exists" check is what makes this O(n) instead of O(n²). Without it, every element would try to count forward, and overlapping sequences would be recounted. With it, each element is visited at most twice total: once in the outer loop (checking if it's a start) and at most once in an inner "count forward" loop (as part of exactly one sequence).

**Time:** O(n) - building the set is O(n). The outer loop iterates n times. The total work across *all* inner "count forward" loops is at most n (each element belongs to exactly one sequence). So total work is O(n) + O(n) = O(n).
**Space:** O(n) - the set stores all n elements.

This is a good problem to practice explaining the O(n) argument. The nested loop looks like O(n²) at first glance, and interviewers will often ask you to justify it. The answer is: the inner loop's iterations across all outer iterations are bounded by n total, not n per iteration.

</details>

<details>
<summary>💻 Code</summary>

```python
def longest_consecutive(nums: list[int]) -> int:
    if not nums:
        return 0
    num_set = set(nums)
    longest = 0
    for num in num_set:
        if num - 1 not in num_set:
            current = num
            streak = 1
            while current + 1 in num_set:
                current += 1
                streak += 1
            longest = max(longest, streak)
    return longest
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Standard | `[100, 4, 200, 1, 3, 2]` | `4` | Non-adjacent in array but consecutive in value |
| Long sequence | `[0, 3, 7, 2, 5, 8, 4, 6, 0, 1]` | `9` | Large sequence with duplicates |
| Empty | `[]` | `0` | Boundary |
| Single | `[1]` | `1` | Minimum sequence |
| No consecutive | `[10, 20, 30]` | `1` | Every element is its own sequence |
| With duplicates | `[1, 2, 0, 1]` | `3` | Duplicates shouldn't extend the count |
| Negative numbers | `[-3, -2, -1, 0, 1]` | `5` | Crosses zero |

---

## Common Pitfalls

1. **Not handling duplicates** - The set handles this naturally, but if you sort without deduplicating, you need to skip equal adjacent elements
2. **Starting sequence from every element** - Without the `num - 1` check, you'll do redundant work and risk O(n²)
3. **Iterating over the original array instead of the set** - If the array has duplicates, you'll process the same sequence start multiple times

---

## Interview Tips

**What to say:**
> "Sorting gives O(n log n). To hit O(n), I'll use a set for O(1) lookups. The trick is only starting sequences from their beginning - a number where num-1 isn't in the set. That way each element is processed at most twice total."

**The O(n) proof is a common follow-up.** Be ready to explain why the nested while loop doesn't make it O(n²). Walk through an example: in `[1, 2, 3, 100, 200]`, the while loop only runs for `num=1` (3 iterations). For 100 and 200, the while loop doesn't execute at all.

**What the interviewer evaluates at each stage:** The sorting approach tests basic problem-solving. The set approach tests whether you can design an O(n) algorithm with a non-obvious amortization argument. Explaining why the nested loop is still O(n) total tests your ability to reason about amortized complexity. At principal level, discussing how to distribute this across partitions (and the boundary-merging challenge) shows systems thinking.

---

## DE Application

Finding consecutive sequences appears in:
- Gap detection in time series data (missing dates, sequence breaks)
- Identifying contiguous partitions in a dataset
- Finding runs of consecutive IDs to detect batch boundaries

In SQL, this is the classic "gaps and islands" problem, typically solved with `ROW_NUMBER()` and grouping. The set-based approach here is the Python equivalent.

---

## At Scale

The hash set stores all n elements. For 10M integers, that's ~400MB. The algorithm itself is O(n) with excellent cache behavior (hash lookups are random access, but each element is processed at most twice). At 1B elements, the set doesn't fit in memory. Distributed approach: range-partition the data so consecutive numbers land on the same partition. Each partition finds local consecutive sequences, then merge sequences that span partition boundaries. This is trickier than it sounds - the boundary merging requires a second pass. In practice, sort-based approaches are often preferred at scale because they're easier to distribute and sort is a well-optimized primitive in every distributed framework.

---

## Related Problems

- [217. Contains Duplicate](217_contains_duplicate.md) - Same set-based existence checking
- [298. Binary Tree Longest Consecutive Sequence](https://leetcode.com/problems/binary-tree-longest-consecutive-sequence/) - Tree version of consecutive sequences
