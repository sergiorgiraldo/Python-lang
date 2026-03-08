# Two Sum (LeetCode #1)

🔗 [LeetCode 1: Two Sum](https://leetcode.com/problems/two-sum/)

> **Difficulty:** Easy | **Interview Frequency:** Very Common

## Problem Statement

Given an array of integers and a target value, find two numbers that add up to the target. Return their indices.

Each input has exactly one solution and you can't use the same element twice.

**Example:**
```
Input: nums = [2, 7, 11, 15], target = 9
Output: [0, 1]
Explanation: nums[0] + nums[1] = 2 + 7 = 9
```

**Constraints:**
- 2 <= nums.length <= 10^4
- -10^9 <= nums[i] <= 10^9
- Exactly one valid answer exists

---

## Thought Process

How to approach this in an interview:

1. **Clarify** - Is there always exactly one solution? Can I use the same element twice? (No.)
2. **Edge cases** - Negative numbers? Zeros? Duplicate values?
3. **Brute force first** - Check every pair. O(n²). Works but slow.
4. **Spot the inefficiency** - For each number, we're scanning the entire array for its complement. That repeated scan is the bottleneck.
5. **Optimize** - A hash map gives O(1) lookups. Store what we've seen, check for the complement as we go.

---

## Worked Example

We need to find two numbers in the array that add up to the target. For any number we look at, we can calculate exactly what other number we'd need: `target - current_number`. That's the "complement." The question becomes: have we already seen the complement somewhere earlier in the array?

A dict answers that question in O(1). As we scan left to right, we store each number and its index in the dict. Before storing, we check if the complement is already there. If it is, we've found our pair. The dict key is the number itself and the value is the index where we saw it (because the problem asks us to return indices, not the numbers).

```
Input: nums = [8, 3, 11, 5, 9, 2, 7], target = 14

Brute force would check every pair:
  8+3=11, 8+11=19, 8+5=13, 8+9=17, 8+2=10, 8+7=15,
  3+11=14 ✓ (found after 7 comparisons)
  For 7 elements, up to 21 pairs to check. For 10,000 elements: ~50 million.

Hash map approach (single pass, checking for complements):
  i=0: num=8   complement=14-8=6
       seen={}
       Is 6 in seen? No. Store 8 and its index. seen={8: 0}

  i=1: num=3   complement=14-3=11
       seen={8: 0}
       Is 11 in seen? No. Store 3. seen={8: 0, 3: 1}

  i=2: num=11  complement=14-11=3
       seen={8: 0, 3: 1}
       Is 3 in seen? YES, at index 1.
       The pair is nums[1] + nums[2] = 3 + 11 = 14. Return [1, 2].

  3 dict lookups, each O(1). Done.

Why not just use two nested loops? They'd work, but each inner loop scans
the rest of the array - that's the repeated work. The dict eliminates that
by remembering every number we've already passed. Instead of asking "let me
scan everything to find 3," we ask "is 3 in my dict?" and get the answer
instantly.
```

---

## Approaches

### Approach 1: Brute Force

<details>
<summary>💡 Hint</summary>

Check every pair of numbers. Two nested loops.

</details>

<details>
<summary>📝 Explanation</summary>

The most direct approach: try every possible pair of numbers and check if they add up to the target. Use two nested loops - the outer loop picks the first number, the inner loop checks every number after it.

For each element at index `i`, you scan every element at index `j > i` and test whether `nums[i] + nums[j] == target`. If yes, return `[i, j]`.

This works correctly but it's slow. The outer loop runs n times, and for each iteration, the inner loop runs up to n-1 times. That's roughly n × n / 2 comparisons total.

**Time:** O(n²) - two nested loops. For n = 10,000 that's up to ~50 million comparisons.
**Space:** O(1) - no extra data structures.

This is a fine starting point in an interview. State it, acknowledge it's O(n²) and then say "I think we can do better with a hash map" to show you recognize the inefficiency.

</details>

<details>
<summary>💻 Code</summary>

```python
def two_sum_brute(nums: list[int], target: int) -> list[int]:
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
```

</details>

---

### Approach 2: Hash Map (Optimal)

<details>
<summary>💡 Hint 1</summary>

For each number, you know exactly what value you're looking for: `target - num`.

</details>

<details>
<summary>💡 Hint 2</summary>

What data structure lets you check "have I seen this value before?" in O(1)?

</details>

<details>
<summary>📝 Explanation</summary>

Instead of checking every pair, we can flip the question. For each number, we know exactly what we're looking for: `target - num` (the "complement"). The problem reduces to: "have I already seen the complement earlier in the array?"

A dict answers that question in O(1). Here's the process:

1. Create an empty dict called `seen`. It will map each number to the index where we found it.
2. Walk through the array left to right. For each number at index `i`:
   - Calculate the complement: `complement = target - nums[i]`
   - Check if `complement` is a key in `seen`. If yes, we found our pair: return `[seen[complement], i]`.
   - If not, store the current number: `seen[nums[i]] = i`.

The dict key is the number itself. The dict value is its index (because the problem asks us to return indices, not values).

Why does this work? By the time we reach index `i`, every number from index 0 through i-1 is in the dict. So when we check "is the complement in `seen`?", we're effectively checking every earlier number in O(1) instead of scanning through them in O(n). That single change turns the whole algorithm from O(n²) to O(n).

**Time:** O(n) - one pass through the array. Each dict lookup and insertion is O(1).
**Space:** O(n) - the dict stores up to n entries.

One subtlety: we check for the complement *before* storing the current number. This ensures we don't match a number with itself (which the problem forbids).

</details>

<details>
<summary>💻 Code</summary>

```python
def two_sum(nums: list[int], target: int) -> list[int]:
    seen: dict[int, int] = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Basic | `[2, 7, 11, 15], 9` | `[0, 1]` | Happy path |
| Negative numbers | `[-1, -2, -3, -4], -6` | `[1, 3]` | Sign handling |
| Zero in array | `[0, 4, 3, 0], 0` | `[0, 3]` | Zero is a valid value |
| Duplicate values | `[3, 3], 6` | `[0, 1]` | Same value, different indices |
| Solution at end | `[1, 2, 3, 4], 7` | `[2, 3]` | Don't stop too early |

---

## Common Pitfalls

1. **Using the same element twice** - The problem says you can't. Check complement before adding current number to the map.
2. **Returning values instead of indices** - Read carefully. This problem asks for indices.
3. **Adding to map before checking** - If you add `nums[i]` to the map before checking for its complement, you might match an element with itself when target = 2 * nums[i].

---

## Interview Tips

**What to say when you see this:**
> "This is a complement problem. For each number, I know what I'm looking for: target minus that number. Brute force checks every pair in O(n²), but a hash map lets me do each lookup in O(1) for O(n) overall."

**Common follow-ups:**
- "What if there are multiple valid pairs?" → Collect all pairs in a list instead of returning early
- "What if you need three numbers?" → Different approach entirely (see 3Sum - sorted array + two pointers)
- "Can you do it without extra space?" → Not in O(n). You'd need O(n²) brute force or O(n log n) with sorting + two pointers

**How to handle hints:**
- "Think about what you're searching for repeatedly" → They want you to identify the complement and use a hash map
- "Can you do it in one pass?" → Confirms the hash map approach (build and query simultaneously)

**What the interviewer evaluates at each stage:** The brute force tests basic problem-solving ability. The hash map optimization tests pattern recognition - can you identify that O(1) lookup eliminates the inner loop? Follow-up questions about memory, scale or streaming test whether you think like an engineer or a puzzle solver. At principal level, volunteering the scale discussion before being asked is a strong signal.

---

## DE Application

This pattern shows up in data engineering when:
- Building lookup tables for enrichment (dimension table → hash map → O(1) lookups per event)
- Implementing join logic in Python when you can't use SQL
- Finding matching records across two datasets
- Deduplication checks against a known set of IDs

See: [Build Lookup Table](../de_scenarios/build_lookup_table.md)

---

## At Scale

The hash map approach uses O(n) memory. For 10M integer pairs, that's roughly 800MB - fits on one machine. For 1B pairs, it's ~80GB and you need a distributed approach: hash-partition both the array and the target complements by key, then each partition independently finds local pairs. In Spark, this is a self-join with a hash partitioner. Watch for skew: if many elements share the same complement, one partition does disproportionate work. An interviewer asking "what if the array doesn't fit in memory?" wants to hear you say "external hashing" or "partition and distribute."

---

## Related Problems

- [15. 3Sum](../../02_two_pointers/problems/015_three_sum.md) - Extension to three numbers, uses sorting + two pointers
- [167. Two Sum II](../../02_two_pointers/problems/167_two_sum_ii.md) - Sorted input, so two pointers works in O(1) space
- [560. Subarray Sum Equals K](560_subarray_sum_k.md) - Same complement idea applied to prefix sums
