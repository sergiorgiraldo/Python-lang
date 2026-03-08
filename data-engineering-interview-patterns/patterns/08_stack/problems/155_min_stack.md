# Min Stack (LeetCode #155)

🔗 [LeetCode 155: Min Stack](https://leetcode.com/problems/min-stack/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

## Problem Statement

Design a stack that supports push, pop, top and retrieving the minimum element, all in O(1) time.

## Thought Process

1. **The challenge:** A regular stack gives O(1) push/pop/top but finding the minimum requires scanning the entire stack (O(n)). We need to track the minimum as elements come and go.
2. **Key insight:** When we push a value, the minimum either changes (if the new value is smaller) or stays the same. When we pop, the minimum reverts to whatever it was before that push. This "snapshot" behavior is exactly what a stack captures.
3. **Two approaches:** Store the current minimum alongside each value (tuple approach), or maintain a separate stack that tracks only the minimums (two-stack approach).

## Worked Example

The core idea: every position in the stack has a "what's the minimum from here down?" answer. We record that answer at push time so we never have to recompute it. When we pop, the answer for the previous position is already recorded.

```
Tuple approach - each entry stores (value, min_so_far):

  push(-2): min = -2.          stack: [(-2, -2)]
  push(0):  min = min(0,-2)=-2. stack: [(-2,-2), (0,-2)]
  push(-3): min = min(-3,-2)=-3. stack: [(-2,-2), (0,-2), (-3,-3)]
  getMin(): stack[-1][1] = -3. ✓
  pop():    remove (-3,-3).     stack: [(-2,-2), (0,-2)]
  top():    stack[-1][0] = 0. ✓
  getMin(): stack[-1][1] = -2. ✓  (minimum "restored" automatically)

Two-stack approach - main stack + min stack:

  push(-2): stack=[-2], min_stack=[-2] (-2 <= nothing, push to min)
  push(0):  stack=[-2,0], min_stack=[-2] (0 > -2, don't push)
  push(-3): stack=[-2,0,-3], min_stack=[-2,-3] (-3 <= -2, push)
  getMin(): min_stack[-1] = -3. ✓
  pop():    pop -3 from stack. -3 == min_stack[-1] → pop min too.
            stack=[-2,0], min_stack=[-2]
  top():    stack[-1] = 0. ✓
  getMin(): min_stack[-1] = -2. ✓

Both approaches: all operations O(1). The tuple approach uses more
memory (every entry stores a min). The two-stack approach only stores
mins when they change, saving space when many consecutive values
are above the current minimum.
```

## Approaches

### Approach 1: Tuple Stack (Value + Min Pairs)

<details>
<summary>📝 Explanation</summary>

Store each entry as a tuple `(value, current_minimum)`. When pushing, the new minimum is `min(val, previous_minimum)`. When getting the minimum, just read the second element of the top tuple.

The insight: every stack position has a fixed "minimum from here down" that never changes once recorded. When we pop, the previous entry's minimum is automatically correct because it was calculated when *that* entry was pushed (before the now-popped entry existed).

**Time:** O(1) for all operations.
**Space:** O(n) - each entry stores two values.

Simpler to implement and reason about. The overhead is storing an extra integer per entry.

</details>

### Approach 2: Two Separate Stacks

<details>
<summary>📝 Explanation</summary>

Maintain a main stack for values and a separate min_stack that only tracks minimums. Push to min_stack when the new value is ≤ the current minimum. Pop from min_stack when the popped value equals the current minimum.

The `<=` (not `<`) is critical: if the same minimum value is pushed twice, the min_stack must record it twice. Otherwise popping one copy would incorrectly remove the minimum even though another copy remains.

**Time:** O(1) for all operations.
**Space:** O(n) worst case, but often less than the tuple approach if the minimum changes infrequently (e.g., pushing [1, 5, 8, 3, 7, 9] only adds 1 and 3 to min_stack).

</details>

## Edge Cases

| Scenario | Why It Matters |
|---|---|
| Duplicate minimums | `push(0), push(0), pop()` - min must still be 0 |
| All same values | Min never changes, but two-stack must still track correctly |
| Decreasing sequence | Every push changes the minimum |
| Single element | getMin after one push must work |

## Common Pitfalls

- **Two-stack: using `<` instead of `<=`:** Must push to min_stack when value equals the current min, not just when strictly less.
- **Forgetting empty checks:** getMin/top on an empty stack should be handled (problem guarantees valid calls, but good to note).

## Interview Tips

> "I need O(1) min retrieval, which means I can't scan the stack each time. I'll snapshot the minimum at each push by storing (value, current_min) tuples. Popping automatically restores the previous minimum."

**Follow-ups:**
- "Can you optimize space?" → Two-stack approach stores fewer mins.
- "What about a max stack?" → Same pattern, track max instead of min.
- "What if you also need O(1) median?" → Two heaps (pattern 05), not stacks.

**What the interviewer evaluates:** Combining two data structures (stack + min tracking) tests design thinking. The tuple approach is simpler; the two-stack approach optimizes space. Explaining WHY popping restores the correct minimum (the snapshot argument) shows understanding, not memorization.

## DE Application

Tracking running minimums or maximums in streaming data without rescanning. For example: "what's the lowest latency we've seen since the pipeline started?" Push each observation, and getMin tells you instantly. If you need to handle a sliding window, combine with a deque.

## At Scale

Each entry uses O(1) extra memory (the min snapshot). For n=10M elements, the tuple approach uses ~240MB (three values per entry: value, min, pointer). The two-stack approach uses less if the minimum changes infrequently. In production, the interesting application is maintaining running statistics over a data stream with O(1) query time. The trade-off: O(n) memory to maintain the history. If you only need the current min (not the ability to pop and restore), a single variable suffices with O(1) memory. The stack-based approach is specifically for "undo-able" minimum tracking.

## Related Problems

- [716. Max Stack](https://leetcode.com/problems/max-stack/) - Same idea with max
- [239. Sliding Window Maximum](https://leetcode.com/problems/sliding-window-maximum/) - Deque-based running max
