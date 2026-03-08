# Reorganize String (LeetCode #767)

🔗 [LeetCode 767: Reorganize String](https://leetcode.com/problems/reorganize-string/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

## Problem Statement

Given a string, rearrange the characters so that no two adjacent characters are the same. Return any valid rearrangement, or an empty string if impossible.

**Example:**
```
Input: s = "aab"
Output: "aba"

Input: s = "aaab"
Output: "" (impossible - 'a' appears 3 times in a 4-char string, would need adjacency)
```

**Constraints:**
- 1 <= s.length <= 500
- s consists of lowercase English letters

---

## Thought Process

1. **When is it impossible?** If any character appears more than ceil(n/2) times (i.e., more than (n+1)/2), there's no way to avoid placing it next to itself.
2. **Greedy approach** - Always place the most frequent character next. After placing it, the second most frequent becomes eligible. A max-heap tracks frequencies.
3. **Key trick** - After placing a character, don't immediately put it back in the heap. Hold it aside for one step so it can't be picked again on the next iteration.

---

## Worked Example

To avoid adjacent duplicates, always place the most frequent character next. A max-heap tracks character frequencies. At each step, pop the most frequent character, place it, decrement its count and push the previously popped character back (the one placed in the prior step). Holding one character back prevents placing the same character twice in a row.

```
Input: s = "aababcc"
Counts: a=3, b=2, c=2. Total=7.

Max-heap (negate for Python min-heap): [(-3,'a'), (-2,'b'), (-2,'c')]

  Step 1: pop (-3,'a') → place 'a'. prev=None. Result: "a"
          Hold 'a' (count now 2) for next step.
  Step 2: pop (-2,'b') → place 'b'. Push back prev ('a',2). Result: "ab"
          Heap: [(-2,'a'), (-2,'c')]. Hold 'b' (count 1).
  Step 3: pop (-2,'a') → place 'a'. Push back 'b' (1). Result: "aba"
          Heap: [(-1,'b'), (-2,'c')]. Hold 'a' (count 1).
  Step 4: pop (-2,'c') → place 'c'. Push back 'a' (1). Result: "abac"
          Heap: [(-1,'a'), (-1,'b')]. Hold 'c' (count 1).
  Step 5: pop (-1,'a') → place 'a'. Push back 'c' (1). Result: "abaca"
          Heap: [(-1,'c'), (-1,'b')]. Hold 'a' (count 0, don't push).
  Step 6: pop (-1,'b') → place 'b'. Push back nothing. Result: "abacab"
          Heap: [(-1,'c')]. Hold 'b' (count 0).
  Step 7: pop (-1,'c') → place 'c'. Result: "abacabc"
          Heap empty. Done.

No adjacent duplicates. The greedy choice (most frequent first) works
because it spreads the most common character as widely as possible.
If any character count > (n+1)/2, it's impossible.
```

---

## Approaches

### Approach 1: Greedy with Max-Heap

<details>
<summary>💡 Hint</summary>

Always pick the most frequent remaining character. Hold it back for one round to prevent adjacency.

</details>

<details>
<summary>📝 Explanation</summary>

Use a max-heap (negate counts for Python's min-heap) to always place the most frequent remaining character. The trick: after placing a character, don't push it back immediately. Hold it for one round and push it back at the *next* step. This prevents placing the same character consecutively.

1. Count character frequencies with Counter.
2. Build a max-heap of (-count, char) pairs.
3. Track the previously placed character. At each step: pop the most frequent, place it, push the previous character back (if its count > 0), save current as previous.
4. If the heap is empty but we haven't placed all characters, return "" (impossible).

The arrangement is impossible when any single character appears more than ⌈n/2⌉ times (there aren't enough "spacer" positions between its occurrences).

**Time:** O(n log k) where k is the number of unique characters (at most 26 for lowercase letters, so effectively O(n)).
**Space:** O(k) for the heap.

</details>

<details>
<summary>💻 Code</summary>

```python
import heapq
from collections import Counter

def reorganize_string(s: str) -> str:
    counts = Counter(s)
    if max(counts.values()) > (len(s) + 1) // 2:
        return ""

    heap = [(-count, char) for char, count in counts.items()]
    heapq.heapify(heap)

    result = []
    prev_count, prev_char = 0, ""

    while heap:
        count, char = heapq.heappop(heap)
        result.append(char)
        if prev_count < 0:
            heapq.heappush(heap, (prev_count, prev_char))
        prev_count = count + 1
        prev_char = char

    return "".join(result)
```

</details>

---

### Approach 2: Sort and Interleave

<details>
<summary>📝 Explanation</summary>

Sort by frequency. Place the most frequent characters at even indices (0, 2, 4...) and the rest at odd indices (1, 3, 5...). This guarantees no adjacent duplicates if a valid arrangement exists.

**Time:** O(n log n) for sorting (or O(n) if using counting sort for bounded alphabet).
**Space:** O(n) - the result array.

Simpler to implement than the heap approach but less intuitive for variable-length strings.

</details>

<details>
<summary>💻 Code</summary>

```python
from collections import Counter

def reorganize_string_interleave(s: str) -> str:
    counts = Counter(s)
    if max(counts.values()) > (len(s) + 1) // 2:
        return ""

    sorted_chars = sorted(counts.keys(), key=lambda c: -counts[c])
    chars = []
    for c in sorted_chars:
        chars.extend([c] * counts[c])

    result = [""] * len(s)
    idx = 0
    for char in chars:
        result[idx] = char
        idx += 2
        if idx >= len(s):
            idx = 1
    return "".join(result)
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Possible | `"aab"` | `"aba"` or similar | Basic case |
| Impossible | `"aaab"` | `""` | Frequency exceeds limit |
| Single char | `"a"` | `"a"` | Trivially valid |
| Two same | `"aa"` | `""` | Can't avoid adjacency |
| All unique | `"abc"` | Any permutation | All valid |
| Balanced | `"aabb"` | `"abab"` or similar | Multiple valid answers |

---

## Common Pitfalls

1. **Forgetting the impossibility check** - Always check `max_count > (n+1)//2` before trying to build a result.
2. **Pushing back immediately** - If you push a character back onto the heap right after popping it, you might pop the same character again on the next step, creating adjacent duplicates.
3. **Off-by-one in max count check** - For a string of length 5, the max allowed frequency is 3 (positions 0, 2, 4). That's `(5+1)//2 = 3`. Getting this wrong means rejecting valid inputs or accepting invalid ones.

---

## Interview Tips

**What to say:**
> "First I'll check if it's even possible - if any character appears more than ceil(n/2) times, we can't avoid adjacency. Then I'll use a max-heap to always place the most frequent character, holding each character back for one step to prevent repeats."

**Common follow-ups:**
- "Can you prove the greedy approach is correct?" → At each step, placing the most frequent character leaves the most balanced remaining distribution. If the impossibility check passes, the greedy approach always succeeds.
- "What about k distant apart instead of just adjacent?" → Similar approach but hold back k-1 characters instead of 1. Use a queue of size k-1 alongside the heap.

**What the interviewer evaluates:** The greedy insight (place most frequent first) combined with the "hold back" trick tests whether you can manage state across heap operations. Getting the impossibility check right (max count > ceil(n/2)) tests edge case reasoning. The follow-up about k-distance generalization tests whether you can extend patterns. Connecting to Task Scheduler (621) shows you recognize the same pattern across problems.

---

## DE Application

The greedy + priority queue pattern shows up in:
- Task scheduling: process the highest-priority task first, with cooldown between same-type tasks
- Load balancing: distribute work to the least loaded worker
- Rate limiting: spread requests across time to avoid bursts from a single source
- Data distribution: spread hot keys across partitions to avoid skew

The "hold back and re-add" technique is particularly useful for scheduling problems where you need a gap between repeated operations.

## At Scale

The heap holds at most 26 entries (one per lowercase letter): O(1) memory regardless of string length. For a 1B-character string, the counting phase (O(n)) dominates. The heap operations are O(n log 26) = O(n). At scale, the rearrangement pattern appears in job scheduling: distribute tasks so that no two tasks of the same type run consecutively. In Airflow, task scheduling with cooldown constraints uses a similar greedy approach. In data pipelines, this maps to spreading write operations across partitions to avoid hotspots. The impossibility check (max frequency > ceil(n/2)) translates to capacity planning: "do we have enough slots to schedule all tasks with the required spacing?"

---

## Related Problems

- [1046. Last Stone Weight](1046_last_stone_weight.md) - Greedy with max-heap (simpler version)
- [23. Merge K Sorted Lists](023_merge_k_sorted.md) - Different heap usage (merge instead of schedule)
- [347. Top K Frequent Elements](../../01_hash_map/problems/347_top_k_frequent.md) - Frequency counting + selection
