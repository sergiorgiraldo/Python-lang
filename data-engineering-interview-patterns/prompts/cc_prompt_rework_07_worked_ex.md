# CC Prompt: Rework Worked Examples - Pattern 07 Intervals

## What This Prompt Does

Rewrites `## Worked Example` in all 6 problem files and 4 DE scenario files.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- Only `.md` files. REPLACE `## Worked Example` sections only.
- NO Oxford commas, NO em dashes, NO exclamation points

---

### 252_meeting_rooms.md

```markdown
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
```

### 056_merge_intervals.md

```markdown
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
```

### 253_meeting_rooms_ii.md

```markdown
## Worked Example

How many meeting rooms do we need? This equals the maximum number of meetings happening at the same time. The sweep line technique creates start (+1) and end (-1) events, sorts them, and counts the peak.

```
Input: intervals = [[0,30], [5,10], [15,20], [10,25]]

Create events:
  (0, start), (5, start), (10, end), (10, start), (15, start),
  (20, end), (25, end), (30, end)

Sort (break ties: ends before starts at the same time):
  (0,+1) (5,+1) (10,-1) (10,+1) (15,+1) (20,-1) (25,-1) (30,-1)

Walk through:
  t=0:  rooms = 0+1 = 1
  t=5:  rooms = 1+1 = 2
  t=10: rooms = 2-1 = 1 (one meeting ends)
  t=10: rooms = 1+1 = 2 (another starts)
  t=15: rooms = 2+1 = 3 ← PEAK
  t=20: rooms = 3-1 = 2
  t=25: rooms = 2-1 = 1
  t=30: rooms = 1-1 = 0

  Answer: 3 rooms needed.

Alternative: use a min-heap tracking end times. At each meeting start,
if the earliest ending meeting is over, reuse that room (pop from heap).
Otherwise allocate a new room.
```
```

### 057_insert_interval.md

```markdown
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
```

### 435_non_overlapping.md

```markdown
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
```

### 986_interval_intersections.md

```markdown
## Worked Example

Find the intersection of two sorted lists of intervals. Two pointers, one per list. At each step, check if the current pair overlaps. If yes, the intersection is [max of starts, min of ends]. Advance whichever pointer has the earlier end.

```
Input:
  A = [[0,2], [5,10], [13,23], [24,25]]
  B = [[1,5], [8,12], [15,24], [25,26]]

  pA=0, pB=0

  A=[0,2] vs B=[1,5]: overlap? max(0,1)=1 ≤ min(2,5)=2. YES.
    Intersection: [1,2]. A ends first (2<5) → advance pA.

  A=[5,10] vs B=[1,5]: overlap? max(5,1)=5 ≤ min(10,5)=5. YES (touching).
    Intersection: [5,5]. B ends first (5<10) → advance pB.

  A=[5,10] vs B=[8,12]: overlap? max(5,8)=8 ≤ min(10,12)=10. YES.
    Intersection: [8,10]. A ends first → advance pA.

  A=[13,23] vs B=[8,12]: overlap? max(13,8)=13 ≤ min(23,12)=12. NO.
    B ends first → advance pB.

  A=[13,23] vs B=[15,24]: overlap? max(13,15)=15 ≤ min(23,24)=23. YES.
    Intersection: [15,23]. A ends first → advance pA.

  A=[24,25] vs B=[15,24]: overlap? max(24,15)=24 ≤ min(25,24)=24. YES.
    Intersection: [24,24]. B ends first → advance pB.

  A=[24,25] vs B=[25,26]: overlap? max(24,25)=25 ≤ min(25,26)=25. YES.
    Intersection: [25,25]. A ends first → advance pA. A exhausted.

  Result: [[1,2], [5,5], [8,10], [15,23], [24,24], [25,25]]
  O(n + m), one pass through both lists.
```
```

---

## DE Scenarios

### de_scenarios/time_range_overlap.md

```markdown
## Worked Example

Detecting overlapping partition date ranges - if two partitions overlap, they may contain duplicate data.

```
Partitions:
  [2024-01-01, 2024-01-15]
  [2024-01-10, 2024-01-20]  ← overlaps with first
  [2024-01-20, 2024-01-31]
  [2024-02-01, 2024-02-15]

Sort by start (already sorted). Check adjacent pairs:
  Jan 01-15 vs Jan 10-20: 10 < 15? YES → OVERLAP. Data duplication risk.
  Jan 10-20 vs Jan 20-31: 20 < 20? NO (end-exclusive) → ok.
  Jan 20-31 vs Feb 01-15: 01 < 31? Depends on convention.

Flag: partitions 1 and 2 overlap by 5 days (Jan 10-15).
Investigate for duplicate data or re-partition.
```
```

### de_scenarios/resource_scheduling.md

```markdown
## Worked Example

How many parallel execution slots does a job scheduler need? Same algorithm as Meeting Rooms II applied to batch job windows.

```
Jobs: extract (00:00-02:00), transform_A (01:00-03:00),
      transform_B (01:30-04:00), load (03:30-05:00), report (05:00-06:00)

Sweep line events:
  00:00+1, 01:00+1, 01:30+1, 02:00-1, 03:00-1, 03:30+1, 04:00-1, 05:00-1, 05:00+1, 06:00-1

  Slots: 1→2→3→2→1→2→1→0→1→0
  Peak: 3 (between 01:30 and 02:00)

  Need 3 parallel slots. Adding a 4th concurrent job would require scaling.
```
```

### de_scenarios/session_stitching.md

```markdown
## Worked Example

Merge overlapping user activity events into sessions. Same algorithm as Merge Intervals applied to clickstream data.

```
User events (sorted by timestamp):
  [10:01, 10:05]  page_view
  [10:03, 10:08]  click        ← overlaps, same session
  [10:07, 10:12]  page_view    ← overlaps, same session
  [10:30, 10:35]  page_view    ← gap > threshold, NEW session
  [10:33, 10:40]  click        ← overlaps, same session

Merge overlapping:
  [10:01, 10:05] + [10:03, 10:08] → [10:01, 10:08]
  [10:01, 10:08] + [10:07, 10:12] → [10:01, 10:12]
  Gap to [10:30, 10:35] → new session
  [10:30, 10:35] + [10:33, 10:40] → [10:30, 10:40]

  Sessions: [10:01-10:12] (11 min), [10:30-10:40] (10 min)
  5 events → 2 sessions.
```
```

### de_scenarios/interval_intersection.md

```markdown
## Worked Example

Finding when two systems had overlapping outages. Same algorithm as Interval Intersections (problem 986) applied to incident windows.

```
System A outages: [[02:00, 04:00], [08:00, 09:00], [14:00, 18:00]]
System B outages: [[03:00, 05:00], [07:00, 10:00], [16:00, 20:00]]

Two-pointer intersection:
  A=[02:00,04:00] vs B=[03:00,05:00]: overlap [03:00,04:00]
  A=[08:00,09:00] vs B=[07:00,10:00]: overlap [08:00,09:00]
  A=[14:00,18:00] vs B=[16:00,20:00]: overlap [16:00,18:00]

Both systems down simultaneously: 03-04, 08-09, 16-18.
Total dual-outage: 4 hours. Useful for SLA impact analysis.
```
```

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns
git diff --name-only | grep -v '.md$'
uv run pytest patterns/07_intervals/ -v --tb=short 2>&1 | tail -3

echo "=== Worked Example count ==="
grep -rl "## Worked Example" patterns/07_intervals/ | wc -l
echo "(should be 10: 6 problems + 4 DE scenarios)"
```
