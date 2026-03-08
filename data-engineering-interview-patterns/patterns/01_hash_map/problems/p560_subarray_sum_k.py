"""
LeetCode 560: Subarray Sum Equals K

Pattern: Hash Map - Prefix Sum + Complement Lookup
Difficulty: Medium
Time Complexity: O(n)
Space Complexity: O(n)
"""

from collections import defaultdict


def subarray_sum(nums: list[int], k: int) -> int:
    """
    Count the number of contiguous subarrays that sum to k.

    Uses prefix sums with a hash map. For each position, we compute
    the running sum. If (running_sum - k) exists as a previous prefix
    sum, then the subarray between those positions sums to k.

    This is the Two Sum pattern applied to prefix sums.

    Args:
        nums: List of integers (can include negatives).
        k: Target sum.

    Returns:
        Number of contiguous subarrays that sum to k.

    Example:
        >>> subarray_sum([1, 1, 1], 2)
        2
    """
    count = 0
    prefix_sum = 0
    # Map of prefix_sum -> how many times we've seen it
    # Initialize with {0: 1} because a prefix sum of 0 means
    # the subarray from index 0 to current sums to k
    seen: dict[int, int] = defaultdict(int)
    seen[0] = 1

    for num in nums:
        prefix_sum += num
        # If (prefix_sum - k) was a previous prefix sum, then the
        # subarray between that point and here sums to k
        count += seen[prefix_sum - k]
        seen[prefix_sum] += 1

    return count


def subarray_sum_brute(nums: list[int], k: int) -> int:
    """
    Brute force: check every subarray.

    Time: O(n²)  Space: O(1)

    For each starting index, compute running sum to every ending index.
    """
    count = 0
    n = len(nums)
    for i in range(n):
        current_sum = 0
        for j in range(i, n):
            current_sum += nums[j]
            if current_sum == k:
                count += 1
    return count


if __name__ == "__main__":
    test_cases = [
        ([1, 1, 1], 2, 2),
        ([1, 2, 3], 3, 2),
        ([1, -1, 0], 0, 3),
    ]

    for nums, k, expected in test_cases:
        result = subarray_sum(nums, k)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status}: subarray_sum({nums}, {k}) = {result}")
