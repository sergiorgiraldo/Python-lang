"""
LeetCode 739: Daily Temperatures

Pattern: Stack - Monotonic decreasing stack
Difficulty: Medium
Time Complexity: O(n)
Space Complexity: O(n)
"""


def daily_temperatures(temperatures: list[int]) -> list[int]:
    """
    For each day, find how many days until a warmer temperature.

    Maintain a stack of indices with decreasing temperatures.
    When a new temperature is warmer than the stack top, it's
    the answer for that stacked day. Pop and record the distance.

    Days remaining in the stack at the end never see a warmer day (answer = 0).
    """
    n = len(temperatures)
    result = [0] * n
    stack: list[int] = []  # indices of unresolved days

    for i in range(n):
        while stack and temperatures[i] > temperatures[stack[-1]]:
            prev = stack.pop()
            result[prev] = i - prev
        stack.append(i)

    return result


def daily_temperatures_brute(temperatures: list[int]) -> list[int]:
    """Brute force: for each day, scan forward for a warmer day. O(n^2)."""
    n = len(temperatures)
    result = [0] * n

    for i in range(n):
        for j in range(i + 1, n):
            if temperatures[j] > temperatures[i]:
                result[i] = j - i
                break

    return result
