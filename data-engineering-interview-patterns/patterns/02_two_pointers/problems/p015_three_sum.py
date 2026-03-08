"""
LeetCode 15: 3Sum

Pattern: Two Pointers - Sort + Opposite Ends (nested)
Difficulty: Medium
Time Complexity: O(n²)
Space Complexity: O(1) extra (O(n) for sort depending on implementation)
"""


def three_sum(nums: list[int]) -> list[list[int]]:
    """
    Find all unique triplets that sum to zero.

    Sort the array first, then for each element, use two pointers
    on the remaining elements to find pairs that sum to its negation.
    Skip duplicates at each level to avoid duplicate triplets.

    Args:
        nums: List of integers.

    Returns:
        List of unique triplets summing to zero.

    Example:
        >>> three_sum([-1, 0, 1, 2, -1, -4])
        [[-1, -1, 2], [-1, 0, 1]]
    """
    nums.sort()
    result: list[list[int]] = []
    n = len(nums)

    for i in range(n - 2):
        # Skip duplicates for the first element
        if i > 0 and nums[i] == nums[i - 1]:
            continue

        # Early termination: if smallest possible sum is positive, stop
        if nums[i] > 0:
            break

        left, right = i + 1, n - 1
        target = -nums[i]

        while left < right:
            current = nums[left] + nums[right]
            if current == target:
                result.append([nums[i], nums[left], nums[right]])
                # Skip duplicates for second element
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                # Skip duplicates for third element
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                left += 1
                right -= 1
            elif current < target:
                left += 1
            else:
                right -= 1

    return result


if __name__ == "__main__":
    test_cases = [
        ([-1, 0, 1, 2, -1, -4], [[-1, -1, 2], [-1, 0, 1]]),
        ([0, 1, 1], []),
        ([0, 0, 0], [[0, 0, 0]]),
    ]

    for nums, expected in test_cases:
        result = three_sum(nums)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status}: three_sum({nums}) = {result}")
