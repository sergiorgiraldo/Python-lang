# Find Minimum in Rotated Sorted Array (LeetCode #153)

🔗 [LeetCode 153: Find Minimum in Rotated Sorted Array](https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

## Problem Statement

An array sorted in ascending order was rotated between 1 and n times. Given the rotated array with unique elements, find the minimum element.

You must write an algorithm that runs in O(log n) time.

**Example:**
```
Input: nums = [3, 4, 5, 1, 2]
Output: 1
Explanation: Original sorted array [1,2,3,4,5] was rotated 3 times.

Input: nums = [11, 13, 15, 17]
Output: 11
Explanation: Not rotated (or rotated n times).
```

**Constraints:**
- n == nums.length
- 1 <= n <= 5000
- -5000 <= nums[i] <= 5000
- All values are unique

---

## Thought Process

1. **Don't scan linearly** - That's O(n). The problem demands O(log n), which means binary search.
2. **What property can we binary search on?** In a rotated sorted array, one half is always properly sorted. The minimum is where the sorting "breaks."
3. **Compare mid to what?** There's no target here. Compare `nums[mid]` to `nums[right]`. If mid is larger than right, the break point (minimum) must be to the right. If mid is smaller or equal, mid might be the minimum, or the break is to the left.
4. **This is a convergence problem** - We don't return immediately when we "find" something. We narrow the window until left equals right.

---

## Worked Example

A rotated sorted array was originally sorted, then some number of elements were moved from the front to the back. For example, [1,2,3,4,5,6,7] rotated by 3 becomes [4,5,6,7,1,2,3]. The minimum element is at the "rotation point" where the sequence breaks.

The key insight for binary search: compare the middle element to the rightmost element. If `nums[mid] > nums[right]`, the rotation point (and therefore the minimum) is somewhere in the right half. If `nums[mid] <= nums[right]`, mid is already in the right (sorted) section, so the minimum is at mid or to the left.

This works because one half of the array is always in sorted order, and the minimum is always in the unsorted half (or at the boundary).

```
Input: nums = [6, 7, 9, 11, 15, 2, 3, 5]  (originally [2,3,5,6,7,9,11,15], rotated by 5)

  left=0, right=7
  mid=3 → nums[3]=11, nums[right]=nums[7]=5
  11 > 5 → minimum is in the right half. left = 4.
  Eliminated: [6, 7, 9, 11] (all larger than 5, can't contain the min)

  left=4, right=7
  mid=5 → nums[5]=2, nums[right]=5
  2 <= 5 → minimum is at mid or to the left. right = 5.
  Eliminated: [3, 5]

  left=4, right=5
  mid=4 → nums[4]=15, nums[right]=nums[5]=2
  15 > 2 → left = 5

  left=5, right=5 → left == right. Minimum is nums[5] = 2.

4 steps for 8 elements. The minimum is 2, which is at the rotation point
where 15 drops to 2 (the original beginning of the sorted array).

No-rotation case: nums = [1, 2, 3, 4, 5]
  mid=2 → nums[2]=3 <= nums[4]=5 → right=2
  mid=1 → nums[1]=2 <= nums[2]=3 → right=1
  mid=0 → nums[0]=1 <= nums[1]=2 → right=0
  left==right==0 → minimum is nums[0] = 1. Correctly identifies the
  first element as the minimum (no rotation happened).
```

---

## Approaches

### Approach: Modified Binary Search

<details>
<summary>💡 Hint 1</summary>

Compare the middle element to the rightmost element. Which half must contain the minimum?

</details>

<details>
<summary>💡 Hint 2</summary>

If `nums[mid] > nums[right]`, the rotation point (minimum) is somewhere to the right of mid. If `nums[mid] <= nums[right]`, either mid is the minimum or the minimum is to the left.

</details>

<details>
<summary>📝 Explanation</summary>

Standard binary search compares mid to the target. Here, we compare mid to the rightmost element to determine which half contains the minimum.

The logic:
- If `nums[mid] > nums[right]`: the rotation point is between mid+1 and right. The left half (including mid) is part of the "rotated up" section and can't contain the minimum. Set `left = mid + 1`.
- If `nums[mid] <= nums[right]`: mid through right is sorted normally. The minimum could be at mid, but not after it. Set `right = mid` (not `mid - 1`, because mid itself might be the answer).

Note the asymmetry: `left = mid + 1` (excluding mid) vs `right = mid` (including mid). This is because:
- When we go right, mid is too large to be the minimum, so we exclude it.
- When we go left, mid might be the minimum, so we keep it.

The loop condition is `while left < right` (not `<=`). When left == right, we've converged to the minimum. Return `nums[left]`.

Why compare to the right end instead of the left? Comparing to the right consistently tells us which half has the rotation break. Comparing to the left creates ambiguous cases when the array isn't rotated.

**Time:** O(log n) - halving the range each step.
**Space:** O(1).

This problem assumes no duplicates. With duplicates (LeetCode 154), the worst case degrades to O(n) because you can't always determine which half to eliminate.

</details>

<details>
<summary>💻 Code</summary>

```python
def find_min(nums: list[int]) -> int:
    left, right = 0, len(nums) - 1
    while left < right:
        mid = (left + right) // 2
        if nums[mid] > nums[right]:
            left = mid + 1
        else:
            right = mid
    return nums[left]
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Standard rotation | `[3,4,5,1,2]` | `1` | Happy path |
| Not rotated | `[11,13,15,17]` | `11` | Minimum is at index 0 |
| Two elements rotated | `[2,1]` | `1` | Minimum array with rotation |
| Two elements sorted | `[1,2]` | `1` | No rotation |
| Single element | `[1]` | `1` | Trivial case |
| Rotation at end | `[2,3,4,5,1]` | `1` | Min is last element |

---

## Common Pitfalls

1. **Comparing to `nums[left]` instead of `nums[right]`** - Leads to ambiguous cases when the array isn't rotated. Always compare to right.
2. **Using `right = mid - 1`** - Mid could be the minimum. Skipping it with `mid - 1` loses the answer.
3. **Forgetting the not-rotated case** - When the array is fully sorted, `nums[mid] <= nums[right]` for every mid, and the loop correctly converges on index 0.
4. **Handling duplicates** - This problem guarantees unique elements. With duplicates (LeetCode 154), the worst case degrades to O(n) because you can't determine which half to eliminate when `nums[mid] == nums[right]`.

---

## Interview Tips

**What to say:**
> "In a rotated sorted array, I can compare the midpoint to the rightmost element to determine which half contains the minimum. If mid is greater than right, the rotation point is to the right. Otherwise, mid could be the minimum, so I set right = mid."

**If asked about duplicates:**
> "With unique elements I can always determine which half to search. With duplicates, when nums[mid] equals nums[right], I can't tell - I'd have to shrink right by one, making worst case O(n)."

**This problem is a building block.** Once you can find the pivot, you can search in a rotated array (#33) by first finding the rotation point and then binary searching the correct half.

**What the interviewer evaluates:** The rotation adds ambiguity to each comparison. You must reason about which half is sorted to decide which way to go. Walking through examples with the interviewer (showing how the comparison determines the search direction) demonstrates careful analysis.

---

## DE Application

Rotated sorted arrays are rare in data engineering, but the underlying skill - modifying binary search for partially ordered data - shows up when:
- Searching in data that's "almost sorted" (common after partitioned processing)
- Finding the changeover point between two different data regimes
- Detecting where a pipeline started writing to a new partition

The bigger lesson: binary search doesn't require perfectly sorted data. It requires a condition that lets you eliminate half the search space.

---

## At Scale

Finding the rotation point in a rotated sorted array is a single O(log n) operation. The practical application at scale: finding the partition boundary in range-partitioned data that has been rotated (e.g., time-partitioned data where partitions wrap around). More commonly, the "binary search on a nearly-sorted structure" pattern applies to searching log files that are sorted within segments but segments may be out of order. At 1B elements, the 30-comparison cost is dominated by the cost of loading the relevant cache lines or disk pages.

---

## Related Problems

- [704. Binary Search](704_binary_search.md) - Foundation (standard sorted array)
- [33. Search in Rotated Sorted Array](033_search_rotated.md) - Find a target in a rotated array (builds on this)
- [154. Find Minimum in Rotated Sorted Array II](https://leetcode.com/problems/find-minimum-in-rotated-sorted-array-ii/) - Same problem with duplicates
