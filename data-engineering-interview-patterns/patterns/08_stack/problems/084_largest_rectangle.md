# Largest Rectangle in Histogram (LeetCode #84)

🔗 [LeetCode 84: Largest Rectangle in Histogram](https://leetcode.com/problems/largest-rectangle-in-histogram/)

> **Difficulty:** Hard | **Interview Frequency:** Occasional

## Problem Statement

Given an array of integers `heights` representing a histogram where each bar has width 1, find the area of the largest rectangle that fits within the histogram.

Example: `[2, 1, 5, 6, 2, 3]` → 10 (rectangle of height 5 spanning indices 2-3)

## Thought Process

1. **Brute force:** For each bar, expand left and right as far as the bar's height allows. Area = height × width. O(n²).
2. **The insight:** For each bar, we need to know how far it can extend left and right before hitting a shorter bar. That's "previous smaller element" (left boundary) and "next smaller element" (right boundary).
3. **Monotonic increasing stack:** Maintain a stack of indices with increasing heights. When a shorter bar arrives, it's the right boundary for everything in the stack that's taller. Pop those bars and calculate their areas.

## Worked Example

A monotonic increasing stack of bar indices. When a shorter bar arrives, it "closes off" all taller bars in the stack. For each popped bar, we know its right boundary (the current shorter bar) and its left boundary (the new stack top after popping). Width = right boundary - left boundary - 1.

```
Input: heights = [2, 1, 5, 6, 2, 3]
Append sentinel 0: [2, 1, 5, 6, 2, 3, 0]

i=0 (h=2): Stack empty. Push 0.          Stack: [0(2)]
i=1 (h=1): 1 < 2. Pop 0.
           height=2, width=1 (no stack left, so width=i=1).
           area = 2×1 = 2. max=2.
           Push 1.                        Stack: [1(1)]
i=2 (h=5): 5 > 1. Push 2.               Stack: [1(1), 2(5)]
i=3 (h=6): 6 > 5. Push 3.               Stack: [1(1), 2(5), 3(6)]
i=4 (h=2): 2 < 6. Pop 3.
           height=6, width=4-2-1=1. area=6. max=6.
           2 < 5. Pop 2.
           height=5, width=4-1-1=2. area=10. max=10.
           2 > 1. Push 4.                Stack: [1(1), 4(2)]
i=5 (h=3): 3 > 2. Push 5.               Stack: [1(1), 4(2), 5(3)]
i=6 (h=0): sentinel. Pop 5.
           height=3, width=6-4-1=1. area=3.
           Pop 4. height=2, width=6-1-1=4. area=8.
           Pop 1. height=1, width=6 (stack empty). area=6.
           max stays 10.

Answer: 10 (height 5, spanning indices 2-3).

The sentinel (height 0) at the end forces all remaining bars to be
popped and evaluated. Without it, bars remaining in the stack at
the end would be missed.
```

## Approaches

### Approach 1: Brute Force (Expand from Each Bar)

<details>
<summary>📝 Explanation</summary>

For each bar at index i, use its height as the rectangle height. Expand left while adjacent bars are at least as tall. Expand right similarly. The width is the total span. Area = height × width. Track the maximum.

**Time:** O(n²) - each bar can expand up to n positions.
**Space:** O(1).

State it, note the complexity, then optimize.

</details>

### Approach 2: Monotonic Increasing Stack

<details>
<summary>📝 Explanation</summary>

Maintain a stack of indices where `heights[stack[i]]` is in increasing order. When a bar shorter than the stack top arrives:

1. Pop the top. The popped bar's height is the rectangle height.
2. The right boundary is the current index `i` (the shorter bar that caused the pop).
3. The left boundary is the new stack top (the first bar to the left that's shorter than the popped bar). If the stack is empty, the popped bar extends all the way to the left edge.
4. Width = right - left - 1 (or just `i` if the stack is empty).
5. Area = height × width. Update the maximum.

Repeat until the stack top is shorter than the current bar (or the stack is empty). Then push the current bar.

A sentinel value of 0 appended to the end ensures all bars get popped and evaluated. Without it, you'd need a separate cleanup loop for bars remaining in the stack.

**Time:** O(n) - each bar is pushed once and popped once.
**Space:** O(n) - the stack.

This is one of the hardest standard stack problems. The width calculation is the tricky part. Practice computing `i - stack[-1] - 1` with concrete examples until it clicks.

</details>

## Edge Cases

| Input | Expected | Why |
|---|---|---|
| `[]` | 0 | Empty histogram |
| `[5]` | 5 | Single bar |
| `[3, 3, 3]` | 9 | All equal - rectangle spans everything |
| `[1, 2, 3, 4, 5]` | 9 | Increasing - best is 3×3 at the end |
| `[5, 4, 3, 2, 1]` | 9 | Decreasing - best is 3×3 from the start |
| `[1, 100, 1]` | 100 | Tall spike - height=100, width=1 |

## Common Pitfalls

- **Width calculation when stack is empty:** When the stack is empty after popping, the popped bar extends from index 0 to i-1. Width = i, not i-1.
- **Forgetting the sentinel:** Without appending 0 at the end, bars remaining in the stack are never evaluated. Common source of wrong answers.
- **Off-by-one in width formula:** `i - stack[-1] - 1` is the width between the current index and the new stack top. Draw it out with specific numbers.

## Interview Tips

> "Each bar's maximum rectangle depends on how far it can extend left and right before hitting a shorter bar. A monotonic increasing stack gives me both boundaries in O(n): the left boundary is the previous stack entry, the right boundary is whatever causes the bar to be popped."

**Common follow-up:** "Explain the width calculation." Walk through a specific example: when we pop index 2 (height=5) at index 4, the new stack top is index 1. Width = 4 - 1 - 1 = 2. The rectangle spans indices 2 and 3.

**What the interviewer evaluates:** This is a hard problem. The monotonic increasing stack with sentinel values is a common technique. Most candidates struggle with what happens when you pop (computing the width using the new top of stack as the left boundary). Walking through a complete example with the interviewer demonstrates composure under complexity. This problem is often the final, hardest problem in an interview set.

## DE Application

Resource utilization analysis: given a histogram of concurrent connections over time buckets, what's the largest sustained capacity window? Same structure as largest rectangle. Also applies to finding the widest time range where throughput exceeded a threshold.

## At Scale

The monotonic increasing stack approach is O(n) time and O(n) memory. For 10M histogram bars, that's ~80MB and completes in ~100ms. The brute force O(n^2) approach would take hours. At scale, the largest rectangle problem appears in resource allocation: "given varying capacity over time, what's the maximum sustained load I can handle?" The rectangle area (height * width) represents sustained throughput over a time period. In capacity planning, finding these rectangles across different time windows helps identify optimal maintenance windows and scaling triggers. The stack-based O(n) solution is essential because capacity data can span millions of time points.

## Related Problems

- [85. Maximal Rectangle](https://leetcode.com/problems/maximal-rectangle/) - 2D version (apply this per row)
- [42. Trapping Rain Water](https://leetcode.com/problems/trapping-rain-water/) - Related histogram problem
- [739. Daily Temperatures](https://leetcode.com/problems/daily-temperatures/) - Same monotonic stack pattern
