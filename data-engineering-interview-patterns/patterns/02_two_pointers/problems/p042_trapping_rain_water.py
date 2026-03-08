"""
LeetCode 42: Trapping Rain Water

Pattern: Two Pointers - Opposite Ends with Running Max
Difficulty: Hard
Time Complexity: O(n)
Space Complexity: O(1)
"""


def trap(height: list[int]) -> int:
    """
    Calculate how much rainwater can be trapped between bars.

    Water at each position = min(max_left, max_right) - height[position].
    The two-pointer approach tracks running max from each side and
    processes the side with the smaller max first.

    The key insight: if left_max < right_max, the water at the left
    pointer is determined by left_max (regardless of what's between
    the pointers). The right side is guaranteed to be at least right_max
    high, so left_max is the bottleneck.

    Args:
        height: List of non-negative integers representing bar heights.

    Returns:
        Total units of trapped water.

    Example:
        >>> trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1])
        6
    """
    if len(height) < 3:
        return 0

    left, right = 0, len(height) - 1
    left_max, right_max = height[left], height[right]
    water = 0

    while left < right:
        if left_max <= right_max:
            left += 1
            left_max = max(left_max, height[left])
            water += left_max - height[left]
        else:
            right -= 1
            right_max = max(right_max, height[right])
            water += right_max - height[right]

    return water


def trap_prefix_max(height: list[int]) -> int:
    """
    Prefix/suffix max approach for clarity.

    Precompute the maximum height to the left and right of each
    position. Water at each position is min(left_max, right_max) - height.

    Time: O(n)  Space: O(n) for the prefix arrays
    """
    if len(height) < 3:
        return 0

    n = len(height)
    left_max = [0] * n
    right_max = [0] * n

    left_max[0] = height[0]
    for i in range(1, n):
        left_max[i] = max(left_max[i - 1], height[i])

    right_max[n - 1] = height[n - 1]
    for i in range(n - 2, -1, -1):
        right_max[i] = max(right_max[i + 1], height[i])

    water = 0
    for i in range(n):
        water += min(left_max[i], right_max[i]) - height[i]

    return water


if __name__ == "__main__":
    test_cases = [
        ([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1], 6),
        ([4, 2, 0, 3, 2, 5], 9),
        ([1, 0, 1], 1),
        ([], 0),
    ]

    for heights, expected in test_cases:
        result = trap(heights)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status}: trap({heights}) = {result}")
