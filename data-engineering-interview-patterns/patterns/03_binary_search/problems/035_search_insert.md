# Search Insert Position (LeetCode #35)

🔗 [LeetCode 35: Search Insert Position](https://leetcode.com/problems/search-insert-position/)

> **Difficulty:** Easy | **Interview Frequency:** Occasional

## Problem Statement

Given a sorted array of distinct integers and a target, return the index if found. If not, return the index where it would be inserted to maintain sorted order.

You must write an algorithm with O(log n) runtime.

**Example:**
```
Input: nums = [1, 3, 5, 6], target = 5
Output: 2

Input: nums = [1, 3, 5, 6], target = 2
Output: 1
```

**Constraints:**
- 1 <= nums.length <= 10^4
- -10^4 <= nums[i] <= 10^4
- nums contains distinct values sorted in ascending order

---

## Thought Process

1. **This is "find the first element >= target"** - Whether the target exists or not, we want the position where it belongs.
2. **Left-boundary variant** - Unlike exact match, we don't return immediately when we find the target. We converge to the boundary.
3. **Key difference from #704** - The loop condition is `left < right` (not `<=`), and `right = mid` (not `mid - 1`). This lets us converge on the boundary without skipping it.
4. **`right` starts at `len(nums)`** - Because the insertion point could be after the last element.

---

## Worked Example

This is a boundary-finding problem. Instead of "is this value here?", we're asking "where should this value go?" If the target exists, return its index. If it doesn't, return the index where it would be inserted to keep the array sorted. This is exactly what Python's `bisect_left` does.

The key difference from exact-match binary search: when the search ends without finding the target, `left` naturally points to the correct insertion position. Elements before `left` are all smaller than the target, and elements from `left` onward are all larger or equal.

```
Input: nums = [1, 3, 5, 7, 9, 11], target = 6

  left=0, right=5, mid=2 → nums[2] = 5
  5 < 6 → left = 3

  left=3, right=5, mid=4 → nums[4] = 9
  9 > 6 → right = 3

  left=3, right=3, mid=3 → nums[3] = 7
  7 > 6 → right = 2

  left=3 > right=2 → not found.
  Return left = 3. Insert 6 at index 3: [1, 3, 5, 6, 7, 9, 11].

Target exists case: target = 7
  left=0, right=5, mid=2 → 5 < 7 → left=3
  left=3, right=5, mid=4 → 9 > 7 → right=3
  left=3, right=3, mid=3 → 7 == 7 → return 3.

Target at edges: target = 0
  left=0, right=5, mid=2 → 5 > 0 → right=1
  left=0, right=1, mid=0 → 1 > 0 → right=-1
  left=0 > right=-1 → return 0 (insert at the beginning).
```

---

## Approaches

### Approach: Left-Boundary Binary Search

<details>
<summary>💡 Hint</summary>

You don't need to handle "found" and "not found" separately. The insertion point IS the position of the first element >= target.

</details>

<details>
<summary>📝 Explanation</summary>

This is a standard binary search where the "not found" behavior returns the insertion point instead of -1. The algorithm is identical to exact match binary search, and the insertion point falls out naturally from the final value of `left`.

Here's why `left` is the correct insertion point: during the search, `left` moves right past elements that are too small, and `right` moves left past elements that are too big. When the loop ends (`left > right`), `left` points to the first element that is greater than or equal to the target. That's exactly where the target should be inserted.

This is equivalent to Python's `bisect.bisect_left(nums, target)`.

**Time:** O(log n) - same as exact match binary search.
**Space:** O(1).

This is the foundation for many boundary-finding problems. Once you understand that `left` converges to the first position where `nums[left] >= target`, you can adapt this template to find any kind of boundary.

</details>

<details>
<summary>💻 Code</summary>

```python
def search_insert(nums: list[int], target: int) -> int:
    left, right = 0, len(nums)
    while left < right:
        mid = (left + right) // 2
        if nums[mid] < target:
            left = mid + 1
        else:
            right = mid
    return left
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Found | `[1,3,5,6], 5` | `2` | Target exists |
| Insert middle | `[1,3,5,6], 2` | `1` | Between elements |
| Insert end | `[1,3,5,6], 7` | `4` | After all elements |
| Insert beginning | `[1,3,5,6], 0` | `0` | Before all elements |
| Single found | `[1], 1` | `0` | Minimum input |
| Single insert after | `[1], 2` | `1` | Right boundary = len |

---

## Common Pitfalls

1. **Using `right = len(nums) - 1`** - Misses the case where target belongs at the end. The insertion point can be at index `len(nums)`.
2. **Using `left <= right` loop** - Causes infinite loop with `right = mid`. The boundary variants need `left < right`.
3. **Confusing with exact match** - The exact match variant (#704) returns immediately on finding target and uses `mid ± 1` for both bounds. The boundary variant converges and uses `right = mid`.

---

## Interview Tips

**What to say:**
> "This is a left-boundary binary search - I need the first position where the value is >= target. I'll use left < right as my loop condition and right = mid instead of mid - 1, since mid could be the answer."

**Articulating the difference from #704 is key.** If you can explain why the loop condition and update rules differ between exact match and boundary search, you demonstrate understanding rather than memorization.

**This is `bisect.bisect_left()` under the hood.** Mentioning this shows you know the standard library. In production, use bisect. In interviews, implement from scratch.

**What the interviewer evaluates:** Understanding what the left pointer represents after binary search terminates (the insertion point) shows you understand the algorithm, not just the template. This is often a warm-up - the interviewer expects fast, clean execution and will escalate.

---

## DE Application

The insertion point / left boundary pattern shows up when:
- Finding where a timestamp falls in a sorted time-series index
- Determining which partition a value belongs to based on boundary ranges
- Implementing range queries on sorted data ("find all events after timestamp X")
- Any situation where you need "the first thing >= my value" in sorted data

This is arguably the most useful binary search variant for data engineering work.

---

## At Scale

Finding the insertion position is how B-tree inserts work internally: binary search to the leaf node, insert there. For 1B elements, this takes 30 comparisons. The cost of actually inserting (shifting elements in an array) is O(n), which is why production systems use trees (O(log n) insert) instead of sorted arrays. In data pipelines, "find where this row belongs in the sorted output" is the partitioning step of a sort-merge operation. Range-partitioned tables use this to route rows to the correct partition.

---

## Related Problems

- [704. Binary Search](704_binary_search.md) - Exact match variant
- [74. Search a 2D Matrix](074_search_2d_matrix.md) - Applies the same logic to 2D data
- [875. Koko Eating Bananas](875_koko_bananas.md) - Search on answer uses the same convergence logic
