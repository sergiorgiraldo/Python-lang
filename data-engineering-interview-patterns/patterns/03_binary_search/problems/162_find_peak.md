# Find Peak Element (LeetCode #162)

🔗 [LeetCode 162: Find Peak Element](https://leetcode.com/problems/find-peak-element/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

## Problem Statement

A peak element is strictly greater than its neighbors. Given an array where `nums[i] != nums[i+1]` for all valid i, find any peak element's index. The array boundaries are treated as -infinity (`nums[-1] = nums[n] = -∞`).

You must write an algorithm that runs in O(log n).

**Example:**
```
Input: nums = [1, 2, 3, 1]
Output: 2
Explanation: nums[2] = 3 is a peak (3 > 2 and 3 > 1)

Input: nums = [1, 2, 1, 3, 5, 6, 4]
Output: 5 (or 1 - any peak is valid)
```

**Constraints:**
- 1 <= nums.length <= 1000
- -2^31 <= nums[i] <= 2^31 - 1
- nums[i] != nums[i + 1] for all valid i

---

## Thought Process

1. **O(log n) means binary search.** But the array isn't sorted. Can binary search still work?
2. **It can, because we only need a local property.** We don't need to find a specific value. We need to find any point where the slope changes from rising to falling.
3. **The key insight:** If `nums[mid] < nums[mid + 1]`, the values are still rising. A peak must exist to the right (either the array keeps rising to the boundary, or it eventually falls). So we can safely eliminate the left half.
4. **This works because boundaries are -infinity.** The rising slope must eventually end - either at a peak in the middle or at the last element (which is a peak because its right boundary is -inf).

---

## Worked Example

A peak element is larger than both its neighbors. The array is guaranteed to have at least one peak (because the boundaries are treated as negative infinity). We can find a peak with binary search by "climbing uphill": compare the middle element with its right neighbor. If the right neighbor is larger, a peak must exist to the right (we're on an ascending slope). If the middle is larger, a peak must exist at mid or to the left.

This is a boundary-finding problem: we're looking for where the array switches from ascending to descending.

```
Input: nums = [1, 3, 5, 8, 6, 4, 2, 7, 9]

  left=0, right=8, mid=4 → nums[4]=6, nums[5]=4
  6 > 4 → we're descending to the right. Peak is at mid or to the left. right = 4.

  left=0, right=4, mid=2 → nums[2]=5, nums[3]=8
  5 < 8 → ascending to the right. Peak is to the right. left = 3.

  left=3, right=4, mid=3 → nums[3]=8, nums[4]=6
  8 > 6 → peak at mid or left. right = 3.

  left=3 == right=3 → converged. nums[3] = 8 is a peak.
  Check: 8 > nums[2]=5 and 8 > nums[4]=6. Confirmed.

3 steps for 9 elements. Note: index 8 (value 9) is also a peak
(since the right boundary is treated as -∞), but binary search
found index 3 first. Any peak is a valid answer.
```

---

## Approaches

### Approach: Binary Search on Slope

<details>
<summary>💡 Hint 1</summary>

You don't need the array to be sorted for binary search. You just need a condition that guarantees a valid answer exists in one half.

</details>

<details>
<summary>💡 Hint 2</summary>

Compare `nums[mid]` to `nums[mid + 1]`. If you're on a rising slope, which direction must have a peak?

</details>

<details>
<summary>📝 Explanation</summary>

Compare `nums[mid]` to `nums[mid + 1]` to determine the slope direction:

- If `nums[mid] < nums[mid + 1]`: we're on an ascending slope. A peak must exist to the right of mid (either the ascent ends at a peak, or we reach the right boundary which counts as a peak since `nums[n] = -∞`). Set `left = mid + 1`.
- If `nums[mid] > nums[mid + 1]`: we're on a descending slope (or at a peak). A peak is at mid or to the left. Set `right = mid`.

Loop condition: `while left < right`. When left == right, we've found a peak.

Why is a peak guaranteed to exist in the chosen direction? Because `nums[-1] = nums[n] = -∞` (virtual negative infinity at both boundaries). If we're ascending toward the right, either we find a descent (peak) or we reach the boundary (peak, since the boundary is -∞). Either way, a peak exists.

**Time:** O(log n) - halving each step.
**Space:** O(1).

This only finds one peak, not all peaks. But the problem only asks for any one. If the array has multiple peaks (like a mountain range), binary search finds whichever peak the halving path leads to.

</details>

<details>
<summary>💻 Code</summary>

```python
def find_peak_element(nums: list[int]) -> int:
    left, right = 0, len(nums) - 1
    while left < right:
        mid = (left + right) // 2
        if nums[mid] < nums[mid + 1]:
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
| Single peak | `[1,2,3,1]` | `2` | Standard case |
| Multiple peaks | `[1,2,1,3,5,6,4]` | `1` or `5` | Any valid peak |
| Single element | `[1]` | `0` | Always a peak |
| Ascending | `[1,2,3,4,5]` | `4` | Last element is peak |
| Descending | `[5,4,3,2,1]` | `0` | First element is peak |
| Two elements | `[1,2]` | `1` | Boundary case |
| Valley | `[5,1,5]` | `0` or `2` | Both ends are peaks |

---

## Common Pitfalls

1. **Accessing `nums[mid + 1]` out of bounds** - Doesn't happen because when `left == right`, the loop ends. And when `left < right`, `mid < right`, so `mid + 1 <= right` is valid.
2. **Returning the value instead of the index** - The problem asks for the index.
3. **Assuming one specific peak** - Multiple peaks may exist. The algorithm finds whichever one the binary search converges on. Tests should verify the result is *a* peak, not *the* peak.

---

## Interview Tips

**What to say:**
> "Even though the array isn't sorted, I can use binary search because I have a local property: if the slope is rising, a peak must be to the right. This lets me eliminate half the search space each step."

**This problem is a great conceptual question.** It tests whether you understand that binary search is about eliminating half the search space, not about sorted arrays. If you articulate that, you've demonstrated deeper understanding than someone who just memorized the pattern.

**If the interviewer asks "why does a peak always exist?"**
> "Because the boundaries are negative infinity. If the array is strictly ascending, the last element is a peak. If it's strictly descending, the first element is. Any other shape has at least one local maximum in the interior."

**What the interviewer evaluates:** The gradient-based binary search tests whether you can generalize binary search beyond sorted arrays. If you only know the "sorted array" version, you'll struggle here. The interviewer wants to see you reason about the binary search invariant: "why can I discard this half?"

---

## DE Application

The "binary search on a local property" concept applies when:
- Finding where a metric peaked or crossed a threshold in time-series data
- Detecting change points in sorted or semi-sorted data
- Any scenario where you need to find a transition point and can determine the direction at each check

The broader lesson: binary search works whenever you can determine which half to eliminate, even without global sorting.

---

## At Scale

Peak finding in O(log n) works because the problem has a "binary search the answer" structure: the gradient tells you which direction to move. At scale, this pattern appears in optimization and tuning: "find the configuration (batch size, partition count, parallelism) that maximizes throughput." If the performance curve is unimodal (one peak), binary search the parameter space. Ternary search generalizes this to any unimodal function. Distributed hyperparameter tuning (like Spark's ML tuning) uses similar search strategies over the parameter space.

---

## Related Problems

- [704. Binary Search](704_binary_search.md) - Standard sorted version
- [852. Peak Index in a Mountain Array](https://leetcode.com/problems/peak-index-in-a-mountain-array/) - Simpler variant (exactly one peak)
- [875. Koko Eating Bananas](875_koko_bananas.md) - Another non-sorted binary search (on answer space)
