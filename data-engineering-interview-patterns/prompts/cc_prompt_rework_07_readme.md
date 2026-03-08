# CC Prompt: Rework README - Pattern 07 Intervals

## What This Prompt Does

Rewrites README.md "What Is It?", "Visual Aid" and "Trade-offs" sections.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- Only modify `patterns/07_intervals/README.md`. REPLACE specified sections only.
- NO Oxford commas, NO em dashes, NO exclamation points

---

## Replace `## What Is It?` (everything up to `## When to Use It`)

```markdown
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
```

## Replace `## Visual Aid` (up to `## Template`)

```markdown
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
```

## Replace `## Trade-offs` (up to `## Problems in This Section`)

```markdown
## Trade-offs

**Sorting is the foundation.** Almost every interval algorithm requires O(n log n) sorting as a first step. After sorting, the processing step is usually O(n). Total: O(n log n). You can't do better than this for general interval problems (proving an interval set is non-overlapping requires sorting-level work).

**Sort by start vs sort by end:** Most problems sort by start time. The exception is Non-Overlapping Intervals (greedy activity selection), which sorts by end time to maximize the number of non-overlapping intervals.

**When intervals don't apply:**
- If ranges aren't naturally ordered (categorical groupings rather than numeric ranges)
- If you need to efficiently query "which intervals contain point X" repeatedly, you need an interval tree (not covered here - rarely asked in interviews)
```

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns
git diff --name-only | grep -v '.md$'
uv run pytest patterns/07_intervals/ -v --tb=short 2>&1 | tail -3

for section in "The basics" "sort by start" "overlap test" "three core" "Connection to data" "problems in this section"; do
    grep -qi "$section" patterns/07_intervals/README.md && echo "✅ $section" || echo "❌ $section"
done
```
