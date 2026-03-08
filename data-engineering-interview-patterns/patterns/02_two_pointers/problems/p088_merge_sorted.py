"""
LeetCode 88: Merge Sorted Array

Pattern: Two Pointers - Two Sequences (Reverse Direction)
Difficulty: Easy
Time Complexity: O(n + m)
Space Complexity: O(1)
"""


def merge_sorted_array(
    nums1: list[int], m: int, nums2: list[int], n: int
) -> None:
    """
    Merge nums2 into nums1 in-place. nums1 has trailing zeros as placeholders.

    Args:
        nums1: First sorted array with m elements followed by n zeros
        m: Number of real elements in nums1
        nums2: Second sorted array with n elements
        n: Number of elements in nums2

    Returns:
        None (modifies nums1 in place)

    Example:
        >>> nums1 = [1, 3, 5, 0, 0, 0]
        >>> merge_sorted_array(nums1, 3, [2, 4, 6], 3)
        >>> nums1
        [1, 2, 3, 4, 5, 6]
    """
    p1 = m - 1
    p2 = n - 1
    write = m + n - 1

    while p2 >= 0:
        if p1 >= 0 and nums1[p1] > nums2[p2]:
            nums1[write] = nums1[p1]
            p1 -= 1
        else:
            nums1[write] = nums2[p2]
            p2 -= 1
        write -= 1


def merge_new_array(nums1: list[int], nums2: list[int]) -> list[int]:
    """
    Merge two sorted arrays into a new sorted array.

    Simpler version that creates a new list. Useful when
    in-place isn't required.

    Time: O(n + m)  Space: O(n + m)
    """
    result: list[int] = []
    i, j = 0, 0

    while i < len(nums1) and j < len(nums2):
        if nums1[i] <= nums2[j]:
            result.append(nums1[i])
            i += 1
        else:
            result.append(nums2[j])
            j += 1

    result.extend(nums1[i:])
    result.extend(nums2[j:])
    return result


if __name__ == "__main__":
    nums1 = [1, 2, 3, 0, 0, 0]
    merge_sorted_array(nums1, 3, [2, 5, 6], 3)
    print(f"In-place merge: {nums1}")
    assert nums1 == [1, 2, 2, 3, 5, 6]

    result = merge_new_array([1, 3, 5], [2, 4, 6])
    print(f"New array merge: {result}")
    assert result == [1, 2, 3, 4, 5, 6]
