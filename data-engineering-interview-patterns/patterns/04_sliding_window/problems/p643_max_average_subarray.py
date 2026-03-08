"""
LeetCode 643: Maximum Average Subarray I

Pattern: Sliding Window - Fixed Size
Difficulty: Easy
Time Complexity: O(n)
Space Complexity: O(1)
"""


def find_max_average(nums: list[int], k: int) -> float:
    """
    Find the contiguous subarray of length k with the highest average.

    Fixed-size sliding window: compute the sum of the first k elements,
    then slide by adding the new element and removing the old one.

    Args:
        nums: List of integers.
        k: Window size.

    Returns:
        Maximum average as a float.

    Example:
        >>> find_max_average([1, 12, -5, -6, 50, 3], 4)
        12.75
    """
    window_sum = sum(nums[:k])
    max_sum = window_sum

    for i in range(k, len(nums)):
        window_sum += nums[i] - nums[i - k]
        max_sum = max(max_sum, window_sum)

    return max_sum / k


def find_max_average_brute(nums: list[int], k: int) -> float:
    """
    Brute force: compute average of every subarray of size k. O(n * k).
    """
    max_avg = float("-inf")
    for i in range(len(nums) - k + 1):
        avg = sum(nums[i : i + k]) / k
        max_avg = max(max_avg, avg)
    return max_avg


if __name__ == "__main__":
    test_cases = [
        ([1, 12, -5, -6, 50, 3], 4, 12.75),
        ([5], 1, 5.0),
        ([0, 4, 0, 3, 2], 1, 4.0),
    ]

    for nums, k, expected in test_cases:
        result = find_max_average(nums, k)
        status = "PASS" if abs(result - expected) < 1e-5 else "FAIL"
        print(f"{status}: find_max_average({nums}, {k}) = {result}")
