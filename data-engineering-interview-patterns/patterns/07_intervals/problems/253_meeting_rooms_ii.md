# Meeting Rooms II (LeetCode #253)

🔗 [LeetCode 253: Meeting Rooms II](https://leetcode.com/problems/meeting-rooms-ii/)

> **Difficulty:** Medium | **Interview Frequency:** Common

*This is a LeetCode Premium problem. The problem description below is written in our own words. If you have LeetCode Premium, the original is at https://leetcode.com/problems/meeting-rooms-ii/.*

## Problem Statement

Given a list of meeting time intervals, find the minimum number of conference rooms required so that all meetings can take place.

**Example:**
```
Input: intervals = [[0, 30], [5, 10], [15, 20]]
Output: 2
Explanation: [0,30] and [5,10] overlap, so they need 2 rooms.
[15,20] can reuse the room from [5,10] (which ended at 10).
```

**Constraints:**
- 1 <= intervals.length <= 10^4
- 0 <= start < end <= 10^6

---

## Thought Process

1. **Clarify** - If a meeting ends at time T and another starts at T, they can share a room.
2. **Key insight** - We need to track how many meetings are active at any point. The peak concurrent count is the answer.
3. **Two approaches** - Min-heap of end times (track active meetings) or sweep line (count start/end events).

---

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

---

## Approaches

### Approach 1: Min-Heap of End Times

<details>
<summary>💡 Hint</summary>

The heap tracks rooms in use. Its minimum is the earliest time a room becomes free. If the next meeting starts after that, reuse the room.

</details>

<details>
<summary>📝 Explanation</summary>

Sort meetings by start time. Maintain a min-heap of end times (each entry represents a room's next available time).

For each meeting:
- If the heap's minimum end time ≤ current meeting's start, that room is free. Pop it (reuse the room).
- Push the current meeting's end time onto the heap (assign this room).
- The heap size after processing all meetings is the answer.

**Time:** O(n log n) - sorting plus n heap operations (each O(log n)).
**Space:** O(n) - heap size equals the number of rooms.

This is functionally equivalent to the sweep line. The heap approach models rooms explicitly. The sweep line models the timeline.

</details>

<details>
<summary>💻 Code</summary>

```python
import heapq

def min_meeting_rooms_heap(intervals):
    if not intervals: return 0
    intervals.sort(key=lambda x: x[0])
    heap = []
    for start, end in intervals:
        if heap and heap[0] <= start:
            heapq.heapreplace(heap, end)
        else:
            heapq.heappush(heap, end)
    return len(heap)
```

</details>

---

### Approach 2: Sweep Line

<details>
<summary>📝 Explanation</summary>

Create a timeline of events: each interval start is a +1 event (room needed), each end is a -1 event (room freed). Sort all events. Walk through, tracking the running count. The peak count is the minimum number of rooms.

When a start and end happen at the same time, process ends first (a room freed at time T can be reused by a meeting starting at time T).

**Time:** O(n log n) - sorting the 2n events.
**Space:** O(n) - the event list.

Alternative implementation: use a min-heap of end times. At each meeting start, if the heap's minimum end time ≤ current start, pop it (reuse that room). Push the current meeting's end time. The heap size at any point is the current room count. Same complexity, slightly different code.

</details>

<details>
<summary>💻 Code</summary>

```python
def min_meeting_rooms_sweep(intervals):
    if not intervals: return 0
    events = []
    for start, end in intervals:
        events.append((start, 1))
        events.append((end, -1))
    events.sort(key=lambda x: (x[0], x[1]))
    max_rooms = current = 0
    for _, delta in events:
        current += delta
        max_rooms = max(max_rooms, current)
    return max_rooms
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| No overlap | `[[2,4],[7,10]]` | `1` | One room suffices |
| Full overlap | `[[1,10],[2,9],[3,8]]` | `3` | All concurrent |
| Back-to-back | `[[1,5],[5,10]]` | `1` | Room reused at boundary |
| Same time | `[[1,5],[1,5],[1,5]]` | `3` | All start simultaneously |

---

## Common Pitfalls

1. **Boundary condition: `<=` vs `<`** - A meeting ending at 5 and one starting at 5 can share a room. Use `<=` when comparing heap top to start.
2. **Sweep line event ordering** - At the same timestamp, process ends (-1) before starts (+1). The sort handles this if you sort by (time, delta) since -1 < 1.

---

## Interview Tips

**What to say:**
> "I'll sort by start time and use a min-heap to track end times of active meetings. The heap size at peak is the minimum rooms needed."

**What the interviewer evaluates:** The heap approach tests data structure selection. The sweep line approach tests event-based thinking. Both are valid. Mentioning that this is how concurrent usage is measured in production (BigQuery slot monitoring, database connection pooling) shows systems awareness. The follow-up "what if meetings can be updated?" tests whether you can handle dynamic intervals.

---

## DE Application

This pattern maps directly to resource scheduling:
- "How many parallel Spark executors do we need for these overlapping jobs?"
- "What's the peak number of concurrent database connections?"
- "How many Airflow worker slots are needed for this schedule?"

See: [Resource Scheduling DE Scenario](../de_scenarios/resource_scheduling.md)

## At Scale

The min-heap approach uses O(n) memory in the worst case (all meetings overlap). For 10M meetings, that's ~160MB for the heap. The sweep line alternative (sort start/end events, scan) uses O(n) memory for the events array but processes in a single pass. At scale, "maximum concurrent connections/sessions/jobs" is a key capacity planning metric. In production, this is often computed in SQL: `SELECT MAX(concurrent) FROM (SELECT timestamp, SUM(delta) OVER (ORDER BY timestamp) as concurrent FROM events)`. Cloud billing (concurrent slot usage in BigQuery) uses exactly this calculation. Knowing the algorithmic version helps you understand and optimize the SQL version.

---

## Related Problems

- [252. Meeting Rooms](252_meeting_rooms.md) - Just detect overlap (simpler)
- [56. Merge Intervals](056_merge_intervals.md) - Merge overlapping ranges
