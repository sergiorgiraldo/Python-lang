# Container With Most Water (LeetCode #11)

🔗 [LeetCode 11: Container With Most Water](https://leetcode.com/problems/container-with-most-water/)

> **Difficulty:** Medium | **Interview Frequency:** Common

## Problem Statement

Given `n` non-negative integers where each represents a vertical line at position `i`, find two lines that form a container holding the most water.

**Example:**
```
Input: height = [1, 8, 6, 2, 5, 4, 8, 3, 7]
Output: 49
Explanation: Lines at indices 1 (height 8) and 8 (height 7)
             Width = 8 - 1 = 7, Height = min(8, 7) = 7
             Area = 7 × 7 = 49
```

**Constraints:**
- n >= 2
- 0 <= height[i] <= 10^4

---

## Thought Process

1. **Area = width × min(left_height, right_height)** - Width decreases as pointers move inward, so we need taller lines to compensate.
2. **Start with maximum width** - Pointers at opposite ends gives the widest possible container.
3. **Greedy choice: move the shorter line** - The water level is limited by the shorter line. Moving the taller line inward can only decrease width without any chance of increasing height (the shorter line still limits). Moving the shorter line might find a taller one.
4. **This greedy argument is the hard part to prove formally** but the intuition is solid and interviewers accept it.

---

## Worked Example

Two lines form a container. Water held = shorter line's height × distance between them. Start at both ends (max width). Move the shorter pointer inward each step because: the water level is limited by the shorter wall, and making the container narrower with the same bottleneck can only reduce the area. Moving the shorter wall *might* find a taller wall that compensates for the lost width.

```
Input: height = [3, 1, 6, 4, 5, 2, 8, 3, 7]
                 0  1  2  3  4  5  6  7  8

  left=0(3), right=8(7): area = min(3,7)×8 = 24. max=24. Left shorter → move left.
  left=1(1), right=8(7): area = min(1,7)×7 = 7.  max=24. Left shorter → move left.
  left=2(6), right=8(7): area = min(6,7)×6 = 36. max=36. Left shorter → move left.
  left=3(4), right=8(7): area = min(4,7)×5 = 20. max=36. Left shorter → move left.
  left=4(5), right=8(7): area = min(5,7)×4 = 20. max=36. Left shorter → move left.
  left=5(2), right=8(7): area = min(2,7)×3 = 6.  max=36. Left shorter → move left.
  left=6(8), right=8(7): area = min(8,7)×2 = 14. max=36. Right shorter → move right.
  left=6(8), right=7(3): area = min(8,3)×1 = 3.  max=36. Done.

  Answer: 36 (between index 2, height 6 and index 8, height 7).
  8 comparisons for 9 elements instead of 36 pairs.
```

---

## Approaches

### Approach 1: Brute Force

<details>
<summary>📝 Explanation</summary>

Check every pair of lines. For each pair (i, j), compute area = min(height[i], height[j]) × (j - i). Track the maximum across all pairs.

This examines n × (n-1) / 2 pairs. For the example with 9 elements, that's 36 pairs checked.

**Time:** O(n²) - all pairs. **Space:** O(1).

Valid starting point in an interview. State it, note the O(n²) cost, then explain how the greedy two-pointer approach eliminates configurations that provably can't improve the answer.

</details>

### Approach 2: Opposite-End Greedy (Optimal)

<details>
<summary>💡 Hint</summary>

Start at maximum width. Which pointer should you move - the one at the taller line or the shorter one? Why?

</details>

<details>
<summary>📝 Explanation</summary>

Start at both ends (maximum width). At each step, move the pointer at the shorter line.

Why: area = min(left_h, right_h) × width. The shorter line is the bottleneck. If we move the taller line inward, width decreases and the bottleneck stays the same (or gets worse). Area can only shrink. Moving the shorter line might find something taller that overcomes the lost width.

Every step eliminates a provably useless configuration. n-1 steps total.

**Time:** O(n) - one pass.
**Space:** O(1).

</details>

<details>
<summary>💻 Code</summary>

```python
def max_area(height: list[int]) -> int:
    left, right = 0, len(height) - 1
    best = 0
    while left < right:
        width = right - left
        h = min(height[left], height[right])
        best = max(best, width * h)
        if height[left] <= height[right]:
            left += 1
        else:
            right -= 1
    return best
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Two elements | `[1,1]` | `1` | Minimum valid input |
| Tall at ends | `[10,1,1,1,10]` | `40` | Wide and tall |
| Single tall spike | `[1,1,1,100,1,1,1]` | `6` | Tall spike doesn't help (needs two tall lines) |
| All same height | `[5,5,5,5]` | `15` | Maximum width wins |
| Ascending | `[1,2,3,4,5]` | `6` | Not at the ends |

---

## Common Pitfalls

1. **Confusing with Trapping Rain Water** - Container uses two lines, trapping rain fills between all bars. Different problems, similar-looking inputs.
2. **Moving the wrong pointer** - Always move the shorter one. Moving the taller one is provably suboptimal.
3. **Not handling equal heights** - When both heights are equal, it doesn't matter which pointer you move. Either direction works.

---

## Interview Tips

**What to say:**
> "I'll start with pointers at opposite ends for maximum width. The area is limited by the shorter line, so I'll always move the shorter pointer inward - moving the taller one can only make things worse since the width is shrinking and the height is still bounded by the shorter line."

**The greedy proof is the key talking point.** You don't need a formal proof, but you should articulate why moving the shorter line is the right choice. This shows algorithmic thinking, not just pattern matching.

**What the interviewer evaluates:** The greedy proof is what separates strong candidates. Saying "move the shorter pointer because..." tests whether you can reason about algorithm correctness, not just implement a pattern. An interviewer may ask you to prove why this works.

---

## DE Application

This optimization pattern shows up when:
- Finding optimal partition boundaries to maximize coverage while minimizing overlap
- Resource allocation problems (maximize throughput given constraints)
- The greedy "move the bottleneck" heuristic applies broadly in pipeline optimization

---

## At Scale

Two pointers scans n elements once: O(n) time, O(1) memory. Even at 1B elements, this completes in seconds and uses no extra memory. The greedy insight (move the shorter pointer inward) is provably optimal. This problem doesn't have a meaningful distributed equivalent because the two pointers must see the full array to make correct decisions. However, the "greedy narrowing" pattern appears in database query optimization: range scans that progressively narrow the search space based on constraints. At scale, the primary concern is data locality: sequential access through a sorted array is cache-friendly and I/O-efficient.

---

## Related Problems

- [42. Trapping Rain Water](042_trapping_rain_water.md) - Harder variant using similar two-pointer technique
- [167. Two Sum II](167_two_sum_ii.md) - Same opposite-ends structure, different optimization target
