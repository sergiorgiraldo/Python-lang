# CC Prompt: Rework Approach Explanations - Pattern 07 Intervals

## What This Prompt Does

Rewrites every `📝 Explanation` block in all 6 problem files.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- Replace content inside `<details>` blocks containing `📝 Explanation` only.
- Leave `💡 Hint` and `💻 Code` blocks untouched.
- NO Oxford commas, NO em dashes, NO exclamation points

---

### 252_meeting_rooms.md - Brute Force

```
Compare every pair of intervals. Two intervals overlap if `a_start < b_end and b_start < a_end`. If any pair overlaps, return False.

**Time:** O(n²) - check all pairs. **Space:** O(1).

Mention it and optimize.
```

### 252_meeting_rooms.md - Sort + Scan

```
Sort intervals by start time. After sorting, if any meeting starts before the previous one ends, there's a conflict. Just check adjacent pairs.

Why sorting works: if meetings are sorted by start time and two meetings overlap, they must be adjacent in the sorted order. Meeting A starts earliest of the two. If meeting B starts before A ends, they overlap. No meetings between A and B can start before B (since we're sorted), so checking adjacent pairs is sufficient.

**Time:** O(n log n) - sorting dominates. The scan is O(n).
**Space:** O(1) extra (or O(n) if sort creates a copy).
```

### 056_merge_intervals.md - Sort + Linear Merge

```
Sort by start time. Walk through the sorted intervals with a result list:
1. Add the first interval to the result.
2. For each subsequent interval:
   - If it overlaps with the last result (its start ≤ the last result's end), extend the last result's end to `max(last_end, current_end)`.
   - If it doesn't overlap, append it as a new entry.

The "extend" step handles both partial overlaps ([1,5] and [3,7] → [1,7]) and containment ([1,10] and [3,5] → [1,10], since max(10,5)=10).

**Time:** O(n log n) - sorting. The merge scan is O(n).
**Space:** O(n) - the result list.

This is the standard approach. There's no faster general solution because determining if intervals overlap requires sorting-level work.
```

### 253_meeting_rooms_ii.md - Sweep Line

```
Create a timeline of events: each interval start is a +1 event (room needed), each end is a -1 event (room freed). Sort all events. Walk through, tracking the running count. The peak count is the minimum number of rooms.

When a start and end happen at the same time, process ends first (a room freed at time T can be reused by a meeting starting at time T).

**Time:** O(n log n) - sorting the 2n events.
**Space:** O(n) - the event list.

Alternative implementation: use a min-heap of end times. At each meeting start, if the heap's minimum end time ≤ current start, pop it (reuse that room). Push the current meeting's end time. The heap size at any point is the current room count. Same complexity, slightly different code.
```

### 253_meeting_rooms_ii.md - Min-Heap

```
Sort meetings by start time. Maintain a min-heap of end times (each entry represents a room's next available time).

For each meeting:
- If the heap's minimum end time ≤ current meeting's start, that room is free. Pop it (reuse the room).
- Push the current meeting's end time onto the heap (assign this room).
- The heap size after processing all meetings is the answer.

**Time:** O(n log n) - sorting plus n heap operations (each O(log n)).
**Space:** O(n) - heap size equals the number of rooms.

This is functionally equivalent to the sweep line. The heap approach models rooms explicitly. The sweep line models the timeline.
```

### 057_insert_interval.md - Three-Phase Linear Scan

```
Walk through the sorted intervals in three phases:
1. **Before:** Add all intervals that end before the new interval starts (no overlap).
2. **During:** Merge all intervals that overlap with the new interval. The merged interval's start is the min of all starts, end is the max of all ends.
3. **After:** Add all remaining intervals (they start after the merged interval ends).

The "during" phase handles 0 overlaps (the new interval fits in a gap) to n overlaps (the new interval spans the entire list).

**Time:** O(n) - single pass through the list. No sorting needed because the input is already sorted.
**Space:** O(n) - the result list.
```

### 435_non_overlapping.md - Greedy (Sort by End Time)

```
Classic activity selection: keep as many non-overlapping intervals as possible, which minimizes removals.

Sort by end time. Greedily keep each interval that doesn't overlap with the last kept interval (its start ≥ the last kept interval's end). Count the ones we skip.

Why sort by end time? The interval that ends earliest leaves the most room for future intervals. Sorting by start time doesn't work: [1,100] starts earliest but blocks everything after it.

**Time:** O(n log n) - sort dominates. The greedy scan is O(n).
**Space:** O(1) extra.

The answer (minimum removals) = total intervals - maximum non-overlapping intervals.
```

### 986_interval_intersections.md - Two Pointers

```
Both input lists are sorted by start time. Use one pointer per list. At each step:

1. Check if the current pair overlaps: `max(a_start, b_start) ≤ min(a_end, b_end)`.
2. If yes, the intersection is `[max(a_start, b_start), min(a_end, b_end)]`. Add it to the result.
3. Advance the pointer whose current interval ends first. That interval can't overlap with anything later in the other list (since both lists are sorted).

**Time:** O(n + m) where n and m are the lengths of the two lists. Each pointer advances at most n or m times.
**Space:** O(1) extra (not counting the output).

This is the same two-pointer merge pattern from Pattern 02, adapted for intersection instead of union.
```

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns
git diff --name-only | grep -v '.md$'
uv run pytest patterns/07_intervals/ -v --tb=short 2>&1 | tail -3

for f in patterns/07_intervals/problems/*.md; do
    name=$(basename "$f")
    awk '/📝 Explanation/{found=1; lines=0; next} found && /<\/details>/{if(lines<4) printf "❌ %s: %d lines\n", "'"$name"'", lines; found=0} found && /\S/{lines++}' "$f"
done
echo "(no output = all substantial)"
```
