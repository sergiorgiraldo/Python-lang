# Daily Temperatures (LeetCode #739)

🔗 [LeetCode 739: Daily Temperatures](https://leetcode.com/problems/daily-temperatures/)

> **Difficulty:** Medium | **Interview Frequency:** Common

## Problem Statement

Given an array of daily temperatures, return an array where each element tells you how many days you have to wait until a warmer temperature. If no future day is warmer, the answer is 0.

Example: `[73, 74, 75, 71, 69, 72, 76, 73]` → `[1, 1, 4, 2, 1, 1, 0, 0]`

## Thought Process

1. **Brute force:** For each day, scan forward until you find a warmer day. O(n²). Works but slow for large inputs.
2. **The key insight:** When we encounter a warm day, it resolves ALL recent cooler days at once. Day 76 in the example resolves both day 75 (waited 4 days) and day 72 (waited 1 day). We need a structure that gives us "all recent unresolved days" - that's a stack.
3. **Monotonic stack:** The stack holds indices of days still waiting for a warmer day. Their temperatures are in decreasing order (a day that's warmer than the one below it would have already resolved it). When a new temperature beats the top, pop and record.

## Worked Example

The stack holds indices of days whose "next warmer day" hasn't been found yet. The temperatures at those indices are always decreasing from bottom to top. When a new day is warmer than the top, it resolves that day and potentially several below it.

```
Input: [73, 74, 75, 71, 69, 72, 76, 73]
Result initialized to all zeros: [0, 0, 0, 0, 0, 0, 0, 0]

i=0 (73): Stack empty. Push 0.           Stack: [0(73)]
i=1 (74): 74 > 73. Pop 0. result[0]=1-0=1. Push 1.
                                          Stack: [1(74)]
i=2 (75): 75 > 74. Pop 1. result[1]=2-1=1. Push 2.
                                          Stack: [2(75)]
i=3 (71): 71 < 75. Push 3.               Stack: [2(75), 3(71)]
i=4 (69): 69 < 71. Push 4.               Stack: [2(75), 3(71), 4(69)]
i=5 (72): 72 > 69. Pop 4. result[4]=5-4=1.
          72 > 71. Pop 3. result[3]=5-3=2.
          72 < 75. Stop. Push 5.          Stack: [2(75), 5(72)]
i=6 (76): 76 > 72. Pop 5. result[5]=6-5=1.
          76 > 75. Pop 2. result[2]=6-2=4.
          Stack empty. Push 6.            Stack: [6(76)]
i=7 (73): 73 < 76. Push 7.               Stack: [6(76), 7(73)]

Remaining (indices 6, 7) stay 0 - no warmer day follows.
Result: [1, 1, 4, 2, 1, 1, 0, 0]

Total operations: 8 pushes + 6 pops = 14. Each index pushed once,
popped at most once. O(n).
```

## Approaches

### Approach 1: Brute Force

<details>
<summary>📝 Explanation</summary>

For each day i, scan forward from i+1 until you find a temperature higher than temperatures[i]. Record the distance. If you reach the end without finding one, the answer is 0.

**Time:** O(n²) - for each of n days, potentially scan up to n-1 future days.
**Space:** O(1) extra (besides the output array).

Simple and correct. State it first, then optimize.

</details>

### Approach 2: Monotonic Decreasing Stack

<details>
<summary>📝 Explanation</summary>

Maintain a stack of indices. The temperatures at these indices are in decreasing order from bottom to top (hence "monotonic decreasing"). This invariant is maintained by popping everything that the current temperature exceeds.

For each day i:
1. While the stack is non-empty and `temperatures[i] > temperatures[stack[-1]]`: pop the top index. The answer for that popped day is `i - popped_index`.
2. Push i onto the stack.

After processing all days, any indices remaining in the stack never found a warmer day (their answer stays 0 from initialization).

Why O(n): each index is pushed exactly once and popped at most once. The inner while loop across all iterations of the outer for loop executes at most n times total. So the total work is at most 2n operations.

**Time:** O(n) - each element pushed and popped at most once.
**Space:** O(n) - stack can hold up to n indices (all decreasing temperatures).

This is the standard monotonic stack pattern. The same structure solves "next greater element," "stock span" and "largest rectangle."

</details>

## Edge Cases

| Input | Expected | Why |
|---|---|---|
| `[50]` | `[0]` | Single day, nothing to compare |
| `[30, 60]` | `[1, 0]` | Two days, second is warmer |
| `[80, 70, 60]` | `[0, 0, 0]` | Decreasing - no warmer day exists |
| `[60, 60, 60]` | `[0, 0, 0]` | Same temp is NOT warmer (strictly greater) |
| `[60, 60, 80]` | `[2, 1, 0]` | Equal temps skip, 80 resolves both |

## Common Pitfalls

- **Using >= instead of > for the comparison:** Same temperature is NOT warmer. Must be strictly greater.
- **Storing temperatures instead of indices:** You need the index to compute the distance. Store indices, look up temperatures.
- **Forgetting that remaining stack items get 0:** They're already 0 from initialization. No extra cleanup needed.

## Interview Tips

> "This is a 'next greater element' problem. I'll use a monotonic decreasing stack of indices. When a warmer day arrives, it resolves all recent cooler days at once. Each element is pushed and popped at most once, so it's O(n) despite the nested loop."

**Key talking point:** Explaining the O(n) complexity of a nested loop is a strong signal. "The inner while loop doesn't restart from scratch each iteration. Across all outer iterations, the total pops equal the total pushes, which is n."

**What the interviewer evaluates:** The monotonic stack is a non-obvious choice. Explaining the O(n) amortized analysis (each element pushed once, popped once, total 2n operations despite nested loops) is the key differentiator. Candidates who can explain WHY this is O(n) demonstrate deeper algorithmic understanding than those who just implement it.

## DE Application

Time-series analysis: "for each data point, when does the metric next exceed this value?" Monitoring dashboards that show "time until next spike" for each measurement. The monotonic stack answers this in a single pass instead of scanning forward from each point.

## At Scale

The monotonic stack stores indices, not values: O(n) memory in the worst case (all decreasing temperatures). For 10M days, that's ~80MB of indices. The O(n) time guarantee (each element pushed and popped at most once) makes this efficient for very large time series. At scale, "next event exceeding a threshold" is a common monitoring query. The monotonic stack answers this in a single pass, but it requires the full sequence. For streaming time series, you can maintain a monotonic stack over a sliding window - new elements enter from the right, stale elements expire from the left. This gives you real-time "time until next spike" metrics.

## Related Problems

- [496. Next Greater Element I](https://leetcode.com/problems/next-greater-element-i/) - Simpler version
- [503. Next Greater Element II](https://leetcode.com/problems/next-greater-element-ii/) - Circular array
- [84. Largest Rectangle in Histogram](https://leetcode.com/problems/largest-rectangle-in-histogram/) - Monotonic increasing stack
