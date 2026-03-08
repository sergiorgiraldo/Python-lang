"""
Binary Search Pattern - Reusable Templates

Three core variants that cover most binary search problems:
1. Exact match - find a specific target
2. Left boundary - find first element >= target (insertion point)
3. Binary search on answer - find minimum feasible value in a range

The left boundary variant is the most versatile. It handles insertion
points, lower bounds and "find first where condition is true" problems.
The exact match variant is simpler but only works when you need an
exact value.
"""

from collections.abc import Callable


def binary_search_exact(arr: list[int], target: int) -> int:
    """
    Find the index of target in a sorted array.

    Returns -1 if not found. This is the classic textbook version.

    Invariant: target, if it exists, is always within [left, right].
    Loop ends when left > right (search space is empty).

    Time: O(log n)  Space: O(1)
    """
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1


def binary_search_left_bound(arr: list[int], target: int) -> int:
    """
    Find the leftmost position where arr[i] >= target.

    This is the insertion point: where you'd insert target to keep
    the array sorted. Equivalent to bisect.bisect_left().

    If target is smaller than all elements, returns 0.
    If target is larger than all elements, returns len(arr).

    Invariant: answer is always within [left, right].
    Loop ends when left == right (converged on the answer).

    Time: O(log n)  Space: O(1)
    """
    left, right = 0, len(arr)  # right = len(arr), not len(arr) - 1

    while left < right:  # < not <=
        mid = (left + right) // 2
        if arr[mid] < target:
            left = mid + 1
        else:
            right = mid  # mid could be the answer, don't skip it

    return left


def binary_search_right_bound(arr: list[int], target: int) -> int:
    """
    Find the rightmost position where arr[i] <= target.

    Returns -1 if target is smaller than all elements.
    Equivalent to bisect.bisect_right() - 1.

    Time: O(log n)  Space: O(1)
    """
    left, right = 0, len(arr) - 1
    result = -1

    while left <= right:
        mid = (left + right) // 2
        if arr[mid] <= target:
            result = mid
            left = mid + 1
        else:
            right = mid - 1

    return result


def binary_search_on_answer(
    low: int,
    high: int,
    is_feasible: Callable[[int], bool],
) -> int:
    """
    Find the minimum value in [low, high] where is_feasible returns True.

    Assumes monotonicity: if is_feasible(x) is True, then
    is_feasible(x+1) is also True. (Or the reverse for maximization.)

    This variant searches over possible answers, not array indices.
    Used for problems like: "What's the minimum speed to finish in K hours?"

    Time: O(log(high - low) * cost_of_is_feasible)
    Space: O(1)
    """
    while low < high:
        mid = (low + high) // 2
        if is_feasible(mid):
            high = mid  # mid works, try smaller
        else:
            low = mid + 1  # mid doesn't work, need bigger

    return low  # low == high == minimum feasible answer


# ============================================================
# When to Use Which Variant
# ============================================================
#
# Exact match:
#   - "Find target in sorted array"
#   - "Does this value exist?"
#   - Return immediately when found
#   - Loop: left <= right, move both bounds past mid
#
# Left boundary:
#   - "Find first element >= target"
#   - "Find insertion point"
#   - "Find where condition changes from False to True"
#   - Converge to boundary, don't return early
#   - Loop: left < right, set right = mid (not mid - 1)
#
# Search on answer:
#   - "Find minimum X such that condition holds"
#   - "Minimize the maximum" / "maximize the minimum"
#   - Search space is a range of values, not array indices
#   - Need a feasibility check function
#   - Same convergence logic as left boundary
#
# Python's bisect module:
#   - bisect.bisect_left() = our left_bound
#   - bisect.bisect_right() = insertion point after existing matches
#   - In interviews, implement from scratch to show understanding.
#     In production code, use bisect - it's C-implemented and faster.
