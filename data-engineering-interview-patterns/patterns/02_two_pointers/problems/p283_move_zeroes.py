"""
LeetCode 283: Move Zeroes

Pattern: Two Pointers - Same Direction (Partition)
Difficulty: Easy
Time Complexity: O(n)
Space Complexity: O(1)
"""


def move_zeroes(nums: list[int]) -> None:
    """
    Move all zeroes to the end while maintaining relative order of non-zero elements.

    Uses a write pointer that tracks where the next non-zero should go.
    After placing all non-zero elements, fill the rest with zeros.

    Args:
        nums: List of integers (modified in place).

    Example:
        >>> nums = [0, 1, 0, 3, 12]
        >>> move_zeroes(nums)
        >>> nums
        [1, 3, 12, 0, 0]
    """
    write = 0

    # Move all non-zero elements to the front
    for read in range(len(nums)):
        if nums[read] != 0:
            nums[write] = nums[read]
            write += 1

    # Fill the rest with zeros
    while write < len(nums):
        nums[write] = 0
        write += 1


def move_zeroes_swap(nums: list[int]) -> None:
    """
    Swap-based variant that does fewer writes.

    Instead of overwriting and zeroing at the end, swap non-zero
    elements with the write position. Each element moves at most once.
    """
    write = 0
    for read in range(len(nums)):
        if nums[read] != 0:
            nums[write], nums[read] = nums[read], nums[write]
            write += 1


if __name__ == "__main__":
    test_cases = [
        ([0, 1, 0, 3, 12], [1, 3, 12, 0, 0]),
        ([0], [0]),
        ([1, 2, 3], [1, 2, 3]),
    ]

    for nums, expected in test_cases:
        original = nums.copy()
        move_zeroes(nums)
        status = "PASS" if nums == expected else "FAIL"
        print(f"{status}: move_zeroes({original}) -> {nums}")
