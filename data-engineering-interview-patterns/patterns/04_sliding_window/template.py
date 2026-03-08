"""
Sliding Window Pattern - Reusable Templates

Two core templates:
1. Fixed-size window - window size is given, slide it across the data
2. Variable-size window - window grows/shrinks to satisfy a condition

The variable-size template is the more important one. Almost every
medium/hard sliding window problem follows the same expand-contract
structure. The only things that change are the state tracking and
the constraint check.
"""

from collections.abc import Sequence

# ============================================================
# Fixed-Size Window
# ============================================================


def fixed_window_sum(arr: Sequence[int | float], k: int) -> list[float]:
    """
    Compute the sum for each window of size k.

    Maintains a running sum. Each step adds the new element
    and removes the one that fell off the left edge.

    Time: O(n)  Space: O(1) beyond output
    """
    if len(arr) < k or k <= 0:
        return []

    results = []
    window_sum = sum(arr[:k])
    results.append(window_sum)

    for i in range(k, len(arr)):
        window_sum += arr[i] - arr[i - k]
        results.append(window_sum)

    return results


def fixed_window_max(arr: Sequence[int], k: int) -> list[int]:
    """
    Compute the maximum for each window of size k.

    Uses a monotonic deque to track potential maximums.
    Elements in the deque are indices, maintained in decreasing
    order of their values.

    Time: O(n)  Space: O(k)
    """
    from collections import deque

    if len(arr) < k or k <= 0:
        return []

    dq: deque[int] = deque()  # Indices of potential maximums
    results = []

    for i in range(len(arr)):
        # Remove elements outside the window
        while dq and dq[0] <= i - k:
            dq.popleft()

        # Remove elements smaller than current (they can't be max)
        while dq and arr[dq[-1]] <= arr[i]:
            dq.pop()

        dq.append(i)

        # Window is full, record the max (front of deque)
        if i >= k - 1:
            results.append(arr[dq[0]])

    return results


# ============================================================
# Variable-Size Window
# ============================================================


def longest_with_condition(
    arr: Sequence,
    is_valid: callable,
    add: callable,
    remove: callable,
    state_factory: callable,
) -> int:
    """
    Generic variable-size sliding window.

    Finds the longest subarray where is_valid(state) is True.

    Args:
        arr: Input sequence.
        is_valid: Function(state) -> bool. True if window is valid.
        add: Function(state, element) -> None. Add element to window state.
        remove: Function(state, element) -> None. Remove element from state.
        state_factory: Function() -> initial_state.

    Time: O(n) assuming add/remove/is_valid are O(1)
    Space: depends on state

    Example usage for "longest substring with at most k distinct chars":

        state_factory = lambda: {}
        add = lambda s, c: s.__setitem__(c, s.get(c, 0) + 1)
        remove = lambda s, c: (s.__setitem__(c, s[c] - 1),
                                s.pop(c) if s[c] == 0 else None)
        is_valid = lambda s: len(s) <= k
    """
    state = state_factory()
    left = 0
    best = 0

    for right in range(len(arr)):
        add(state, arr[right])

        while not is_valid(state):
            remove(state, arr[left])
            left += 1

        best = max(best, right - left + 1)

    return best


# ============================================================
# Choosing the Right Variant
# ============================================================
#
# Fixed-size window:
#   - "Maximum average of subarray of size k"
#   - "Find all anagrams of length m in string"
#   - "Check if duplicates exist within distance k"
#   - Window size is given or derivable from the problem
#
# Variable-size window:
#   - "Longest substring without repeating characters"
#   - "Shortest subarray with sum >= target"
#   - "Longest substring with at most K distinct chars"
#   - Need to find longest/shortest subarray meeting a condition
#
# Monotonic deque (special case of fixed window):
#   - "Maximum/minimum in each window of size k"
#   - Need running max/min, not just sum/average
#   - Elements in deque maintained in sorted order
#
# Frequency map inside window:
#   - "Find permutations/anagrams in string"
#   - "Substring containing all characters of another string"
#   - Track character counts, compare to target counts
#
# Python's itertools and pandas alternatives:
#   - itertools.islice for streaming windows
#   - pandas.Series.rolling() for fixed-window aggregations
#   - In interviews, implement from scratch. In production,
#     use the library that fits your stack.
