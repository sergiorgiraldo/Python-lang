# Sliding Window Pattern

## What Is It?

### The basics

A sliding window is a technique for processing subarrays or substrings by maintaining a "window" (a contiguous range) that slides across the data. Instead of recomputing everything for every possible subarray (O(n²) or worse), the window moves one step at a time, adding a new element on one end and removing an old element from the other. This incremental update keeps the total work at O(n).

Think of it like looking through a train window. As the train moves forward, new scenery appears on the right side while old scenery disappears on the left. You don't need to re-examine everything in view - you just process what's new and forget what's gone.

### The two types

**1. Fixed-size window**

The window has a predetermined size k. It slides one position at a time, always containing exactly k elements.

```python
# fixed window of size k
window_sum = sum(arr[:k])  # initialize with first k elements
for i in range(k, len(arr)):
    window_sum += arr[i]       # add new element entering the window
    window_sum -= arr[i - k]   # remove element leaving the window
    # process window_sum
```

The key operation: when the window slides right by one position, we add one element and remove one element. Each slide costs O(1) instead of re-summing all k elements.

Use this when: the problem says "subarray of size k" or "window of length k." Maximum average subarray, Contains Duplicate II.

**2. Variable-size window**

The window expands and contracts based on some condition. A right pointer extends the window, and a left pointer shrinks it when a constraint is violated.

```python
left = 0
for right in range(len(arr)):
    # expand: add arr[right] to window state
    while window_violates_constraint():
        # contract: remove arr[left] from window state
        left += 1
    # process current valid window [left..right]
```

The right pointer always moves forward (expands). The left pointer only moves forward (contracts). Since both pointers only move in one direction and each visits at most n positions, the total work is O(n) despite the nested loop.

Use this when: "longest substring/subarray that satisfies..." or "smallest window that contains..." Longest Substring Without Repeating Characters, Longest Repeating Character Replacement.

### Why it's O(n) with a nested loop

The variable-size window has an inner while loop, which looks like it could be O(n²). But consider: the left pointer starts at 0 and can only move forward to at most n-1. Each iteration of the inner loop advances left by 1. Across ALL iterations of the outer loop, left moves at most n times total. So the inner loop doesn't run n times per outer iteration - it runs n times *total* across the entire algorithm.

Think of it this way: each element enters the window once (when right passes over it) and leaves the window once (when left passes over it). That's at most 2n operations total = O(n).

### Tracking window state with a hash map

Most sliding window problems track what's inside the window using a hash map (dict or Counter). When an element enters the window, update the map. When an element leaves, update the map again.

```python
from collections import defaultdict
counts = defaultdict(int)

left = 0
for right in range(len(s)):
    counts[s[right]] += 1       # element enters window
    while window_invalid():
        counts[s[left]] -= 1    # element leaves window
        if counts[s[left]] == 0:
            del counts[s[left]]  # clean up zero-count entries
        left += 1
```

This combination of sliding window + hash map is one of the most common patterns in interviews. The window handles the "contiguous subarray" constraint. The hash map handles the "what's in the window?" tracking.

### Connection to data engineering

Sliding windows are everywhere in data engineering:
- **Moving averages** - compute the average of the last k data points as new data arrives
- **Sessionization** - group events into sessions based on time gaps (variable window)
- **Anomaly detection** - flag values that deviate from a sliding window of recent values
- **Rate limiting** - count requests within a sliding time window
- **Stream processing** - Spark Streaming and Flink both have native sliding window operations

The SQL equivalent is window functions: `AVG(value) OVER (ORDER BY ts ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)` is a fixed-size sliding window.

## When to Use It

**Recognition signals:**
- "Find the longest/shortest subarray/substring that..."
- "Maximum/minimum sum of size k"
- "Subarray with at most K distinct elements"
- "Find all anagrams/permutations in a string"
- Any problem about contiguous sequences with constraints

**Two types:**
- **Fixed-size window** - Window size is given (k). Slide it across the data. Used for moving averages, rolling sums, pattern matching of known length.
- **Variable-size window** - Window grows and shrinks to satisfy a condition. Find the longest/shortest subarray meeting some criteria.

## Visual Aid

```
Fixed-size window: Maximum sum of 3 consecutive elements

Array: [2, 1, 5, 1, 3, 2, 8, 4]

Window [2, 1, 5] → sum=8
       [1, 5, 1] → sum=7  (added 1, removed 2: 8+1-2=7)
          [5, 1, 3] → sum=9  (added 3, removed 1: 7+3-1=9)
             [1, 3, 2] → sum=6
                [3, 2, 8] → sum=13  ← maximum
                   [2, 8, 4] → sum=14  ← new maximum

Each slide: add one element, remove one element. O(1) per slide.
Total: O(n) for the entire array. Without the window: O(n×k) re-summing.
```

```
Variable-size window: Longest substring without repeating characters

String: "abcdbefa"

  a         → {a} valid, length 1
  ab        → {a,b} valid, length 2
  abc       → {a,b,c} valid, length 3
  abcd      → {a,b,c,d} valid, length 4
  abcdb     → {a,b,c,d,b} duplicate 'b'! Contract from left:
   bcdb     → still has duplicate 'b'. Contract:
    cdb     → {c,d,b} valid, length 3
    cdbe    → {c,d,b,e} valid, length 4
    cdbef   → {c,d,b,e,f} valid, length 5  ← longest
    cdbefa  → duplicate 'a'? No, first 'a' was removed.
     Wait: {c,d,b,e,f,a} valid, length 6  ← new longest

Right pointer always advances. Left pointer only advances to fix violations.
Total movement of both pointers combined: O(n).
```

## The Two Templates

### Fixed-Size Window

```python
def fixed_window(arr, k):
    # Initialize: compute the first window
    window_value = compute(arr[:k])
    best = window_value

    # Slide: add new element, remove old element
    for i in range(k, len(arr)):
        window_value = update(window_value, arr[i], arr[i - k])
        best = better(best, window_value)

    return best
```

### Variable-Size Window

```python
def variable_window(arr):
    left = 0
    best = 0
    state = {}  # Track what's in the window

    for right in range(len(arr)):
        # Expand: add arr[right] to state
        add_to_state(state, arr[right])

        # Contract: shrink from left while constraint is violated
        while constraint_violated(state):
            remove_from_state(state, arr[left])
            left += 1

        # Update answer
        best = max(best, right - left + 1)

    return best
```

**The variable-size template is worth memorizing.** Almost every medium/hard sliding window problem follows this exact structure. The only things that change are the state tracking and the constraint check.

## Why O(n) and Not O(n * k)?

The brute force approach recomputes the entire window from scratch for each position. For a fixed window of size k sliding across n elements, that's O(n * k).

The sliding window approach maintains a running computation. Each element enters the window once and exits once. Total work across all slides: O(n).

For variable windows, the key insight is that `left` only moves forward. Even though there's a while loop inside the for loop, `left` moves at most n total steps across all iterations of the outer loop. So the total work is O(n), not O(n^2).

## Time/Space Complexity

| Variant | Time | Space |
|---------|------|-------|
| Fixed window (sum/average) | O(n) | O(1) |
| Fixed window (with hash map) | O(n) | O(k) |
| Variable window | O(n) | O(min(n, alphabet)) |
| Sliding window maximum (deque) | O(n) | O(k) |

## Trade-offs

**Sliding window gives O(n) time for contiguous subarray/substring problems.** Without it, checking every subarray is O(n²) (or O(n²k) if you re-compute for each). The window's incremental update avoids redundant work.

**When sliding window works:**
- The problem asks about contiguous subarrays or substrings (not subsequences)
- You can define a clear condition for when the window is valid/invalid
- Adding and removing elements from the window state is O(1)

**When sliding window doesn't work:**
- The problem asks about subsequences (elements don't need to be contiguous)
- The valid/invalid condition can't be maintained incrementally (e.g., you need to re-examine all elements to decide)
- The data isn't sequential (graphs, trees, etc.)

**Sliding window vs two pointers:** There's significant overlap. A variable-size sliding window IS a two-pointer technique (left and right pointers moving forward). The distinction: "sliding window" emphasizes tracking state inside the window (usually with a hash map). "Two pointers" emphasizes the pointer movement logic. Same mechanics, different emphasis.

### Scale characteristics

Sliding window algorithms process each element exactly once (or twice: once entering, once leaving). This makes them inherently streaming-friendly: you don't need the full dataset in memory, just the current window state.

| Window type | Memory usage | Input size dependency |
|---|---|---|
| Fixed-size window (k) | O(k) | Independent of n |
| Variable window with hash map | O(unique elements in window) | Usually << n |
| Variable window with deque (max/min) | O(k) worst case | Bounded by window size |

**Streaming context:** Sliding windows map directly to stream processing frameworks. Kafka Streams, Flink and Spark Structured Streaming all have first-class window operations: tumbling (non-overlapping), sliding (overlapping) and session (gap-based) windows. The window state is maintained incrementally - exactly like the algorithmic pattern.

**Memory concern at scale:** The window state is usually small (O(k) or O(alphabet)). The risk is when the window itself is large. A 30-day sliding window over events at 1M events/day means the window holds 30M events. If you need all events in the window (not just aggregates), that's ~2.4GB. Incremental aggregation (maintain running sum, subtract exiting elements) avoids storing individual events.

### SQL equivalent

Window functions in SQL (`OVER (ORDER BY ... ROWS BETWEEN ...)`) implement the sliding window pattern. `SUM(amount) OVER (ORDER BY date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW)` is a 30-day rolling sum. The SQL engine maintains the window state internally. For large windows, the engine may need to materialize the window frame, so performance depends on window size. The SQL section's window functions subsection covers these patterns in depth.

## Problems

| # | Problem | Difficulty | Key Concept |
|---|---------|------------|-------------|
| [643](https://leetcode.com/problems/maximum-average-subarray-i/) | [Maximum Average Subarray I](problems/643_max_average_subarray.md) | Easy | Fixed window basics |
| [219](https://leetcode.com/problems/contains-duplicate-ii/) | [Contains Duplicate II](problems/219_contains_duplicate_ii.md) | Easy | Fixed window + hash set |
| [3](https://leetcode.com/problems/longest-substring-without-repeating-characters/) | [Longest Substring Without Repeating](problems/003_longest_substring.md) | Medium | Variable window classic |
| [424](https://leetcode.com/problems/longest-repeating-character-replacement/) | [Longest Repeating Character Replacement](problems/424_longest_repeating_char.md) | Medium | Variable window with constraint |
| [567](https://leetcode.com/problems/permutation-in-string/) | [Permutation in String](problems/567_permutation_in_string.md) | Medium | Fixed window + frequency match |
| [438](https://leetcode.com/problems/find-all-anagrams-in-a-string/) | [Find All Anagrams](problems/438_find_all_anagrams.md) | Medium | Fixed window + frequency match (all positions) |
| [239](https://leetcode.com/problems/sliding-window-maximum/) | [Sliding Window Maximum](problems/239_sliding_window_max.md) | Hard | Monotonic deque |
| [76](https://leetcode.com/problems/minimum-window-substring/) | [Minimum Window Substring](problems/076_min_window_substring.md) | Hard | Variable window + frequency tracking |

**Suggested order:** 643 → 219 → 3 → 424 → 567, 438 → 239 → 76

## DE Scenarios

| Scenario | Description | Connection |
|----------|-------------|------------|
| [Moving Averages](de_scenarios/moving_averages.md) | Rolling statistics on time-series data | Fixed window |
| [Sessionization](de_scenarios/sessionization.md) | Group events into sessions by time gap | Variable window |
| [Anomaly Detection](de_scenarios/anomaly_detection.md) | Detect values outside rolling bounds | Fixed window + statistics |
| [Rate Limiting](de_scenarios/rate_limiting.md) | Check request rates within time windows | Fixed window + counting |

## Interview Tips

**What to say when you see "subarray" or "substring":**
> "This involves contiguous elements, so I'm thinking sliding window. Let me figure out if it's a fixed-size or variable-size window."

**Fixed vs variable - how to tell:**
> "If the window size is given or implied by the problem, it's fixed. If I need to find the longest or shortest subarray that meets a condition, it's variable."

**On the O(n) argument:**
> "Even though there's a nested loop in the variable window template, the inner pointer only moves forward. Each element enters and exits the window at most once, so total work is O(n)."

Interviewers often ask about the time complexity of the variable window. Being able to explain why the nested loops are still O(n) shows understanding.

**What the interviewer evaluates across sliding window problems:**

- **643 (Max Average):** This is a warm-up. Clean O(n) with O(1) space is expected quickly. The interviewer is testing whether you know the fixed-size sliding window template. Finishing fast earns time for harder follow-ups.
- **219 (Contains Duplicate II):** Combining a sliding window with a hash set tests whether you can compose patterns. The window maintains the distance constraint, the set maintains the uniqueness check. Mentioning streaming dedup shows you've internalized the production application.
- **3 (Longest Substring):** Variable-size windows are harder than fixed-size. The expand/shrink logic tests your ability to manage two pointers with a state invariant. Getting the shrink condition right (when to move left) is where most candidates struggle. A clean implementation with clear variable names is a strong signal.
- **424 (Longest Repeating Replacement):** The "replacements budget" concept makes the window condition non-trivial. You need to realize that the window is valid when (window size - max frequency) <= k. The insight that max_freq doesn't need to decrease when the window shrinks is the optimization that impresses.
- **567 (Permutation in String):** The "matches" counter optimization (comparing one character at a time instead of full arrays) tests whether you think about unnecessary work. A candidate who compares 26-element arrays every step gets O(26n) = O(n), but the constant factor matters for very large inputs. The optimization to O(1) per step shows attention to practical performance.
- **438 (Find Anagrams):** Nearly identical to 567. If asked both in sequence, the interviewer tests whether you can adapt your solution (return list instead of boolean) without starting over. Reusing your sliding window template with a minor output change is the right move.
- **239 (Sliding Window Maximum):** The monotonic deque is a non-obvious data structure choice. This tests whether you know data structures beyond arrays and hash maps. Explaining WHY the deque maintains a decreasing order (because elements that are both older and smaller can never be the maximum) is the key insight. This problem is frequently used for senior+ interviews.
- **76 (Min Window Substring):** This is a hard problem combining variable windows with character frequency tracking. The "have" counter optimization (tracking how many unique characters are satisfied) avoids O(26) comparisons per step. This tests both pattern knowledge and implementation precision. At principal level, discussing the streaming application and comparing to SQL approaches shows breadth.

## Related Patterns

- **[Hash Map](../01_hash_map/)** - Often used inside sliding windows for frequency counting. Problems like "longest substring with at most K distinct characters" combine both patterns.
- **[Two Pointers](../02_two_pointers/)** - Similar concept (two indices moving through data) but two pointers typically works on sorted data while sliding windows work on sequential/unsorted data.
- **Heap** (patterns/05_heap_priority_queue/) - The monotonic deque in Sliding Window Maximum is related to priority queue concepts.

## What's Next

**Next pattern:** [Heap / Priority Queue](../05_heap_priority_queue/) - when you need the top-K or need to merge sorted streams, heaps are the tool.

**See also:**
- [Sliding Window vs Recompute Benchmark](../../benchmarks/sliding_window_vs_recompute.py) - O(n) vs O(n*k) for moving averages
- [Pattern Recognition Cheat Sheet](../../docs/PATTERN_RECOGNITION.md) - quick reference for identifying which pattern fits
- [Time Complexity Reference](../../docs/TIME_COMPLEXITY_CHEATSHEET.md) - Big-O comparison card
