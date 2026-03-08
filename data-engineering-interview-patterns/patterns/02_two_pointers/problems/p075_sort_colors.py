"""
LeetCode 75: Sort Colors (Dutch National Flag)

Pattern: Two Pointers - Three-Way Partition
Difficulty: Medium
Time Complexity: O(n)
Space Complexity: O(1)
"""


def sort_colors(nums: list[int]) -> None:
    """
    Sort an array containing only 0s, 1s and 2s in place.

    Uses the Dutch National Flag algorithm with three pointers:
    - low: boundary for 0s (everything before low is 0)
    - mid: current element being examined
    - high: boundary for 2s (everything after high is 2)

    Args:
        nums: List containing only 0, 1 and 2 (modified in place).

    Example:
        >>> nums = [2, 0, 2, 1, 1, 0]
        >>> sort_colors(nums)
        >>> nums
        [0, 0, 1, 1, 2, 2]
    """
    low, mid, high = 0, 0, len(nums) - 1

    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1
            mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:  # nums[mid] == 2
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1
            # Don't advance mid - the swapped element hasn't been examined


def sort_colors_counting(nums: list[int]) -> None:
    """
    Two-pass counting approach for comparison.

    Count occurrences of each value, then overwrite the array.
    Simpler but requires two passes.

    Time: O(n)  Space: O(1)
    """
    counts = [0, 0, 0]
    for num in nums:
        counts[num] += 1

    idx = 0
    for val in range(3):
        for _ in range(counts[val]):
            nums[idx] = val
            idx += 1


if __name__ == "__main__":
    test_cases = [
        ([2, 0, 2, 1, 1, 0], [0, 0, 1, 1, 2, 2]),
        ([2, 0, 1], [0, 1, 2]),
        ([0], [0]),
        ([1, 0], [0, 1]),
    ]

    for nums, expected in test_cases:
        original = nums.copy()
        sort_colors(nums)
        status = "PASS" if nums == expected else "FAIL"
        print(f"{status}: sort_colors({original}) -> {nums}")
