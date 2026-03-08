# Maximum Average Subarray I (LeetCode #643)

🔗 [LeetCode 643: Maximum Average Subarray I](https://leetcode.com/problems/maximum-average-subarray-i/)

> **Difficulty:** Easy | **Interview Frequency:** Occasional

## Problem Statement

Given an integer array `nums` and an integer `k`, find the contiguous subarray of length `k` that has the maximum average value. Return the maximum average.

**Example:**
```
Input: nums = [1, 12, -5, -6, 50, 3], k = 4
Output: 12.75
Explanation: Maximum average is (12 - 5 - 6 + 50) / 4 = 12.75
```

**Constraints:**
- n == nums.length
- 1 <= k <= n <= 10^5
- -10^4 <= nums[i] <= 10^4

---

## Thought Process

1. **Brute force:** Compute the average of every subarray of size k. That's O(n * k) - for each of n-k+1 starting positions, sum k elements.
2. **Observation:** Adjacent windows overlap by k-1 elements. When the window slides one position right, only one element enters and one leaves.
3. **Optimization:** Maintain a running sum. Each slide: add the new element, subtract the old one. Update: O(1) per slide, O(n) total.

---

## Worked Example

The simplest sliding window problem: find the maximum average of any subarray of length k. Since the length is fixed, the window just slides one position at a time. For each slide, add the new element and subtract the one that fell off. Track the maximum sum (dividing by k at the end gives the average).

```
Input: nums = [1, 12, -5, -6, 50, 3, 8, -2], k = 4

  Initialize: window = [1, 12, -5, -6], sum = 2

  Slide right, add 50, remove 1:  sum = 2 + 50 - 1 = 51.  [12, -5, -6, 50]  max_sum=51
  Slide right, add 3, remove 12:  sum = 51 + 3 - 12 = 42. [-5, -6, 50, 3]   max_sum=51
  Slide right, add 8, remove -5:  sum = 42 + 8 - (-5) = 55. [-6, 50, 3, 8]  max_sum=55
  Slide right, add -2, remove -6: sum = 55 + (-2) - (-6) = 59. [50, 3, 8, -2] max_sum=59

  Maximum average = 59 / 4 = 14.75

5 window positions checked in O(n) total. Each slide was one addition
and one subtraction. The brute force approach (re-sum all k elements for
each position) would do 4 additions per position × 5 positions = 20 additions.
Small savings here, but for k=10,000 the difference is dramatic.
```

---

## Approaches

### Approach 1: Brute Force

<details>
<summary>📝 Explanation</summary>

For every possible starting position (0 through n-k), sum the k elements in that subarray and compute the average. Track the maximum.

Two nested loops: outer loop over starting positions, inner loop sums k elements.

**Time:** O(n × k) - n-k+1 windows, each requiring k additions.
**Space:** O(1).

For large k, this is slow. If n = 100,000 and k = 10,000, that's a billion operations.

</details>

<details>
<summary>💻 Code</summary>

```python
def find_max_average_brute(nums: list[int], k: int) -> float:
    max_avg = float("-inf")
    for i in range(len(nums) - k + 1):
        avg = sum(nums[i:i+k]) / k
        max_avg = max(max_avg, avg)
    return max_avg
```

</details>

### Approach 2: Sliding Window (Optimal)

<details>
<summary>💡 Hint</summary>

You don't need to recompute the sum from scratch each time. What changes when the window moves one position?

</details>

<details>
<summary>📝 Explanation</summary>

Compute the sum of the first k elements. Then slide the window one position at a time: add the new element entering the window on the right and subtract the element leaving on the left. Each slide updates the sum in O(1) instead of re-summing all k elements.

1. `window_sum = sum(nums[:k])` - initial window.
2. `max_sum = window_sum`.
3. For i from k to n-1:
   - `window_sum += nums[i] - nums[i - k]` (add new, subtract old)
   - Update `max_sum` if window_sum is larger.
4. Return `max_sum / k`.

**Time:** O(n) - one pass. Each element is added once and subtracted once.
**Space:** O(1) - just the running sum.

The key insight: consecutive windows overlap by k-1 elements. Re-summing all k elements wastes work on the k-1 elements that didn't change. The sliding window only processes the one element that changed on each end.

</details>

<details>
<summary>💻 Code</summary>

```python
def find_max_average(nums: list[int], k: int) -> float:
    window_sum = sum(nums[:k])
    max_sum = window_sum
    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]
        max_sum = max(max_sum, window_sum)
    return max_sum / k
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Basic | `[1,12,-5,-6,50,3], 4` | `12.75` | Standard case |
| Single element | `[5], 1` | `5.0` | Window = entire array |
| All negative | `[-1,-2,-3,-4], 2` | `-1.5` | Max of negatives |
| All same | `[5,5,5,5], 2` | `5.0` | No variation |
| Max at end | `[1,1,1,1,10,10], 2` | `10.0` | Don't stop early |
| Max at start | `[10,10,1,1,1,1], 2` | `10.0` | Initial window could be best |

---

## Common Pitfalls

1. **Dividing in the loop** - Divide by k once at the end, not every iteration. Tracking the sum is cleaner and avoids floating point accumulation.
2. **Off-by-one in loop range** - The loop starts at index k (the first new element to add), not k-1.
3. **Not initializing max_sum** - Initialize with the first window's sum, not 0 (which would be wrong if all values are negative).

---

## Interview Tips

**This is a warm-up problem.** Solve it quickly and cleanly. The real value is demonstrating you know the fixed-window template, which extends to harder problems.

**What to say:**
> "This is a fixed-size sliding window. I'll compute the first window's sum, then slide by adding and subtracting one element at a time."

**What the interviewer evaluates:** This is a warm-up. Clean O(n) with O(1) space is expected quickly. The interviewer is testing whether you know the fixed-size sliding window template. Finishing fast earns time for harder follow-ups.

---

## DE Application

Fixed-window aggregations are everywhere in data engineering:
- Moving averages for dashboard metrics
- Rolling sums for billing calculations
- Sliding counts for rate limiting
- Any `AVG(x) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)` in SQL

This problem is the algorithmic foundation for all of those.

## At Scale

Fixed-size sliding window uses O(1) memory regardless of input size. For 1B elements with window size 1000, you store only the running sum and the window boundaries. The computation is dominated by I/O (reading the data) not memory or CPU. In streaming systems, this is a tumbling or sliding window aggregate: `SELECT AVG(value) OVER (ORDER BY timestamp ROWS BETWEEN 999 PRECEDING AND CURRENT ROW)`. At scale, the concern shifts from algorithm efficiency to data freshness: how quickly does the window update as new data arrives? Micro-batch (Spark) updates every few seconds; true streaming (Flink) updates per event.

---

## Related Problems

- [219. Contains Duplicate II](219_contains_duplicate_ii.md) - Fixed window with a hash set instead of a sum
- [239. Sliding Window Maximum](239_sliding_window_max.md) - Fixed window where you need the max, not sum (requires a deque)
- [3. Longest Substring Without Repeating](003_longest_substring.md) - Variable window (window size isn't fixed)
