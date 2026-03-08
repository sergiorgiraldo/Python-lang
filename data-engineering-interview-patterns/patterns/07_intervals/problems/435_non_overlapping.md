# Non-overlapping Intervals (LeetCode #435)

🔗 [LeetCode 435: Non-overlapping Intervals](https://leetcode.com/problems/non-overlapping-intervals/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

## Problem Statement

Given an array of intervals, return the minimum number of intervals you need to remove to make the rest non-overlapping.

**Example:**
```
Input: intervals = [[1,2],[2,3],[3,4],[1,3]]
Output: 1  (remove [1,3], then [1,2],[2,3],[3,4] don't overlap)
```

**Constraints:**
- 1 <= intervals.length <= 10^5
- intervals[i].length == 2

---

## Thought Process

1. **Reframe** - Minimum removals = total - maximum non-overlapping intervals we can keep.
2. **Greedy insight** - Sort by end time. Always keep the interval that ends earliest. This leaves the most room for future intervals.
3. **Why sort by end, not start?** - Sorting by start and keeping the shortest doesn't work because a short interval might conflict with more future intervals than one that ends earlier.

---

## Worked Example

Remove the fewest intervals to eliminate all overlaps. This is the classic "activity selection" problem. The greedy strategy: sort by end time, always keep the interval that ends earliest. This leaves maximum room for future intervals.

```
Input: intervals = [[1,4], [2,3], [3,6], [4,7], [6,8]]

Sort by end time: [[2,3], [1,4], [3,6], [4,7], [6,8]]

Greedy selection:
  Keep [2,3] (ends earliest). Last end = 3.
  [1,4]: starts at 1 < 3 → overlaps with [2,3]. REMOVE. count=1.
  [3,6]: starts at 3 ≥ 3 → no overlap. Keep. Last end = 6.
  [4,7]: starts at 4 < 6 → overlaps. REMOVE. count=2.
  [6,8]: starts at 6 ≥ 6 → no overlap. Keep. Last end = 8.

  Kept: [2,3], [3,6], [6,8]. Removed 2.

Why sort by end time? Keeping the earliest-ending interval maximizes
the remaining timeline for other intervals. Sorting by start time
doesn't work - [1,100] starts earliest but blocks everything.
```

---

## Approaches

### Approach 1: Sort by End Time (Optimal)

<details>
<summary>💡 Hint</summary>

The interval that ends earliest leaves the most room for everything else.

</details>

<details>
<summary>📝 Explanation</summary>

Classic activity selection: keep as many non-overlapping intervals as possible, which minimizes removals.

Sort by end time. Greedily keep each interval that doesn't overlap with the last kept interval (its start ≥ the last kept interval's end). Count the ones we skip.

Why sort by end time? The interval that ends earliest leaves the most room for future intervals. Sorting by start time doesn't work: [1,100] starts earliest but blocks everything after it.

**Time:** O(n log n) - sort dominates. The greedy scan is O(n).
**Space:** O(1) extra.

The answer (minimum removals) = total intervals - maximum non-overlapping intervals.

</details>

<details>
<summary>💻 Code</summary>

```python
def erase_overlap_intervals(intervals):
    if not intervals: return 0
    intervals.sort(key=lambda x: x[1])
    kept = 1
    last_end = intervals[0][1]
    for start, end in intervals[1:]:
        if start >= last_end:
            kept += 1
            last_end = end
    return len(intervals) - kept
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| No overlap | `[[1,2],[3,4]]` | `0` | Nothing to remove |
| All same | `[[1,5],[1,5],[1,5]]` | `2` | Keep one, remove rest |
| Nested | `[[1,100],[11,22],[33,44]]` | `1` | Remove the big one |
| Touching | `[[1,2],[2,3]]` | `0` | Not overlapping |

---

## Common Pitfalls

1. **Sorting by start instead of end** - Sorting by start is a different (also valid) approach but requires different comparison logic. The end-time greedy is simpler.
2. **Off-by-one: `>=` vs `>`** - Use `>=` because touching intervals ([1,2] and [2,3]) don't overlap.

---

## Interview Tips

**What to say:**
> "I'll sort by end time and greedily keep intervals that don't conflict. Minimum removals equals total minus maximum keepable."

**What the interviewer evaluates:** The greedy choice (sort by end time, keep earliest-ending interval) must be explained and justified. "Why end time, not start time?" tests proof intuition. The connection to activity selection and job scheduling shows you recognize the broader problem class.

---

## DE Application

This pattern applies to:
- Selecting non-overlapping maintenance windows
- Choosing non-conflicting batch job schedules
- Maximizing the number of non-overlapping data partition ranges

## At Scale

Sort by end time + greedy selection: O(n log n). Memory is O(1) extra (sort in-place, count removals). For 10M intervals, this takes ~3 seconds. The greedy approach (keep the interval that ends earliest) is provably optimal. At scale, "find the maximum non-overlapping set" is a resource scheduling problem: maximize utilization without conflicts. In job scheduling, this determines the maximum number of non-conflicting tasks. In data pipelines, this resolves write conflicts when multiple processes target the same time range. The greedy algorithm's simplicity makes it easy to implement in SQL using window functions: sort by end time, then filter rows where start >= previous selected end.

---

## Related Problems

- [252. Meeting Rooms](252_meeting_rooms.md) - Just check if any overlap (simpler)
- [56. Merge Intervals](056_merge_intervals.md) - Merge instead of remove
