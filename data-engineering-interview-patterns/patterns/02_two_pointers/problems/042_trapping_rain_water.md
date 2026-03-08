# Trapping Rain Water (LeetCode #42)

🔗 [LeetCode 42: Trapping Rain Water](https://leetcode.com/problems/trapping-rain-water/)

> **Difficulty:** Hard | **Interview Frequency:** Occasional

## Problem Statement

Given `n` non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it can trap after raining.

**Example:**
```
Input: height = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]
Output: 6

Visual:
       #
   #   ##
 # ## ####
_#_##_####_ → 6 units of water (between the bars)
```

**Constraints:**
- n == height.length
- 0 <= n <= 2 * 10^4
- 0 <= height[i] <= 10^5

---

## Thought Process

1. **Water at each position depends on the bars around it** - Specifically, the tallest bar to its left and the tallest bar to its right.
2. **Water at position i = min(max_left, max_right) - height[i]** - The water level is limited by the shorter of the two bounding walls.
3. **Brute force: O(n²)** - For each position, scan left and right to find the maximums.
4. **Prefix arrays: O(n) time, O(n) space** - Precompute left_max and right_max arrays.
5. **Two pointers: O(n) time, O(1) space** - Process from both sides, always handling the side with the smaller max. The logic: if left_max < right_max, water at the left position is determined by left_max alone (right side is guaranteed to be at least right_max).

---

## Worked Example

Water at position i = min(tallest wall to its left, tallest wall to its right) - height[i]. The two-pointer approach tracks running maximums from each side. If left_max < right_max, the water at the left pointer is determined by left_max (right side is at least as tall). Process whichever side has the smaller running max.

```
Input: height = [0, 2, 0, 3, 0, 1, 4, 0, 2, 0, 3]
  left=0, right=10, left_max=0, right_max=0, water=0

  left_max(0) ≤ right_max(0): process left
    left_max = max(0, h[0]=0) = 0. water += 0. left=1.
  left_max(0) ≤ right_max(0): process left
    left_max = max(0, h[1]=2) = 2. water += 0. left=2.
  left_max(2) > right_max(0): process right
    right_max = max(0, h[10]=3) = 3. water += 0. right=9.
  left_max(2) ≤ right_max(3): process left
    left_max stays 2. water += 2-0 = 2. left=3. (total: 2)
  left_max(2) ≤ right_max(3): process left
    left_max = max(2, h[3]=3) = 3. water += 0. left=4.
  left_max(3) ≤ right_max(3): process left
    water += 3-0 = 3. left=5. (total: 5)
  left_max(3) ≤ right_max(3): process left
    water += 3-1 = 2. left=6. (total: 7)
  left_max(3) ≤ right_max(3): process left
    left_max = max(3, h[6]=4) = 4. water += 0. left=7.
  left_max(4) > right_max(3): process right
    water += 3-0 = 3. right=8. (total: 10)
  left_max(4) > right_max(3): process right
    water += 3-2 = 1. right=7. (total: 11)
  left_max(4) > right_max(3): process right
    water += 3-0 = 3. right=6. (total: 14)
  left > right → done.

  Total water: 14. One pass, O(1) space.
```

---

## Approaches

### Approach 1: Prefix/Suffix Max Arrays

<details>
<summary>📝 Explanation</summary>

Water at position i = min(left_max[i], right_max[i]) - height[i].

Precompute two arrays:
- `left_max[i]` = max height from 0 through i (left to right scan)
- `right_max[i]` = max height from i through n-1 (right to left scan)

Third pass: for each position, compute the water using both arrays.

**Time:** O(n) - three passes.
**Space:** O(n) - two extra arrays.

Easier to understand than two pointers. Solid first answer.

</details>

<details>
<summary>💻 Code</summary>

```python
def trap_prefix_max(height: list[int]) -> int:
    if len(height) < 3:
        return 0
    n = len(height)
    left_max = [0] * n
    right_max = [0] * n

    left_max[0] = height[0]
    for i in range(1, n):
        left_max[i] = max(left_max[i - 1], height[i])

    right_max[n - 1] = height[n - 1]
    for i in range(n - 2, -1, -1):
        right_max[i] = max(right_max[i + 1], height[i])

    return sum(min(left_max[i], right_max[i]) - height[i] for i in range(n))
```

</details>

---

### Approach 2: Two Pointers (Optimal)

<details>
<summary>💡 Hint 1</summary>

You don't need to know the exact max on both sides. You just need to know which side has the smaller max.

</details>

<details>
<summary>💡 Hint 2</summary>

If `left_max < right_max`, the water at the left position is `left_max - height[left]`. It doesn't matter what the exact right_max is - it's at least as big as left_max, so left_max is the bottleneck.

</details>

<details>
<summary>📝 Explanation</summary>

Track running left_max and right_max as we go. If left_max ≤ right_max, the left side is the bottleneck. Process left and advance. Otherwise process right and retreat.

Why: when left_max ≤ right_max, we know the water at the left pointer is bounded by left_max regardless of what's further right (the right side is at least as tall). So we don't need the full right_max array.

**Time:** O(n) - single pass.
**Space:** O(1) - four variables.

Harder to reason about but optimal. The key proof: when processing the left side, left_max can only increase as left moves right, so the water calculation is correct even though we haven't seen the rest of the right side.

</details>

<details>
<summary>💻 Code</summary>

```python
def trap(height: list[int]) -> int:
    if len(height) < 3:
        return 0
    left, right = 0, len(height) - 1
    left_max, right_max = height[left], height[right]
    water = 0
    while left < right:
        if left_max <= right_max:
            left += 1
            left_max = max(left_max, height[left])
            water += left_max - height[left]
        else:
            right -= 1
            right_max = max(right_max, height[right])
            water += right_max - height[right]
    return water
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Classic | `[0,1,0,2,1,0,1,3,2,1,2,1]` | `6` | Standard case |
| Simple pool | `[1,0,1]` | `1` | Minimum trapping |
| V-shape | `[4,2,0,3,2,5]` | `9` | Deep valley |
| Empty | `[]` | `0` | Boundary |
| Flat | `[3,3,3,3]` | `0` | No valleys |
| Ascending | `[1,2,3,4,5]` | `0` | No right wall to trap |
| Bowl | `[5,0,5]` | `5` | Maximum trap between two bars |

---

## Common Pitfalls

1. **Including the bar's own height in the water** - Water is `min(left_max, right_max) - height[i]`, not just `min(left_max, right_max)`. The bar itself displaces water.
2. **Not handling the "less than 3 bars" case** - Need at least 3 bars to trap any water.
3. **Confusing with Container With Most Water** - Container uses two bars as walls. Trapping rain fills between all bars. Very different problems despite similar-looking inputs.

---

## Interview Tips

**What to say:**
> "Water at each position is determined by the minimum of the tallest bars on each side, minus the bar's own height. I can precompute left and right maximums for O(n) with O(n) space. For O(1) space, I use two pointers - processing whichever side has the smaller running max, since that side determines the water level."

**Start with the prefix array approach.** It's clearer and correct. Then optimize to two pointers when the interviewer asks about space. This shows the progression interviewers want to see.

**The "why process the smaller side" argument is the crux.** If `left_max = 3` and `right_max = 5`, water at the left position is `3 - height[left]`. We don't care that right_max might get even bigger - left_max is already the bottleneck.

**What the interviewer evaluates:** This is a hard problem used to test senior+ candidates. Multiple valid approaches (prefix arrays, two pointers, monotonic stack) exist. Starting with the prefix approach (correct but O(n) space), then optimizing to two pointers (O(1) space) shows the optimization process interviewers want to see. Explaining WHY the two-pointer invariant works is the principal-level differentiator.

---

## DE Application

The "bounded by surrounding context" pattern shows up in:
- Computing fill rates or capacity utilization bounded by upstream and downstream constraints
- Quality scores bounded by the weakest link in a pipeline
- Any metric where the effective value at a point depends on the minimum of its surrounding maximums

This is also a classic whiteboard problem that tests whether you can progress from brute force to optimal through systematic improvement.

---

## At Scale

The two-pointer approach uses O(1) memory and a single pass. The prefix max approach uses O(n) memory for the left_max and right_max arrays. At 10M elements, that's ~80MB of extra memory vs zero. At 1B elements, the O(n) approach needs 8GB of extra arrays - the two-pointer approach needs nothing. The monotonic stack approach (Pattern 08) also uses O(n) memory in the worst case. For time-series analysis at scale (finding periods where a metric dips below surrounding peaks), the two-pointer O(1)-memory approach is the only viable option for streaming data where you can't store the full history.

---

## Related Problems

- [11. Container With Most Water](011_container_water.md) - Simpler two-pointer problem with similar structure
- [238. Product of Array Except Self](https://leetcode.com/problems/product-of-array-except-self/) - Same prefix/suffix precomputation pattern
