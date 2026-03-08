# Binary Search (LeetCode #704)

🔗 [LeetCode 704: Binary Search](https://leetcode.com/problems/binary-search/)

> **Difficulty:** Easy | **Interview Frequency:** Very Common

## Problem Statement

Given a sorted array of distinct integers and a target, return the index of target. If not found, return -1.

You must write an algorithm with O(log n) runtime.

**Example:**
```
Input: nums = [-1, 0, 3, 5, 9, 12], target = 9
Output: 4
```

**Constraints:**
- 1 <= nums.length <= 10^4
- -10^4 < nums[i], target < 10^4
- All integers in nums are unique
- nums is sorted in ascending order

---

## Thought Process

1. **This is the textbook binary search problem.** Sorted array, distinct elements, find one target. No tricks.
2. **Define the search space** - left and right pointers bracket where the target could be.
3. **Each step halves the space** - Compare the midpoint to the target. If mid is too small, the answer is in the right half. If too large, the left half.
4. **Termination** - Either we find the target, or left crosses right (search space is empty).

---

## Worked Example

The classic case: find an exact value in a sorted array. We maintain a search range [left, right] and check the middle element. If it matches, we're done. If the target is larger, the answer must be in the right half (everything to the left of mid is smaller, so we can discard it). If smaller, the answer is in the left half. Each step cuts the range in half.

```
Input: nums = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91], target = 23

  left=0, right=9, mid=4 → nums[4] = 16
  16 < 23 → target is in right half. left = 5.
  Eliminated: [2, 5, 8, 12, 16]

  left=5, right=9, mid=7 → nums[7] = 56
  56 > 23 → target is in left half. right = 6.
  Eliminated: [56, 72, 91]

  left=5, right=6, mid=5 → nums[5] = 23
  23 == 23 → found it. Return index 5.

3 steps to find the value in a 10-element array. Linear search would
have taken 6 steps (checking indices 0 through 5).

Not-found case: target = 20
  left=0, right=9, mid=4 → 16 < 20 → left=5
  left=5, right=9, mid=7 → 56 > 20 → right=6
  left=5, right=6, mid=5 → 23 > 20 → right=4
  left=5 > right=4 → search space empty. Return -1.
```

---

## Approaches

### Approach: Exact Match Binary Search

<details>
<summary>💡 Hint</summary>

Start with the full array. Check the middle element. Which half can you eliminate?

</details>

<details>
<summary>📝 Explanation</summary>

Maintain a search range defined by `left` and `right` pointers. At each step, compute `mid = (left + right) // 2` and compare `nums[mid]` to the target:

- If `nums[mid] == target`: return mid.
- If `nums[mid] < target`: the answer must be to the right (all elements before mid are even smaller). Set `left = mid + 1`.
- If `nums[mid] > target`: the answer must be to the left. Set `right = mid - 1`.

Continue until `left > right`, which means the search range is empty and the target doesn't exist. Return -1.

The `+1` and `-1` are critical. We've already checked `mid` and it's not the target, so we exclude it from the next range. Without the adjustment, the range wouldn't shrink and the loop would run forever.

**Time:** O(log n) - each step halves the search range. After k steps, the range is n / 2^k. When n / 2^k < 1, the search ends. Solving for k: k = log₂(n).
**Space:** O(1) - just three variables (left, right, mid).

This is the most fundamental algorithm in the pattern. Every other binary search variant builds on this structure.

</details>

<details>
<summary>💻 Code</summary>

```python
def binary_search(nums: list[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Found in middle | `[-1,0,3,5,9,12], 9` | `4` | Standard case |
| Not found | `[-1,0,3,5,9,12], 2` | `-1` | Target between elements |
| Single element found | `[5], 5` | `0` | Minimum array size |
| Single element not found | `[5], -5` | `-1` | Empty result on minimum input |
| First element | `[1,2,3,4,5], 1` | `0` | Left boundary |
| Last element | `[1,2,3,4,5], 5` | `4` | Right boundary |
| Two elements | `[1,3], 2` | `-1` | Convergence on small input |
| Empty array | `[], 1` | `-1` | No elements to search |

---

## Common Pitfalls

1. **`left < right` instead of `left <= right`** - Misses the case where left equals right (one element remaining). For exact match, use `<=`.
2. **`right = mid` instead of `right = mid - 1`** - Causes infinite loop when `mid == left`. For exact match, always move past mid.
3. **Integer overflow on `(left + right)`** - Not an issue in Python (arbitrary precision) but matters in Java/C++. Mention `left + (right - left) // 2` if interviewing in those languages.

---

## Interview Tips

**What to say:**
> "This is a standard binary search. I'll use left and right pointers with the loop condition left <= right. Each iteration I check the midpoint and eliminate half the search space."

**This is a warm-up problem.** Solve it quickly and correctly. The real test is whether you can extend it to harder variants (rotated arrays, search on answer).

**If the interviewer asks about Python's bisect module:**
> "I know bisect_left and bisect_right exist and I'd use them in production. For the interview, I'll implement it from scratch to show I understand the mechanics."

**What the interviewer evaluates:** Clean implementation of binary search (correct boundary handling, no off-by-one errors) is the baseline. The real test is whether you can extend the pattern: "now what if the array is rotated?" or "what if you're searching a function instead of an array?" Your comfort with the basic template determines how quickly you can handle variants.

---

## DE Application

Binary search on sorted data appears in data engineering when:
- Finding a specific record in a sorted log file
- Looking up a timestamp in time-series data
- Checking whether a value exists in a sorted partition
- Any indexed lookup in a B-tree is binary search under the hood

This is the foundation problem. Every other binary search variant builds on this exact structure.

---

## At Scale

Binary search on 1B sorted elements takes 30 comparisons. This is negligible. The real cost at scale is getting the data sorted in the first place (O(n log n)) and keeping it sorted as new data arrives (B-tree insert is O(log n) per element). In a database, the sorted data IS the index. Every primary key lookup, every range scan and every merge join relies on binary search internally. At 1T rows with a B-tree index of depth 4, a point lookup touches 4 disk pages. With 4KB pages cached in memory, this takes microseconds.

---

## Related Problems

- [35. Search Insert Position](035_search_insert.md) - Same problem but return where target would be inserted
- [33. Search in Rotated Sorted Array](033_search_rotated.md) - Binary search with a twist
- [167. Two Sum II](../../02_two_pointers/problems/167_two_sum_ii.md) - Sorted data, but two pointers is better for pairs
