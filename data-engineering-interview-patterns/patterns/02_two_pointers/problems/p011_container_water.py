"""
LeetCode 11: Container With Most Water

Pattern: Two Pointers - Opposite Ends (Greedy)
Difficulty: Medium
Time Complexity: O(n)
Space Complexity: O(1)
"""


def max_area(height: list[int]) -> int:
    """
    Find two lines that together with the x-axis form a container
    holding the most water.

    Opposite-end pointers with a greedy choice: always move the
    shorter line inward. Moving the taller line can never increase
    the area (the water level is limited by the shorter line, and
    the width is decreasing).

    Args:
        height: List of non-negative integers representing line heights.

    Returns:
        Maximum area of water the container can hold.

    Example:
        >>> max_area([1, 8, 6, 2, 5, 4, 8, 3, 7])
        49
    """
    left, right = 0, len(height) - 1
    best = 0

    while left < right:
        width = right - left
        h = min(height[left], height[right])
        best = max(best, width * h)

        # Move the shorter line inward
        if height[left] <= height[right]:
            left += 1
        else:
            right -= 1

    return best


def max_area_brute(height: list[int]) -> int:
    """
    Brute force: check every pair.

    Time: O(n²)  Space: O(1)
    """
    best = 0
    n = len(height)
    for i in range(n):
        for j in range(i + 1, n):
            area = (j - i) * min(height[i], height[j])
            best = max(best, area)
    return best


if __name__ == "__main__":
    test_cases = [
        ([1, 8, 6, 2, 5, 4, 8, 3, 7], 49),
        ([1, 1], 1),
        ([4, 3, 2, 1, 4], 16),
    ]

    for heights, expected in test_cases:
        result = max_area(heights)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status}: max_area({heights}) = {result}")
