# Two Sum II - Input Array Is Sorted (LeetCode #167)

🔗 [LeetCode 167: Two Sum II - Input Array Is Sorted](https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

## Problem Statement

Given a **1-indexed** sorted array, find two numbers that add up to target. Return their 1-indexed positions.

Exactly one solution is guaranteed. You can't use the same element twice.

**Example:**
```
Input: numbers = [2, 7, 11, 15], target = 9
Output: [1, 2]
```

**Constraints:**
- 2 <= numbers.length <= 3 * 10^4
- -1000 <= numbers[i] <= 1000
- numbers is sorted in non-decreasing order
- Exactly one solution exists

---

## Thought Process

1. **This is Two Sum but sorted** - We could use a hash map in O(n) time and O(n) space (same as LeetCode 1). But the sorted property lets us do better on space.
2. **Opposite ends** - Left pointer at start, right pointer at end. The sum of the smallest and largest gives us a starting point.
3. **Adjusting** - If the sum is too small, moving left pointer right increases it (sorted). If too large, moving right pointer left decreases it.
4. **Convergence** - Since exactly one solution exists and the array is sorted, the pointers will converge on it.

---

## Worked Example

With sorted input, start one pointer at the smallest value and one at the largest. Their sum tells us which pointer to move: too big means the right value is too large (move right left), too small means the left value is too small (move left right). Each step eliminates one position because sorted order guarantees the eliminated value can't be part of any valid pair.

```
Input: numbers = [2, 4, 5, 7, 9, 11, 14], target = 11

  left=0 (2), right=6 (14): 2+14=16 > 11
    Too big. Even the smallest left (2) makes 16 with 14.
    Every other left value would be bigger. Eliminate 14. Move right←.

  left=0 (2), right=5 (11): 2+11=13 > 11
    Still too big. Same logic. Eliminate 11. Move right←.

  left=0 (2), right=4 (9): 2+9=11 = target → found. Return [1, 5] (1-indexed).

  3 comparisons. Brute force: up to 21 pairs.
```

---

## Approaches

### Approach 1: Hash Map (From Two Sum)

<details>
<summary>📝 Explanation</summary>

Same approach as LeetCode 1 (Two Sum). Build a dict mapping each number to its index. For each number, check if `target - number` exists in the dict.

This solves the problem correctly in O(n) time but uses O(n) extra space for the hash map. It treats the input as if it were unsorted.

**Time:** O(n). **Space:** O(n).

Works but ignores the sorted property entirely. It's like doing a full table scan when you have an index available. In an interview, mention this approach first, then explain how two pointers achieve the same time complexity with O(1) space by exploiting sorted order.

</details>

### Approach 2: Opposite-End Pointers (Optimal for sorted)

<details>
<summary>💡 Hint</summary>

Start at the extremes. What does the sum tell you about which direction to move?

</details>

<details>
<summary>📝 Explanation</summary>

Start at both ends of the sorted array. Compute the sum:
- Equals target → return indices.
- Too large → right value is too big. Move right left.
- Too small → left value is too small. Move left right.

Why moving works: if `left + right > target`, then pairing right with ANY value ≥ left produces an even bigger sum. So right can't be part of any valid pair. Eliminate it. Same logic for the "too small" case.

Each step eliminates one value. At most n steps until pointers meet.

**Time:** O(n) - one pass.
**Space:** O(1) - two index variables.

Same time as hash map but O(1) space. Optimal when input is sorted.

</details>

<details>
<summary>💻 Code</summary>

```python
def two_sum_ii(numbers: list[int], target: int) -> list[int]:
    left, right = 0, len(numbers) - 1
    while left < right:
        current = numbers[left] + numbers[right]
        if current == target:
            return [left + 1, right + 1]
        elif current < target:
            left += 1
        else:
            right -= 1
    return []
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Adjacent | `[2,7,11,15], 9` | `[1,2]` | Solution at the start |
| Non-adjacent | `[2,3,4], 6` | `[1,3]` | Pointers skip middle elements |
| Negatives | `[-1,0], -1` | `[1,2]` | Negative numbers work the same |
| Ends | `[1,10], 11` | `[1,2]` | First and last element |
| With duplicates | `[1,2,2,4], 4` | `[2,3]` | Duplicates in the array |

---

## Common Pitfalls

1. **0-indexed vs 1-indexed** - This problem uses 1-indexed output. Add 1 to both indices.
2. **Moving the wrong pointer** - If sum < target, move left right (not right left). Think "I need a bigger number."
3. **Using hash map reflexively** - Works but misses the point. Interviewers want to see you exploit the sorted property.

---

## Interview Tips

**What to say:**
> "Since the input is sorted, I can use two pointers from opposite ends instead of a hash map. Same O(n) time but O(1) space."

**This is the classic "sorted data → two pointers" demonstration.** Interviewers often use this as a bridge from Two Sum to test whether you adapt your approach based on input properties.

**Follow-up: "Why not binary search?"**
→ You could binary search for the complement of each element, giving O(n log n). Two pointers is better at O(n). But binary search is a valid mention that shows you're thinking about the sorted property.

**What the interviewer evaluates:** Can you exploit the sorted precondition? Reaching for a hash map on sorted data is a yellow flag - it means you're applying patterns mechanically rather than analyzing the input. The follow-up "what if it's not sorted?" tests whether you understand the tradeoff: sort first + O(1) memory vs hash map + O(n) memory.

---

## DE Application

The opposite-ends pattern on sorted data appears when:
- Finding matching records in two sorted datasets (sorted merge join)
- Range queries on sorted indexes (find all pairs within a distance)
- Partition boundary selection (find two boundaries that cover a target range)

The O(1) space is critical for out-of-core processing where data is too large for memory but is already sorted on disk.

---

## At Scale

Two pointers on sorted data uses O(1) memory vs O(n) for the hash map approach. For 1B sorted integers, the scan takes ~10 seconds and requires zero extra memory beyond the input. The sorted precondition is the key constraint: if the data arrives unsorted, you pay O(n log n) to sort it first. In a database context, if the column has an index (B-tree), the data is already sorted and the two-pointer scan is free. This is why indexed columns enable efficient range queries and pair-finding. An interviewer asking "what if the array is already sorted?" is testing whether you recognize that sorted data unlocks better algorithms.

---

## Related Problems

- [1. Two Sum](../../01_hash_map/problems/001_two_sum.md) - Unsorted version (hash map)
- [15. 3Sum](015_three_sum.md) - Extension to three numbers
- [11. Container With Most Water](011_container_water.md) - Same opposite-ends technique, different optimization
