"""
LeetCode 853: Car Fleet

Pattern: Stack - Monotonic (by arrival time)
Difficulty: Medium
Time Complexity: O(n log n) due to sorting
Space Complexity: O(n)
"""


def car_fleet(target: int, position: list[int], speed: list[int]) -> int:
    """
    Count car fleets arriving at target.

    A car fleet forms when a faster car catches up to a slower car
    ahead of it. Once caught, they travel together at the slower speed.
    Cars cannot pass each other.

    Sort by position (descending = closest to target first). Calculate
    each car's time to reach the target. If a car behind takes less
    time than the car ahead, it catches up and joins that fleet.
    Use a stack: only push arrival times that are strictly greater
    than the current fleet's time.
    """
    pairs = sorted(zip(position, speed), reverse=True)
    stack: list[float] = []

    for pos, spd in pairs:
        time = (target - pos) / spd
        if not stack or time > stack[-1]:
            stack.append(time)

    return len(stack)
