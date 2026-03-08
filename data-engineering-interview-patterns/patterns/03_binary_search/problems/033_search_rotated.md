# Search in Rotated Sorted Array (LeetCode #33)

🔗 [LeetCode 33: Search in Rotated Sorted Array](https://leetcode.com/problems/search-in-rotated-sorted-array/)

> **Difficulty:** Medium | **Interview Frequency:** Common

## Problem Statement

An integer array sorted in ascending order was rotated at some pivot. Given the rotated array (all unique values) and a target, return its index or -1 if not found.

You must achieve O(log n) runtime.

**Example:**
```
Input: nums = [4, 5, 6, 7, 0, 1, 2], target = 0
Output: 4

Input: nums = [4, 5, 6, 7, 0, 1, 2], target = 3
Output: -1
```

**Constraints:**
- 1 <= nums.length <= 5000
- -10^4 <= nums[i] <= 10^4
- All values unique
- nums was originally sorted and rotated between 1 and n times

---

## Thought Process

1. **Can't just binary search normally** - The array isn't fully sorted. Standard comparison to target would go the wrong way.
2. **But one half is always sorted** - At any midpoint in a rotated sorted array, either the left half or the right half is in proper sorted order.
3. **Check if target is in the sorted half** - If the left half is sorted and target falls in its range, go left. Otherwise go right. Same logic if the right half is sorted.
4. **Two approaches** - Single-pass (determine sorted half at each step) or two-pass (find the pivot first, then binary search the correct half).

---

## Worked Example

Unlike "find minimum in rotated array" (which searches for the rotation point), this problem searches for a specific target value. The insight: in a rotated sorted array, at least one half is always sorted normally. We can check which half is sorted and determine if the target falls within that sorted range. If it does, search there. If not, search the other half.

```
Input: nums = [6, 7, 9, 11, 15, 2, 3, 5], target = 3

  left=0, right=7, mid=3 → nums[3] = 11
  Is the left half [6,7,9,11] sorted? nums[0]=6 <= nums[3]=11 → yes.
  Is target 3 in the range [6, 11]? 3 < 6 → no.
  So target must be in the right half. left = 4.

  left=4, right=7, mid=5 → nums[5] = 2
  Is the left half [15,2] sorted? nums[4]=15 <= nums[5]=2? No → right half is sorted.
  Is the right half [2,3,5] sorted? Yes. Is target 3 in range [2, 5]? 2 <= 3 <= 5 → yes.
  Search right half: left = 6.

  Wait, let me redo this more carefully:
  left=4, right=7, mid=5 → nums[5] = 2
  Check left half: nums[left]=nums[4]=15, nums[mid]=2. 15 > 2 → left half NOT sorted.
  So right half [2, 3, 5] IS sorted.
  Is target 3 in [nums[mid+1]..nums[right]] = [3, 5]? 3 >= 3 and 3 <= 5 → yes.
  left = mid + 1 = 6.

  left=6, right=7, mid=6 → nums[6] = 3
  3 == 3 → found it. Return index 6.

3 steps for 8 elements.

Not-found case: target = 10
  left=0, right=7, mid=3 → 11. Left [6,7,9,11] sorted. 6 <= 10 <= 11 → target in left half.
  right=3. left=0, right=3, mid=1 → 7. Left [6,7] sorted. 6 <= 10? yes. 10 <= 7? no.
  Target not in left [6,7]. Go right: left=2.
  left=2, right=3, mid=2 → 9. Left [9] sorted. 9 <= 10? yes. But right = 3, mid = 2.
  nums[left]=9 <= nums[mid]=9. Sorted left. 9 <= 10 <= 9? No (10 > 9). Go right: left=3.
  left=3, right=3, mid=3 → 11. 11 != 10. 11 > 10 → right=2.
  left=3 > right=2 → not found. Return -1.
```

---

## Approaches

### Approach 1: Single-Pass (Determine Sorted Half)

<details>
<summary>💡 Hint 1</summary>

At each midpoint, one half is always sorted. How can you tell which one?

</details>

<details>
<summary>💡 Hint 2</summary>

If `nums[left] <= nums[mid]`, the left half is sorted. Check if target falls in `[nums[left], nums[mid])`. If yes, go left. If no, go right.

</details>

<details>
<summary>📝 Explanation</summary>

At each step, determine which half of the array is sorted (at least one half always is in a rotated sorted array). Then check if the target falls within the sorted half's range. If yes, search that half. If no, search the other half.

The decision process at each step:
1. Check if the left half `[left..mid]` is sorted: `nums[left] <= nums[mid]`.
2. If the left half is sorted, check if target is in range `[nums[left], nums[mid]]`. If yes, go left (`right = mid - 1`). If no, go right (`left = mid + 1`).
3. If the left half is NOT sorted, the right half must be sorted. Check if target is in range `[nums[mid], nums[right]]`. If yes, go right. If no, go left.

This works because one half is always sorted (the rotation break can only be in one half). By checking the sorted half's range, we reliably determine where the target could be.

**Time:** O(log n) - halving the search space each step.
**Space:** O(1).

The tricky part is getting the comparisons right. Draw out examples with the rotation in the left half vs the right half to build intuition.

</details>

<details>
<summary>💻 Code</summary>

```python
def search(nums: list[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        if nums[left] <= nums[mid]:
            # Left half is sorted
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            # Right half is sorted
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1
```

</details>

### Approach 2: Find Pivot, Then Binary Search

<details>
<summary>📝 Explanation</summary>

Split the problem into two simpler steps:
1. Find the rotation point (minimum element) using the technique from problem 153.
2. Determine which sorted half the target is in, then do a standard binary search on that half.

After finding the minimum at index `pivot`:
- Left sorted half: `nums[0..pivot-1]`
- Right sorted half: `nums[pivot..n-1]`
- If `target >= nums[0]`, it's in the left half (or the array isn't rotated).
- Otherwise, it's in the right half.

**Time:** O(log n) - two binary searches, each O(log n).
**Space:** O(1).

This is conceptually simpler (two standard binary searches instead of one modified one) but requires two passes. Most interviewers are fine with either approach.

</details>

<details>
<summary>💻 Code</summary>

```python
def search_with_pivot(nums: list[int], target: int) -> int:
    if not nums:
        return -1
    n = len(nums)

    # Find the pivot (minimum)
    lo, hi = 0, n - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        else:
            hi = mid
    pivot = lo

    # Choose which half to search
    if target >= nums[pivot] and target <= nums[n - 1]:
        lo, hi = pivot, n - 1
    else:
        lo, hi = 0, pivot - 1

    # Standard binary search
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Found in right half | `[4,5,6,7,0,1,2], 0` | `4` | Standard case |
| Not found | `[4,5,6,7,0,1,2], 3` | `-1` | Target doesn't exist |
| Found in left half | `[4,5,6,7,0,1,2], 5` | `1` | Target in higher segment |
| First element | `[4,5,6,7,0,1,2], 4` | `0` | Left boundary |
| Last element | `[4,5,6,7,0,1,2], 2` | `6` | Right boundary |
| Single element | `[1], 1` | `0` | Trivial case |
| Not rotated | `[1,2,3,4,5], 3` | `2` | Degenerates to standard search |
| Two elements rotated | `[3,1], 1` | `1` | Minimal rotation |
| Empty | `[], 1` | `-1` | No data |

---

## Common Pitfalls

1. **Using `<` instead of `<=` when checking `nums[left] <= nums[mid]`** - Fails when left equals mid (two elements remaining).
2. **Getting range checks wrong** - The boundary conditions in `nums[left] <= target < nums[mid]` (strict less on right) and `nums[mid] < target <= nums[right]` (strict less on left) are precise. Missing the `=` on either bound means you skip the first or last element.
3. **Not handling the non-rotated case** - If the array isn't rotated, the algorithm should still work. It does, because the left half is always sorted in this case.

---

## Interview Tips

**What to say:**
> "In a rotated sorted array, one half is always sorted at any midpoint. I'll determine which half is sorted, check if the target falls in its range and narrow accordingly."

**Single-pass vs two-pass:**
> "I can either determine the sorted half at each step (single pass) or find the rotation pivot first and then do a standard binary search (two passes). Both are O(log n). I'll go with [whichever you're more confident implementing]."

**If asked "what if there are duplicates?"**
> "With duplicates, when nums[left] equals nums[mid], I can't tell which half is sorted. I'd need to increment left and try again, making worst case O(n). That's LeetCode 81."

**What the interviewer evaluates:** This combines the rotation handling from 153 with the target search from 704. Getting both right under pressure tests composure and systematic thinking. Off-by-one errors are common - using `<=` vs `<` in the boundary check is where most bugs hide.

---

## DE Application

Searching in non-trivially sorted data comes up when:
- Data partitions have been reorganized but maintain internal ordering
- Logs from multiple sources are interleaved but each source's entries are sorted
- Historical data has been archived and reloaded in a different order

The deeper lesson here isn't about rotated arrays specifically. It's about adapting binary search when the data has a known structural property you can exploit, even if it's not perfectly sorted.

---

## At Scale

Binary search in a rotated sorted array is O(log n) - same as standard binary search. The extra comparison per step (checking which half is sorted) doesn't change the asymptotic complexity. At scale, the important lesson is that binary search works on ANY structure with a monotonic property, not just perfectly sorted arrays. Database indexes handle this with B-tree variants that maintain balance through rotations. Log-structured merge trees (LSM trees, used in Cassandra and RocksDB) maintain multiple sorted runs and binary-search each one separately.

---

## Related Problems

- [153. Find Minimum in Rotated Sorted Array](153_find_min_rotated.md) - Find the pivot point (building block for this problem)
- [704. Binary Search](704_binary_search.md) - Standard version on fully sorted data
- [81. Search in Rotated Sorted Array II](https://leetcode.com/problems/search-in-rotated-sorted-array-ii/) - With duplicates
