# Last Stone Weight (LeetCode #1046)

🔗 [LeetCode 1046: Last Stone Weight](https://leetcode.com/problems/last-stone-weight/)

> **Difficulty:** Easy | **Interview Frequency:** Occasional

## Problem Statement

You have a collection of stones, each with a positive integer weight. Each round, pick the two heaviest stones and smash them. If they weigh the same, both are destroyed. Otherwise, the lighter one is destroyed and the heavier one's weight is reduced by the lighter stone's weight. Return the weight of the last remaining stone (or 0 if none remain).

**Example:**
```
Input: stones = [2, 7, 4, 1, 8, 1]

Round 1: smash 8 and 7 → 8-7 = 1 remains → [2, 4, 1, 1, 1]
Round 2: smash 4 and 2 → 4-2 = 2 remains → [2, 1, 1, 1]
Round 3: smash 2 and 1 → 2-1 = 1 remains → [1, 1, 1]
Round 4: smash 1 and 1 → destroyed       → [1]

Output: 1
```

**Constraints:**
- 1 <= stones.length <= 30
- 1 <= stones[i] <= 1000

---

## Thought Process

1. **Clarify** - We always pick the two heaviest. If equal, both gone. If different, remainder goes back.
2. **Brute force** - Sort, pop two largest, push remainder, repeat. O(n^2 log n) total.
3. **Key insight** - We repeatedly need the maximum. That's exactly what a max-heap does in O(log n). Pop two, push the remainder (if any).

---

## Worked Example

Repeatedly pick the two heaviest stones, smash them together, and if they're different weights, the remainder goes back. A max-heap (negate values for Python's min-heap) gives O(log n) access to the two heaviest stones at each step.

```
Input: stones = [2, 7, 4, 1, 8, 1]

  Max-heap (stored as negated): [-8, -7, -4, -2, -1, -1]
  (heap[0] = -8, so the heaviest stone is 8)

  Round 1: Pop two heaviest: 8 and 7. |8-7| = 1. Push 1 back.
    heap: [-4, -2, -1, -1, -1]

  Round 2: Pop 4 and 2. |4-2| = 2. Push 2.
    heap: [-2, -1, -1, -1]

  Round 3: Pop 2 and 1. |2-1| = 1. Push 1.
    heap: [-1, -1, -1]

  Round 4: Pop 1 and 1. |1-1| = 0. Both destroyed.
    heap: [-1]

  Only 1 stone left. Return 1.
```

---

## Approaches

### Approach 1: Sort Each Round (Brute Force)

<details>
<summary>💡 Hint</summary>

Sort the list, take the last two elements, process them, repeat.

</details>

<details>
<summary>📝 Explanation</summary>

Sort the stones, pop the two largest, compute the result, add it back if non-zero. Repeat until one or zero stones remain.

Each round: sort the entire list (O(n log n)), pop twice (O(1)), and potentially insert (O(1) append + re-sort next round).

**Time:** O(n² log n) - up to n rounds, each requiring an O(n log n) sort.
**Space:** O(1) extra (sorting in-place).

</details>

<details>
<summary>💻 Code</summary>

```python
def last_stone_weight_sort(stones: list[int]) -> int:
    while len(stones) > 1:
        stones.sort()
        first = stones.pop()
        second = stones.pop()
        if first != second:
            stones.append(first - second)
    return stones[0] if stones else 0
```

</details>

---

### Approach 2: Max-Heap (Optimal)

<details>
<summary>💡 Hint</summary>

You repeatedly need the maximum element. What data structure gives you the max in O(1) and lets you remove/insert in O(log n)?

</details>

<details>
<summary>📝 Explanation</summary>

Build a max-heap from the stones. Repeatedly pop the two largest, compute the difference, and push it back if non-zero. Stop when one or zero stones remain.

Python's heapq is a min-heap, so negate all values. Push `-stone` to simulate a max-heap. Pop gives the most negative value (= largest stone).

1. `heap = [-s for s in stones]`, then `heapify(heap)`.
2. While `len(heap) > 1`:
   - Pop twice: `first = -heappop(heap)`, `second = -heappop(heap)`.
   - If `first != second`: push `-(first - second)`.
3. Return `-heap[0]` if heap is non-empty, else 0.

**Time:** O(n log n) - up to n rounds, each doing O(log n) heap operations.
**Space:** O(n) - the heap.

Much better than re-sorting each round. The heap maintains the "who's heaviest?" property automatically as stones are removed and remainders added.

</details>

<details>
<summary>💻 Code</summary>

```python
import heapq

def last_stone_weight(stones: list[int]) -> int:
    heap = [-s for s in stones]
    heapq.heapify(heap)

    while len(heap) > 1:
        first = -heapq.heappop(heap)
        second = -heapq.heappop(heap)
        if first != second:
            heapq.heappush(heap, -(first - second))

    return -heap[0] if heap else 0
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Single stone | `[1]` | `1` | Nothing to smash |
| Two equal | `[3, 3]` | `0` | Both destroyed |
| Two unequal | `[3, 7]` | `4` | Basic difference |
| All equal (even) | `[5, 5, 5, 5]` | `0` | Pairs destroy each other |
| All equal (odd) | `[5, 5, 5]` | `5` | One survives |
| One dominant | `[100, 1, 1, 1]` | `97` | Large stone absorbs all |

---

## Common Pitfalls

1. **Forgetting to negate** - Python's heapq is a min-heap. Pushing raw values gives you the *lightest* stone, not the heaviest.
2. **Negating inconsistently** - Negate on push, negate on pop. If you forget one side, the logic breaks.
3. **Not handling the empty heap** - If all stones cancel out, the heap is empty. Return 0, not `heap[0]`.

---

## Interview Tips

**What to say:**
> "I need repeated access to the two largest elements. A max-heap gives me that in O(log n) per operation instead of O(n log n) for re-sorting. Python's heapq is a min-heap, so I'll negate the values."

**Common follow-ups:**
- "Can you avoid negation?" → You could use `heapq._heapify_max` but it's a private API and doesn't have a public `heappop` equivalent. Negation is the standard approach.
- "What if this were a min version?" → Use the heap directly without negation. Same logic but pop the two smallest.

**What the interviewer evaluates:** This is a straightforward heap simulation. The interviewer expects quick, clean execution. The real test is whether you reach for a max-heap naturally (Python requires negation for max-heap behavior) and handle the re-insertion logic correctly. Finishing fast opens time for harder problems.

---

## DE Application

The max-heap pattern shows up in priority-based processing:
- Processing high-priority tasks first in a job queue
- Selecting the most impactful items for batch processing
- Greedy algorithms where you repeatedly pick the largest/smallest available option

The negation trick is worth knowing because Python doesn't have a built-in max-heap. You'll use it whenever you need max-heap behavior in production Python code.

## At Scale

The max-heap simulation runs O(n log n) in total: n elements, each extracted and potentially re-inserted at O(log n). For n=10M, this takes a few seconds. Memory is O(n) for the heap. The simulation doesn't parallelize well because each step depends on the previous result. At scale, the interesting question is whether you need the exact final value or can approximate. For resource allocation problems (where stones represent competing demands), a greedy approximation may suffice. The interviewer may use this as a warm-up before harder heap problems.

---

## Related Problems

- [703. Kth Largest Element in a Stream](703_kth_largest_stream.md) - Min-heap for top-K tracking
- [215. Kth Largest Element in an Array](215_kth_largest_array.md) - One-shot selection problem
- [767. Reorganize String](767_reorganize_string.md) - Greedy with max-heap for scheduling
