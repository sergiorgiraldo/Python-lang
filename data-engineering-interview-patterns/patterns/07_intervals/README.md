# Intervals Pattern

## What Is It?

### The basics

An interval is a pair of values representing a range: `[start, end]`. A meeting from 9:00 to 10:00, a data partition covering dates 2024-01-01 to 2024-01-31, a SLA window from midnight to 6am. Two intervals **overlap** if one starts before the other ends: `a_start < b_end and b_start < a_end`.

In Python, intervals are usually lists or tuples of two elements:

```python
meeting = [9, 10]       # start=9, end=10
intervals = [[1,3], [2,6], [8,10], [15,18]]
```

### The universal first step: sort by start time

Nearly every interval problem starts the same way: **sort by start time**. Once sorted, you only need to compare adjacent intervals to detect overlaps. Without sorting, you'd have to compare every pair (O(n²)).

```python
intervals.sort(key=lambda x: x[0])  # sort by start
```

After sorting `[[8,10], [1,3], [15,18], [2,6]]` becomes `[[1,3], [2,6], [8,10], [15,18]]`. Now overlapping intervals are always next to each other.

### The overlap test

Two intervals `[a_start, a_end]` and `[b_start, b_end]` overlap if and only if:

```python
a_start < b_end and b_start < a_end
```

Equivalently, they do NOT overlap if one ends before the other starts: `a_end <= b_start or b_end <= a_start`. This test is the building block for every problem in this section.

### The three core operations

**1. Merge overlapping intervals**

Combine intervals that overlap or touch into single larger intervals. Walk through the sorted list. If the current interval overlaps with the previous result, extend the previous result. If not, start a new result.

```python
if current_start <= result[-1][1]:    # overlaps with last result
    result[-1][1] = max(result[-1][1], current_end)  # extend
else:
    result.append(current)            # no overlap, new result
```

**2. Count maximum concurrent intervals**

How many intervals overlap at the same time? (How many meeting rooms needed? How many parallel tasks?) Use a sweep line: create a list of all start and end events, sort them, and walk through. Each start increments a counter, each end decrements it. The peak counter value is the answer.

**3. Find intersections between two sorted lists**

Given two lists of intervals (both sorted by start), find where they overlap. Two pointers (one per list). At each step, compute the intersection (if any) and advance the pointer whose interval ends first.

### Connection to data engineering

Interval problems map directly to real data engineering work:

- **Partition management:** Do any date-range partitions overlap? (data duplication risk)
- **SLA validation:** Which outage windows violate SLA coverage periods?
- **Session stitching:** Merge overlapping user activity windows into sessions
- **Job scheduling:** How many execution slots do we need if these jobs can't overlap?
- **Time-range queries:** "Give me all events between timestamp A and B"
- **Event deduplication:** Overlapping time windows from different sources may contain duplicate data

### What the problems in this section use

| Problem | Core operation | What it models |
|---|---|---|
| Meeting Rooms | Overlap detection | "Can one person attend all meetings?" |
| Merge Intervals | Merge overlapping | Combine overlapping ranges into minimal set |
| Meeting Rooms II | Count max concurrent | "How many rooms needed?" |
| Insert Interval | Merge with new interval | Add a range to an existing set |
| Non-Overlapping Intervals | Find minimum removals | Remove fewest intervals to eliminate all overlaps |
| Interval Intersections | Two-list intersection | Find overlapping portions of two schedules |

## When to Use It

**Recognition signals in interviews:**
- "Given a list of intervals/meetings/events..."
- "Find overlapping time ranges..."
- "Merge overlapping intervals..."
- "Minimum number of rooms/resources..."
- "Can this person attend all meetings?"
- Any problem with [start, end] pairs

**Recognition signals in DE work:**
- Session stitching from raw events
- Time-range overlap detection for deduplication
- Scheduling pipeline jobs within time windows
- Partition range management
- SLA window calculations

## Visual Aid

```
Merge Intervals:

Input (after sorting by start):
  [1,3]  [2,6]  [8,10]  [15,18]
   ───    ────    ──      ───
  1  3   2    6  8  10  15  18

  [1,3] and [2,6] overlap (2 < 3). Merge → [1,6].
  [1,6] and [8,10] don't overlap (8 > 6). Keep separate.
  [8,10] and [15,18] don't overlap. Keep separate.

  Result: [1,6]  [8,10]  [15,18]

Meeting Rooms II (sweep line):

  Meetings: [0,30]  [5,10]  [15,20]

  Events: (0,start) (5,start) (10,end) (15,start) (20,end) (30,end)
  Sorted: 0:+1  5:+1  10:-1  15:+1  20:-1  30:-1

  Counter: 0→1→2→1→2→1→0
  Peak: 2. Need 2 meeting rooms.

Interval Intersection (two pointers):

  A: [0,2]  [5,10]  [13,23]
  B: [1,5]  [8,12]  [15,24]

  A[0]=[0,2] vs B[0]=[1,5]: overlap at [1,2]. A ends first → advance A.
  A[1]=[5,10] vs B[0]=[1,5]: overlap at [5,5]. B ends first → advance B.
  A[1]=[5,10] vs B[1]=[8,12]: overlap at [8,10]. A ends first → advance A.
  A[2]=[13,23] vs B[1]=[8,12]: no overlap. B ends first → advance B.
  A[2]=[13,23] vs B[2]=[15,24]: overlap at [15,23]. A ends first → advance A.

  Intersections: [[1,2], [5,5], [8,10], [15,23]]
```

## The Foundation: Sort by Start Time

Nearly every interval problem starts with sorting by start time. Once sorted:
- Overlapping intervals are adjacent in the sorted order
- You can process them in a single left-to-right scan
- The problem reduces to comparing each interval with the previous one

```python
intervals.sort(key=lambda x: x[0])
```

This is the single most important line in interval problems. If you remember nothing else, remember to sort first.

## Overlap Detection

Two intervals [a_start, a_end] and [b_start, b_end] overlap if and only if:

```python
a_start < b_end and b_start < a_end
```

Think of it as: they overlap unless one ends before the other starts. The negation of "no overlap" is simpler to reason about:
- No overlap: `a_end <= b_start or b_end <= a_start`
- Overlap: the opposite of that

## Three Patterns You Need to Know

### 1. Sort and Scan (Merge / Overlap Check)

Sort by start, scan left to right. Compare each interval with the running "current" interval.

```python
def merge(intervals):
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:  # overlaps
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged
```

### 2. Min-Heap for Concurrent Count (Meeting Rooms)

Sort by start. Use a min-heap to track end times of active intervals. The heap size at any point is the number of concurrent intervals.

```python
import heapq

def min_rooms(intervals):
    intervals.sort(key=lambda x: x[0])
    heap = []  # end times of active meetings
    for start, end in intervals:
        if heap and heap[0] <= start:
            heapq.heapreplace(heap, end)  # reuse room
        else:
            heapq.heappush(heap, end)  # new room
    return len(heap)
```

### 3. Greedy Interval Scheduling (Minimum Removals)

Sort by end time. Greedily keep intervals that don't conflict with the last kept interval. This maximizes non-overlapping intervals (equivalently, minimizes removals).

```python
def min_removals(intervals):
    intervals.sort(key=lambda x: x[1])  # sort by END
    kept = 0
    last_end = float('-inf')
    for start, end in intervals:
        if start >= last_end:  # no conflict
            kept += 1
            last_end = end
    return len(intervals) - kept
```

## Time/Space Complexity

| Operation | Complexity |
|-----------|------------|
| Sort intervals | O(n log n) |
| Merge overlapping | O(n log n) sort + O(n) scan |
| Count max concurrent | O(n log n) sort + O(n log n) heap |
| Check any overlap | O(n log n) sort + O(n) scan |
| Interval intersection | O(n + m) with two pointers (pre-sorted) |

The sorting step dominates. The scan/merge is always O(n).

## Trade-offs

**Sorting is the foundation.** Almost every interval algorithm requires O(n log n) sorting as a first step. After sorting, the processing step is usually O(n). Total: O(n log n). You can't do better than this for general interval problems (proving an interval set is non-overlapping requires sorting-level work).

**Sort by start vs sort by end:** Most problems sort by start time. The exception is Non-Overlapping Intervals (greedy activity selection), which sorts by end time to maximize the number of non-overlapping intervals.

**When intervals don't apply:**
- If ranges aren't naturally ordered (categorical groupings rather than numeric ranges)
- If you need to efficiently query "which intervals contain point X" repeatedly, you need an interval tree (not covered here - rarely asked in interviews)

### Scale characteristics

Interval problems almost always sort first: O(n log n). The merge/scan pass is O(n). Memory depends on the specific problem but is typically O(n) for the output.

| n (intervals) | Sort time | Merge time | Total |
|---|---|---|---|
| 100K | ~20ms | ~5ms | ~25ms |
| 10M | ~3 seconds | ~500ms | ~3.5 seconds |
| 1B | ~5 minutes | ~1 minute | ~6 minutes |

**Distributed equivalent:** Sorting intervals by start time, then merging is a natural fit for distributed sort-merge. Spark handles this as: repartition by start time range, sort within each partition, merge locally, then handle cross-partition boundary intervals. The boundary case is the tricky part: an interval that starts in partition k might overlap with intervals in partition k+1. A second pass to merge boundary intervals is needed.

**Time-series join (interval overlap):** Finding overlapping time ranges across two datasets is an interval intersection problem. In SQL, this is often written as `WHERE a.start < b.end AND a.end > b.start` - a range join. Without optimization, this is O(n*m). Databases use interval trees, sort-merge approaches or bin-based partitioning to speed this up. BigQuery and Spark don't natively optimize range joins, so they often devolve to cross joins with filters. Knowing this limitation (and workarounds like binning by time period) is a principal-level skill.

### SQL equivalent

Interval operations in SQL use window functions and self-joins. Merging overlapping intervals: `LAG(end) OVER (ORDER BY start)` to detect overlaps, then group contiguous overlapping intervals. Meeting rooms (counting concurrent intervals): convert to events (start/end), sort, use a running count. The SQL section's window functions and joins subsections cover these patterns. Range joins (finding overlapping intervals across two tables) are particularly important for DE and are covered in the optimization subsection.

## Problems

| # | Problem | Difficulty | Key Concept |
|---|---------|------------|-------------|
| [252](https://leetcode.com/problems/meeting-rooms/) | [Meeting Rooms](problems/252_meeting_rooms.md) | Easy | Overlap detection |
| [56](https://leetcode.com/problems/merge-intervals/) | [Merge Intervals](problems/056_merge_intervals.md) | Medium | Sort + merge scan |
| [253](https://leetcode.com/problems/meeting-rooms-ii/) | [Meeting Rooms II](problems/253_meeting_rooms_ii.md) | Medium | Min-heap for concurrent count |
| [57](https://leetcode.com/problems/insert-interval/) | [Insert Interval](problems/057_insert_interval.md) | Medium | Binary search + merge |
| [435](https://leetcode.com/problems/non-overlapping-intervals/) | [Non-overlapping Intervals](problems/435_non_overlapping.md) | Medium | Greedy scheduling |
| [986](https://leetcode.com/problems/interval-list-intersections/) | [Interval List Intersections](problems/986_interval_intersections.md) | Medium | Two-pointer intersection |

**Suggested order:** 252 → 56 → 253 → 57 → 435 → 986

Start with 252 (simplest overlap check). 56 is the foundational merge problem. 253 adds heap-based concurrent counting. 57 teaches interval insertion. 435 introduces greedy scheduling. 986 combines intervals with two pointers.

## DE Scenarios

| Scenario | What It Demonstrates |
|----------|---------------------|
| [Time Range Overlap](de_scenarios/time_range_overlap.md) | Event deduplication using overlap detection |
| [Resource Scheduling](de_scenarios/resource_scheduling.md) | Concurrent job slot management |
| [Session Stitching](de_scenarios/session_stitching.md) | Merging raw events into sessions |
| [Interval Intersection](de_scenarios/interval_intersection.md) | Finding common time windows |

## Interview Tips

**What to say when you recognize this pattern:**
> "This is an interval problem. My first step is to sort by start time. That way, overlapping intervals are adjacent and I can solve this in a single scan."

**Common follow-ups:**
- "What if the intervals are already sorted?" → Skip the sort, go straight to the scan. Complexity drops from O(n log n) to O(n).
- "What if intervals can be open or closed?" → Clarify whether endpoints are inclusive. It affects the overlap condition: `<` vs `<=`.
- "What about very large datasets?" → Interval merge is inherently sequential (each interval depends on the previous). But you can partition by time ranges, merge within partitions, then merge boundaries.

**Python-specific tips:**
- `intervals.sort(key=lambda x: x[0])` sorts by start time
- `intervals.sort(key=lambda x: (x[0], x[1]))` breaks ties by end time
- Use `heapq` for concurrent counting (Meeting Rooms II)
- Intervals are usually `list[list[int]]` on LeetCode but `list[tuple[int, int]]` is cleaner

## Related Patterns

- **Two Pointers** - Interval intersection uses two pointers on sorted lists. Direct connection to pattern 02.
- **Heap / Priority Queue** - Meeting Rooms II uses a min-heap to track active meetings. Direct connection to pattern 05.
- **Sliding Window** - Session stitching is interval merging on time-series data. Related to pattern 04.
- **Binary Search** - Finding where a new interval fits in a sorted list uses binary search. Connection to pattern 03.

## What's Next

After completing interval problems, move to [Stack](../08_stack/) for nested structure validation and monotonic stack patterns.

---