# Meeting Rooms (LeetCode #252)

🔗 [LeetCode 252: Meeting Rooms](https://leetcode.com/problems/meeting-rooms/)

> **Difficulty:** Easy | **Interview Frequency:** Occasional

*This is a LeetCode Premium problem. The problem description below is written in our own words. If you have LeetCode Premium, the original is at https://leetcode.com/problems/meeting-rooms/.*

## Problem Statement

Given a list of meeting time intervals where `intervals[i] = [start, end]`, determine if a person can attend all meetings (i.e., no two meetings overlap).

**Example:**
```
Input: intervals = [[0, 30], [5, 10], [15, 20]]
Output: false  (the first meeting overlaps with the second)

Input: intervals = [[7, 10], [2, 4]]
Output: true  (no overlap)
```

**Constraints:**
- 0 <= intervals.length <= 10^4
- intervals[i].length == 2
- 0 <= start < end <= 10^6

---

## Thought Process

1. **Clarify** - Does end == start of next count as overlap? (No, a meeting ending at 5 and one starting at 5 don't conflict.)
2. **Brute force** - Check every pair. O(n^2).
3. **Key insight** - Sort by start time. Then overlaps can only happen between adjacent meetings. Check each consecutive pair.

---

## Worked Example

Can one person attend all meetings? After sorting by start time, just check if any meeting starts before the previous one ends. If yes, there's a conflict.

```
Input: intervals = [[7,10], [2,4], [1,5], [12,14]]

Sort by start: [[1,5], [2,4], [7,10], [12,14]]

  [1,5] vs [2,4]: does 2 < 5? YES → overlap. Return False.
  (Person can't be in both meetings simultaneously.)

Non-conflicting case: [[1,3], [4,6], [7,10]]
  [1,3] vs [4,6]: 4 < 3? No → ok.
  [4,6] vs [7,10]: 7 < 6? No → ok.
  Return True.

One pass after sorting. O(n log n) total.
```

---

## Approaches

### Approach 1: Check Every Pair (Brute Force)

<details>
<summary>📝 Explanation</summary>

Compare every pair of intervals. Two intervals [a_start, a_end] and [b_start, b_end] overlap if `a_start < b_end and b_start < a_end`. If any pair overlaps, return False.

This checks n × (n-1) / 2 pairs. For 100 meetings, that's 4,950 comparisons. It works but doesn't exploit any structure in the data.

**Time:** O(n²) - check all pairs. **Space:** O(1).

Valid as a brute-force starting point. Mention it to show you understand the baseline, then optimize by sorting to reduce the check to adjacent pairs only.

</details>

<details>
<summary>💻 Code</summary>

```python
def can_attend_brute(intervals):
    for i in range(len(intervals)):
        for j in range(i + 1, len(intervals)):
            a_start, a_end = intervals[i]
            b_start, b_end = intervals[j]
            if a_start < b_end and b_start < a_end:
                return False
    return True
```

</details>

---

### Approach 2: Sort and Scan (Optimal)

<details>
<summary>💡 Hint</summary>

After sorting by start time, overlaps can only happen between consecutive intervals.

</details>

<details>
<summary>📝 Explanation</summary>

Sort intervals by start time. After sorting, if any meeting starts before the previous one ends, there's a conflict. Just check adjacent pairs.

Why sorting works: if meetings are sorted by start time and two meetings overlap, they must be adjacent in the sorted order. Meeting A starts earliest of the two. If meeting B starts before A ends, they overlap. No meetings between A and B can start before B (since we're sorted), so checking adjacent pairs is sufficient.

**Time:** O(n log n) - sorting dominates. The scan is O(n).
**Space:** O(1) extra (or O(n) if sort creates a copy).

</details>

<details>
<summary>💻 Code</summary>

```python
def can_attend(intervals):
    intervals.sort(key=lambda x: x[0])
    for i in range(1, len(intervals)):
        if intervals[i][0] < intervals[i - 1][1]:
            return False
    return True
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Empty | `[]` | `True` | No meetings, no conflicts |
| Single | `[[1, 5]]` | `True` | Can't overlap with nothing |
| Adjacent | `[[1, 5], [5, 10]]` | `True` | End == start is NOT overlap |
| Contained | `[[1, 10], [3, 5]]` | `False` | One inside another |
| Same time | `[[1, 5], [1, 5]]` | `False` | Identical intervals overlap |

---

## Common Pitfalls

1. **Not sorting first** - Without sorting, you'd need to check every pair (O(n^2)).
2. **Wrong overlap condition** - `<=` vs `<` matters. If end == start of next meeting, there's no overlap (the first meeting ends exactly when the next begins).
3. **Modifying input** - `sort()` modifies the list in place. If the caller needs the original order, use `sorted()` instead.

---

## Interview Tips

**What to say:**
> "I'll sort by start time, then scan consecutive pairs. If any meeting starts before the previous one ends, there's a conflict. This is O(n log n) for the sort and O(n) for the scan."

**Common follow-ups:**
- "What if meetings can overlap by up to 5 minutes?" → Change the condition to `intervals[i][0] < intervals[i-1][1] - 5`.
- "How many meetings overlap?" → That's Meeting Rooms II (problem 253).

**What the interviewer evaluates:** This is a warm-up. Clean sort + scan is expected quickly. The key insight is sorting by start time and checking adjacent pairs. An interviewer may ask this as a lead-in to Meeting Rooms II.

---

## DE Application

Overlap detection is the building block for:
- **Event deduplication:** Do any ingested events overlap in time? If so, they might be duplicates.
- **SLA validation:** Do any outage windows overlap with SLA coverage windows?
- **Schedule validation:** Can this set of batch jobs all run without overlapping execution windows?
- **Data quality:** Do any date-range partitions overlap (indicating duplicate data)?

## At Scale

Sort + linear scan: O(n log n) time, O(1) extra memory (if sorting in-place). For 10M meetings, sorting takes ~3 seconds. The scan to check for overlaps takes ~50ms. At scale, "do any intervals overlap?" is a data quality check for scheduling data, SLA windows and maintenance periods. In a pipeline, this validates that time-based partitions don't overlap. In SQL: sort by start time, then use LAG to check if the previous end exceeds the current start. If any row satisfies that condition, overlaps exist.

---

## Related Problems

- [56. Merge Intervals](056_merge_intervals.md) - Merge overlapping intervals instead of just detecting them
- [253. Meeting Rooms II](253_meeting_rooms_ii.md) - Count how many overlapping meetings exist at peak
- [435. Non-overlapping Intervals](435_non_overlapping.md) - Minimum removals to eliminate overlaps
