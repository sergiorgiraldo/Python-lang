# Squares of a Sorted Array (LeetCode #977)

🔗 [LeetCode 977: Squares of a Sorted Array](https://leetcode.com/problems/squares-of-a-sorted-array/)

> **Difficulty:** Easy | **Interview Frequency:** Occasional

## Problem Statement

Given a sorted array of integers, return an array of the squares of each number, sorted in non-decreasing order.

**Example:**
```
Input: nums = [-4, -1, 0, 3, 10]
Output: [0, 1, 9, 16, 100]
```

**Constraints:**
- 1 <= nums.length <= 10^4
- -10^4 <= nums[i] <= 10^4
- nums is sorted in non-decreasing order

---

## Thought Process

1. **Naive approach** - Square everything, then sort. O(n log n).
2. **Can we do O(n)?** - The input is sorted. After squaring, the largest values are at the extremes (large negatives become large positives). The smallest squares are near zero.
3. **Opposite-end pointers** - Compare squares at both ends, take the larger one, fill the result from the back.
4. **This is a merge variant** - We're merging two "sorted" sequences (left half reversed and right half) into one.

---

## Worked Example

In a sorted array with negatives, the largest squared values are at the ends (large negatives become large positives). Two pointers from both ends build the result from largest to smallest, filling from the back.

```
Input: nums = [-7, -3, -1, 2, 4, 6]

  left=0 (49), right=5 (36), write=5

  49 > 36 → result[5]=49. left=1.     result = [_, _, _, _, _, 49]
  9 < 36  → result[4]=36. right=4.    result = [_, _, _, _, 36, 49]
  9 < 16  → result[3]=16. right=3.    result = [_, _, _, 16, 36, 49]
  9 > 4   → result[2]=9. left=2.      result = [_, _, 9, 16, 36, 49]
  1 < 4   → result[1]=4. right=2.     result = [_, 4, 9, 16, 36, 49]
  left=right=2: result[0]=1.          result = [1, 4, 9, 16, 36, 49]

One pass, O(n). The naive approach (square everything, then sort) is O(n log n).
```

---

## Approaches

### Approach 1: Square and Sort

<details>
<summary>📝 Explanation</summary>

Square every element, then sort the result. One line in Python: `sorted(x*x for x in nums)`.

The squaring step is O(n) but the sort step is O(n log n), which dominates. The sort is needed because squaring can change the relative order when negatives are present: [-4, -1, 3] squares to [16, 1, 9], which isn't sorted.

**Time:** O(n log n) - sort dominates. **Space:** O(n) for the result.

This ignores the sorted structure of the input. Since the largest squares are always at the extremes of the sorted array, two pointers can build the result in O(n).

</details>

### Approach 2: Opposite-End Pointers (Optimal)

<details>
<summary>💡 Hint</summary>

After squaring, where are the largest values? Where are the smallest?

</details>

<details>
<summary>📝 Explanation</summary>

Largest squared values are at the extremes (large negatives become large positives). Two pointers from both ends, compare absolute values, write the larger to the back of the result array.

1. Create result array of size n.
2. left=0, right=n-1, write=n-1.
3. Compare abs(nums[left]) vs abs(nums[right]). Write the larger squared value at result[write]. Move that pointer inward. Decrement write.

**Time:** O(n) - each element squared and placed once.
**Space:** O(n) - result array (can't do in-place since we write from the back).

Same "fill from the back" idea as Merge Sorted Array (problem 88).

</details>

<details>
<summary>💻 Code</summary>

```python
def sorted_squares(nums: list[int]) -> list[int]:
    n = len(nums)
    result = [0] * n
    left, right = 0, n - 1
    write = n - 1
    while left <= right:
        left_sq = nums[left] ** 2
        right_sq = nums[right] ** 2
        if left_sq >= right_sq:
            result[write] = left_sq
            left += 1
        else:
            result[write] = right_sq
            right -= 1
        write -= 1
    return result
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Mixed signs | `[-4,-1,0,3,10]` | `[0,1,9,16,100]` | Core case |
| All positive | `[0,1,2]` | `[0,1,4]` | Right pointer does all the work |
| All negative | `[-5,-3,-1]` | `[1,9,25]` | Left pointer does all the work |
| Symmetric | `[-3,-2,-1,1,2,3]` | `[1,1,4,4,9,9]` | Equal squares from both sides |
| Single | `[5]` | `[25]` | Boundary |

---

## Common Pitfalls

1. **Filling from the front instead of the back** - We're placing the largest first, so fill from the end of the result array
2. **Off-by-one with `left <= right`** - Need `<=` to handle the last remaining element when pointers meet

---

## Interview Tips

**What to say:**
> "Since the input is sorted, the largest squares are at the extremes. I'll use opposite-end pointers, compare squares, and fill the result from the back. That gives O(n) instead of O(n log n) from sorting."

This is a good warm-up problem. Solve it quickly to show pattern fluency.

**What the interviewer evaluates:** Recognizing that the largest squares come from the extremes tests insight over brute force. The "two sorted halves" observation is the key. This is a warm-up problem - the interviewer expects a clean O(n) solution quickly and will move to harder follow-ups.

---

## DE Application

This "transform and merge" pattern shows up when:
- Applying a non-monotonic transformation to sorted data and re-sorting efficiently
- Merging data from two ends of a time range (e.g., combining oldest and newest records)
- The concept of "largest values at the extremes" applies to any U-shaped or V-shaped distribution

---

## At Scale

Two pointers from both ends produces a sorted result in O(n) time and O(n) space (for the output array). The key insight - largest squares are at the extremes of a sorted array with negatives - avoids an O(n log n) sort of the squared values. At 1B elements, saving the log n factor means ~30x faster. In data pipelines, the "merge two sorted sequences" pattern appears whenever you combine pre-sorted partitions. A sorted output from two sorted inputs is the merge step of merge sort, sort-merge joins and external sorting.

---

## Related Problems

- [88. Merge Sorted Array](088_merge_sorted.md) - Same fill-from-back technique
- [167. Two Sum II](167_two_sum_ii.md) - Same opposite-ends on sorted data
