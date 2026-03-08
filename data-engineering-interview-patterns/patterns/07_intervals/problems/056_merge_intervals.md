# Merge Intervals (LeetCode #56)

🔗 [LeetCode 56: Merge Intervals](https://leetcode.com/problems/merge-intervals/)

> **Difficulty:** Medium | **Interview Frequency:** Very Common

## Problem Statement

Given an array of intervals where `intervals[i] = [start, end]`, merge all overlapping intervals and return an array of non-overlapping intervals that cover all the ranges.

**Example:**
```
Input: intervals = [[1,3],[2,6],[8,10],[15,18]]
Output: [[1,6],[8,10],[15,18]]
Explanation: [1,3] and [2,6] overlap, merge into [1,6].
```

**Constraints:**
- 1 <= intervals.length <= 10^4
- intervals[i].length == 2
- 0 <= start <= end <= 10^4

---

## Thought Process

1. **Clarify** - Do touching intervals ([1,3] and [3,5]) merge? (Yes, they share the point 3.)
2. **Key insight** - Sort by start time. Then overlapping intervals are adjacent. Scan left to right, extending the current interval or starting a new one.
3. **Two conditions per interval** - If it overlaps with the previous merged interval, extend. If not, append.

---

## Worked Example

Combine overlapping intervals into the smallest set of non-overlapping intervals. Sort by start, then walk through. If the current interval overlaps with the last result, extend the result's end. Otherwise start a new result.

```
Input: intervals = [[1,3], [8,10], [2,6], [15,18], [5,7]]

Sort by start: [[1,3], [2,6], [5,7], [8,10], [15,18]]

  Start with result = [[1,3]]

  [2,6]: does 2 ≤ 3 (last result's end)? Yes → overlap.
    Extend: result[-1] = [1, max(3,6)] = [1,6]. Result: [[1,6]]

  [5,7]: does 5 ≤ 6? Yes → overlap.
    Extend: result[-1] = [1, max(6,7)] = [1,7]. Result: [[1,7]]

  [8,10]: does 8 ≤ 7? No → no overlap. Append.
    Result: [[1,7], [8,10]]

  [15,18]: does 15 ≤ 10? No → append.
    Result: [[1,7], [8,10], [15,18]]

5 intervals merged to 3. One pass after sorting.
Note: [1,3] and [5,7] don't overlap directly, but [2,6] bridges them.
Sorting ensures we catch these transitive overlaps.
```

---

## Approaches

### Approach 1: Brute Force (Repeated Pairwise Merge)

<details>
<summary>📝 Explanation</summary>

Repeatedly scan through all intervals looking for overlapping pairs. When two intervals overlap, merge them into one and restart the scan. Continue until a full pass finds no more overlaps.

Each pass is O(n) and might reduce the count by one. In the worst case (a chain of overlapping intervals), this requires O(n) passes, each scanning O(n) intervals.

**Time:** O(n^2) worst case - O(n) passes of O(n) each.
**Space:** O(n) - working copy of intervals.

</details>

<details>
<summary>💻 Code</summary>

```python
def merge_brute(intervals):
    if not intervals: return []
    result = [iv[:] for iv in intervals]
    changed = True
    while changed:
        changed = False
        new_result = []
        used = [False] * len(result)
        for i in range(len(result)):
            if used[i]: continue
            current = result[i][:]
            for j in range(i + 1, len(result)):
                if used[j]: continue
                if current[0] <= result[j][1] and result[j][0] <= current[1]:
                    current = [min(current[0], result[j][0]), max(current[1], result[j][1])]
                    used[j] = True
                    changed = True
            new_result.append(current)
        result = new_result
    return sorted(result, key=lambda x: x[0])
```

</details>

---

### Approach 2: Sort and Scan (Optimal)

<details>
<summary>💡 Hint</summary>

After sorting by start, overlapping intervals are adjacent. You only need one pass.

</details>

<details>
<summary>📝 Explanation</summary>

Sort by start time. Walk through the sorted intervals with a result list:
1. Add the first interval to the result.
2. For each subsequent interval:
   - If it overlaps with the last result (its start ≤ the last result's end), extend the last result's end to `max(last_end, current_end)`.
   - If it doesn't overlap, append it as a new entry.

The "extend" step handles both partial overlaps ([1,5] and [3,7] → [1,7]) and containment ([1,10] and [3,5] → [1,10], since max(10,5)=10).

**Time:** O(n log n) - sorting. The merge scan is O(n).
**Space:** O(n) - the result list.

This is the standard approach. There's no faster general solution because determining if intervals overlap requires sorting-level work.

</details>

<details>
<summary>💻 Code</summary>

```python
def merge(intervals):
    if not intervals: return []
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0][:]]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Empty | `[]` | `[]` | Guard clause |
| Single | `[[1, 5]]` | `[[1, 5]]` | Nothing to merge |
| No overlap | `[[1,2],[4,5],[7,8]]` | `[[1,2],[4,5],[7,8]]` | All separate |
| Full overlap | `[[1,10],[2,5],[3,7]]` | `[[1,10]]` | Everything merges |
| Touching | `[[1,3],[3,5]]` | `[[1,5]]` | Shared endpoint merges |
| Contained | `[[1,10],[3,5]]` | `[[1,10]]` | Small inside large |
| Chain | `[[1,3],[2,5],[4,7],[6,9]]` | `[[1,9]]` | Progressive merging |

---

## Common Pitfalls

1. **Not copying intervals** - `merged.append(intervals[i])` shares a reference. If you later modify `merged[-1][1]`, you modify the original. Use `intervals[i][:]` or `[start, end]`.
2. **Forgetting `max()` on end** - When merging, the end should be `max(merged[-1][1], end)`, not just `end`. The current interval's end might be smaller (contained interval).
3. **Not handling touching intervals** - `[1,3]` and `[3,5]` should merge. Use `<=` not `<` for the overlap check.

---

## Interview Tips

**What to say:**
> "Sort by start time, then one pass comparing each interval with the last merged one. If they overlap, extend. If not, append. O(n log n) overall."

**Common follow-ups:**
- "What if intervals arrive in a stream?" → You can't sort a stream. Use an interval tree or process in windows.
- "Can you do it in O(n)?" → Only if the input is already sorted. The sort is the bottleneck.

**What the interviewer evaluates:** Sort + merge is the expected approach. Edge cases (touching intervals [1,2] and [2,3] - do they merge?) test attention to detail. The real differentiator is discussing why this is hard in SQL and how partitioning by entity key avoids cross-partition issues.

---

## DE Application

Merge intervals is one of the most directly applicable DE patterns:
- **Session stitching:** Merge overlapping event timestamps into sessions
- **Partition deduplication:** Merge overlapping date ranges to find unique coverage
- **SLA calculation:** Merge outage windows to calculate total downtime
- **Time-series compaction:** Merge adjacent time ranges with the same value

In SQL, this is a gaps-and-islands problem. In Python, the sort-and-scan approach above is the standard solution.

See: [Session Stitching DE Scenario](../de_scenarios/session_stitching.md)

## At Scale

Sort + merge: O(n log n) time, O(n) space for the output. For 10M intervals, this takes ~3 seconds. The merge pass is cache-friendly (sequential access). At scale, merging intervals is a common ETL operation: "consolidate overlapping time ranges for the same user." In SQL, this is surprisingly hard to do efficiently - it typically requires recursive CTEs or window functions with careful gap detection. Spark handles it as: sort by key + start time within each partition, then merge sequentially. Cross-partition intervals (spanning partition boundaries) require a second pass. In practice, partitioning by the entity key (user_id, device_id) ensures that all intervals for one entity land on the same partition, eliminating the boundary problem.

---

## Related Problems

- [252. Meeting Rooms](252_meeting_rooms.md) - Detect overlaps (simpler version)
- [57. Insert Interval](057_insert_interval.md) - Insert one new interval and merge
- [253. Meeting Rooms II](253_meeting_rooms_ii.md) - Count concurrent overlaps
