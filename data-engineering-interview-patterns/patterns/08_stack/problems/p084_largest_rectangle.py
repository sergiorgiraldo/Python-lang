"""
LeetCode 84: Largest Rectangle in Histogram

Pattern: Stack - Monotonic increasing stack
Difficulty: Hard
Time Complexity: O(n)
Space Complexity: O(n)
"""


def largest_rectangle_area(heights: list[int]) -> int:
    """
    Find the largest rectangular area in a histogram.

    Use a monotonic increasing stack of indices. When a bar shorter
    than the stack top appears, the topped bar can no longer extend
    right. Pop it and calculate its area using:
    - height = the popped bar's height
    - width = distance from the new stack top to the current index - 1

    A sentinel value of 0 is appended to flush all remaining bars.
    """
    stack: list[int] = []  # indices
    max_area = 0
    heights = heights + [0]  # sentinel to force final cleanup

    for i, h in enumerate(heights):
        while stack and heights[stack[-1]] > h:
            height = heights[stack.pop()]
            width = i if not stack else i - stack[-1] - 1
            max_area = max(max_area, height * width)
        stack.append(i)

    return max_area


def largest_rectangle_brute(heights: list[int]) -> int:
    """Brute force: for each bar, expand left and right. O(n^2)."""
    max_area = 0
    n = len(heights)

    for i in range(n):
        h = heights[i]
        left = i
        right = i
        while left > 0 and heights[left - 1] >= h:
            left -= 1
        while right < n - 1 and heights[right + 1] >= h:
            right += 1
        max_area = max(max_area, h * (right - left + 1))

    return max_area
