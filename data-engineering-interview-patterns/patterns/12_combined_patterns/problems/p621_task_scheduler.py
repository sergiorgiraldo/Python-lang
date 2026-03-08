"""
LeetCode 621: Task Scheduler

Combined Patterns: Hash Map (frequency counting) + Heap (greedy selection)
Difficulty: Medium
Time Complexity: O(n) where n is the number of tasks
Space Complexity: O(1) - at most 26 unique task types
"""

import heapq
from collections import Counter


def least_interval(tasks: list[str], n: int) -> int:
    """
    Find minimum intervals to execute all tasks with cooldown n.

    Each task takes 1 interval. Between two same tasks, there must
    be at least n intervals of cooldown (other tasks or idle).

    Strategy: always schedule the most frequent remaining task.
    This greedy approach minimizes idle time because high-frequency
    tasks are the bottleneck.

    Phase 1 (Hash Map): count task frequencies.
    Phase 2 (Heap): greedily pick the most frequent available task
    each interval. Track cooldowns with a waiting queue.
    """
    counts = Counter(tasks)

    # Max-heap of remaining counts (negate for Python min-heap)
    heap = [-count for count in counts.values()]
    heapq.heapify(heap)

    time = 0
    cooldown: list[tuple[int, int]] = []  # (available_time, remaining_count)

    while heap or cooldown:
        time += 1

        # Move tasks whose cooldown has expired back to the heap
        if cooldown and cooldown[0][0] == time:
            _, count = cooldown.pop(0)
            heapq.heappush(heap, count)

        if heap:
            count = heapq.heappop(heap)
            count += 1  # was negative, so this decrements remaining

            if count != 0:  # still has remaining executions
                cooldown.append((time + n + 1, count))
        # else: idle interval

    return time


def least_interval_math(tasks: list[str], n: int) -> int:
    """
    Math-based approach. O(n) time, O(1) space.

    The most frequent task determines the frame structure:
    (max_freq - 1) chunks of size (n + 1), plus a final partial chunk
    for all tasks tied at max frequency.

    Total = max((max_freq - 1) * (n + 1) + count_of_max_freq, len(tasks))

    The max with len(tasks) handles the case where there are enough
    different tasks to fill all cooldown slots with no idle time.
    """
    counts = Counter(tasks)
    max_freq = max(counts.values())
    max_count = sum(1 for c in counts.values() if c == max_freq)

    # Frame: (max_freq - 1) full chunks + final partial chunk
    intervals = (max_freq - 1) * (n + 1) + max_count

    # If we have more tasks than frame slots, no idle time needed
    return max(intervals, len(tasks))
