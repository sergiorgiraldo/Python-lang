"""
LeetCode 239: Sliding Window Maximum

Pattern: Sliding Window - Fixed Size + Monotonic Deque
Difficulty: Hard
Time Complexity: O(n)
Space Complexity: O(k)
"""

from collections import deque


def max_sliding_window(nums: list[int], k: int) -> list[int]:
    """
    Return the maximum value in each window of size k.

    Uses a monotonic decreasing deque. The deque stores indices,
    and the values at those indices are always in decreasing order.
    The front of the deque is always the current window's maximum.

    Why it works: when a new element arrives that's larger than
    elements at the back of the deque, those elements can never
    be the maximum of any future window (they're smaller AND
    older). So we remove them.

    Args:
        nums: Input array.
        k: Window size.

    Returns:
        List of maximum values, one per window position.

    Example:
        >>> max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3)
        [3, 3, 5, 5, 6, 7]
    """
    dq: deque[int] = deque()  # Stores indices, values are decreasing
    result = []

    for i in range(len(nums)):
        # Remove indices outside the window
        while dq and dq[0] <= i - k:
            dq.popleft()

        # Remove indices whose values are <= current
        # (they can never be the max of any future window)
        while dq and nums[dq[-1]] <= nums[i]:
            dq.pop()

        dq.append(i)

        # Window is full, record the maximum (front of deque)
        if i >= k - 1:
            result.append(nums[dq[0]])

    return result


def max_sliding_window_brute(nums: list[int], k: int) -> list[int]:
    """Brute force: compute max of each window. O(n * k)."""
    if not nums or k == 0:
        return []
    return [max(nums[i : i + k]) for i in range(len(nums) - k + 1)]


if __name__ == "__main__":
    test_cases = [
        ([1, 3, -1, -3, 5, 3, 6, 7], 3, [3, 3, 5, 5, 6, 7]),
        ([1], 1, [1]),
        ([1, -1], 1, [1, -1]),
        ([9, 8, 7, 6, 5], 3, [9, 8, 7]),
    ]

    for nums, k, expected in test_cases:
        result = max_sliding_window(nums, k)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status}: max_sliding_window({nums}, {k}) = {result}")
