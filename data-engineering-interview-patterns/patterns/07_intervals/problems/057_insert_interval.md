# Insert Interval (LeetCode #57)

🔗 [LeetCode 57: Insert Interval](https://leetcode.com/problems/insert-interval/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

## Problem Statement

Given a sorted list of non-overlapping intervals and a new interval, insert the new interval and merge if necessary. The result should remain sorted and non-overlapping.

**Example:**
```
Input: intervals = [[1,3],[6,9]], newInterval = [2,5]
Output: [[1,5],[6,9]]
```

**Constraints:**
- 0 <= intervals.length <= 10^4
- intervals is sorted by start and non-overlapping
- newInterval.length == 2

---

## Thought Process

1. **Input is already sorted** - No need to sort. Just find where the new interval fits.
2. **Three phases** - Before overlap, during overlap, after overlap. The "during" phase merges by expanding the new interval.
3. **O(n) scan** - Walk through once, handling each phase.

---

## Worked Example

Insert a new interval into a sorted non-overlapping list. Three phases: intervals entirely before the new one (no overlap), intervals that overlap with the new one (merge them all), intervals entirely after (no overlap).

```
Input: intervals = [[1,2], [3,5], [6,7], [8,10], [12,16]], newInterval = [4,8]

Phase 1 - Add intervals that end before newInterval starts (end < 4):
  [1,2]: end=2 < 4 → add to result. Result: [[1,2]]
  [3,5]: end=5 ≥ 4 → stop, this overlaps.

Phase 2 - Merge all overlapping intervals:
  [3,5] overlaps with [4,8] → merged = [min(3,4), max(5,8)] = [3,8]
  [6,7] overlaps with [3,8] (6 ≤ 8) → merged = [3, max(7,8)] = [3,8]
  [8,10] overlaps with [3,8] (8 ≤ 8) → merged = [3, max(8,10)] = [3,10]
  [12,16]: start=12 > 10 → no overlap. Stop merging.
  Add merged [3,10] to result. Result: [[1,2], [3,10]]

Phase 3 - Add remaining intervals:
  [12,16] → add. Result: [[1,2], [3,10], [12,16]]

One pass, O(n). The input was 5 intervals + 1 new, output is 3.
```

---

## Approaches

### Approach 1: Three-Phase Scan (Optimal)

<details>
<summary>📝 Explanation</summary>

Walk through the sorted intervals in three phases:
1. **Before:** Add all intervals that end before the new interval starts (no overlap).
2. **During:** Merge all intervals that overlap with the new interval. The merged interval's start is the min of all starts, end is the max of all ends.
3. **After:** Add all remaining intervals (they start after the merged interval ends).

The "during" phase handles 0 overlaps (the new interval fits in a gap) to n overlaps (the new interval spans the entire list).

**Time:** O(n) - single pass through the list. No sorting needed because the input is already sorted.
**Space:** O(n) - the result list.

</details>

<details>
<summary>💻 Code</summary>

```python
def insert(intervals, new_interval):
    result = []
    i, n = 0, len(intervals)
    while i < n and intervals[i][1] < new_interval[0]:
        result.append(intervals[i]); i += 1
    while i < n and intervals[i][0] <= new_interval[1]:
        new_interval = [min(new_interval[0], intervals[i][0]),
                        max(new_interval[1], intervals[i][1])]
        i += 1
    result.append(new_interval)
    while i < n:
        result.append(intervals[i]); i += 1
    return result
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Empty list | `[], [5,7]` | `[[5,7]]` | Insert into nothing |
| Before all | `[[3,5]], [1,2]` | `[[1,2],[3,5]]` | No overlap, insert at front |
| After all | `[[1,3]], [5,7]` | `[[1,3],[5,7]]` | No overlap, insert at end |
| Merge all | `[[1,3],[5,7]], [2,6]` | `[[1,7]]` | New interval bridges the gap |
| Touching | `[[1,3],[6,9]], [3,6]` | `[[1,9]]` | Boundary merge |

---

## Common Pitfalls

1. **Phase 2 boundary: `<=` not `<`** - If the new interval's end equals an existing interval's start, they overlap (touching).
2. **Forgetting to add the merged new interval** - After phase 2, the new interval (possibly expanded) must be appended before continuing to phase 3.

---

## Interview Tips

**What to say:**
> "The input is already sorted, so I don't need to sort. I'll scan in three phases: add intervals before the new one, merge overlapping intervals, then add the rest. O(n) time."

**What the interviewer evaluates:** The three-phase approach (before, overlap, after) tests clear decomposition. Getting the merge condition right (start <= existing_end AND end >= existing_start) is where bugs occur. Mentioning interval trees for the general case shows algorithmic breadth.

---

## DE Application

Insert interval represents incremental updates to range-based data:
- Inserting a new time partition into an existing set of partitions
- Adding a new maintenance window to a schedule
- Updating coverage ranges for data freshness tracking

## At Scale

Single-pass merge is O(n) for a sorted list. Binary search to find the insertion point makes it O(log n + merge cost). At scale, the real question is the data structure: a sorted list with O(n) insert/merge is fine for small interval sets but slow for large ones. An interval tree provides O(log n + k) query and O(log n) insert, where k is the number of overlapping intervals. Databases use B-tree indexes on interval endpoints to efficiently find overlapping ranges. In a streaming context, inserting intervals into a maintained sorted structure is the core of real-time session tracking and time-based windowing.

---

## Related Problems

- [56. Merge Intervals](056_merge_intervals.md) - Merge all overlapping (unsorted input)
- [252. Meeting Rooms](252_meeting_rooms.md) - Overlap detection
