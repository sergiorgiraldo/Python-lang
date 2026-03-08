"""
LeetCode 253: Meeting Rooms II (Premium)

Pattern: Intervals - Min-heap for concurrent count
Difficulty: Medium
Time Complexity: O(n log n)
Space Complexity: O(n)
"""

import heapq


def min_meeting_rooms_heap(intervals: list[list[int]]) -> int:
    """
    Find the minimum number of conference rooms needed.

    Sort by start time. Use a min-heap of end times to track
    active meetings. When a new meeting starts after the earliest
    ending meeting, reuse that room. Otherwise, add a new room.

    Args:
        intervals: List of [start, end] meeting times.

    Returns:
        Minimum number of rooms required.

    Example:
        >>> min_meeting_rooms_heap([[0, 30], [5, 10], [15, 20]])
        2
    """
    if not intervals:
        return 0

    intervals.sort(key=lambda x: x[0])
    heap: list[int] = []  # end times of active meetings

    for start, end in intervals:
        if heap and heap[0] <= start:
            heapq.heapreplace(heap, end)  # reuse earliest-ending room
        else:
            heapq.heappush(heap, end)  # need a new room

    return len(heap)


def min_meeting_rooms_sweep(intervals: list[list[int]]) -> int:
    """
    Sweep line approach: process start/end events separately.

    Create +1 events for starts and -1 events for ends.
    Sort all events. The running sum's maximum is the peak
    concurrent count.

    Time: O(n log n)  Space: O(n)
    """
    if not intervals:
        return 0

    events: list[tuple[int, int]] = []
    for start, end in intervals:
        events.append((start, 1))  # meeting starts
        events.append((end, -1))  # meeting ends

    # Sort: by time, then ends before starts at same time
    events.sort(key=lambda x: (x[0], x[1]))

    max_rooms = 0
    current = 0
    for _, delta in events:
        current += delta
        max_rooms = max(max_rooms, current)

    return max_rooms


if __name__ == "__main__":
    cases = [
        [[0, 30], [5, 10], [15, 20]],
        [[7, 10], [2, 4]],
        [[1, 5], [2, 3], [4, 6], [5, 7]],
    ]
    for intervals in cases:
        print(f"min_rooms({intervals}) = {min_meeting_rooms_heap(intervals)}")
