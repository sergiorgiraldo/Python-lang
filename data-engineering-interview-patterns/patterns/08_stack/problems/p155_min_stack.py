"""
LeetCode 155: Min Stack

Pattern: Stack - Augmented data structure
Difficulty: Medium
Time Complexity: O(1) for all operations
Space Complexity: O(n)
"""


class MinStackTuple:
    """
    Stack that supports push, pop, top and getMin in O(1).

    Each entry stores (value, current_minimum). The minimum at any
    point is the min of the new value and the previous minimum.
    This way, popping an element also "restores" the previous minimum.
    """

    def __init__(self) -> None:
        self.stack: list[tuple[int, int]] = []

    def push(self, val: int) -> None:
        current_min = min(val, self.stack[-1][1]) if self.stack else val
        self.stack.append((val, current_min))

    def pop(self) -> None:
        self.stack.pop()

    def top(self) -> int:
        return self.stack[-1][0]

    def get_min(self) -> int:
        return self.stack[-1][1]


class MinStackTwoStacks:
    """
    Alternative: separate main stack and min-tracking stack.

    The min stack only pushes when a new minimum (or equal) arrives.
    Pops from min stack only when the popped value equals the current min.
    Uses less space when minimums change infrequently.
    """

    def __init__(self) -> None:
        self.stack: list[int] = []
        self.min_stack: list[int] = []

    def push(self, val: int) -> None:
        self.stack.append(val)
        if not self.min_stack or val <= self.min_stack[-1]:
            self.min_stack.append(val)

    def pop(self) -> None:
        val = self.stack.pop()
        if val == self.min_stack[-1]:
            self.min_stack.pop()

    def top(self) -> int:
        return self.stack[-1]

    def get_min(self) -> int:
        return self.min_stack[-1]
