"""
Two Pointers Pattern - Reusable Templates

Three core variants:
1. Opposite ends - converging pointers on sorted data
2. Same direction - read/write or fast/slow
3. Two sequences - merging or comparing sorted inputs
"""


def opposite_ends_pair_sum(arr: list[int], target: int) -> list[int]:
    """
    Find a pair in a sorted array that sums to target.

    Two pointers start at opposite ends and converge.
    If the sum is too small, move left pointer right.
    If the sum is too large, move right pointer left.

    Time: O(n)  Space: O(1)
    Requires: sorted input
    """
    left, right = 0, len(arr) - 1

    while left < right:
        current_sum = arr[left] + arr[right]
        if current_sum == target:
            return [left, right]
        elif current_sum < target:
            left += 1
        else:
            right -= 1

    return []


def remove_duplicates_sorted(arr: list[int]) -> int:
    """
    Remove duplicates from a sorted array in place.

    Write pointer tracks where the next unique element goes.
    Read pointer scans ahead looking for new values.

    Time: O(n)  Space: O(1)
    Returns: new length (elements beyond this are garbage)
    """
    if not arr:
        return 0

    write = 1
    for read in range(1, len(arr)):
        if arr[read] != arr[read - 1]:
            arr[write] = arr[read]
            write += 1

    return write


def merge_sorted(a: list[int], b: list[int]) -> list[int]:
    """
    Merge two sorted arrays into a single sorted array.

    Compare elements at each pointer, take the smaller one,
    advance that pointer. Append any remaining elements.

    Time: O(n + m)  Space: O(n + m) for the result
    """
    result: list[int] = []
    i, j = 0, 0

    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            result.append(a[i])
            i += 1
        else:
            result.append(b[j])
            j += 1

    result.extend(a[i:])
    result.extend(b[j:])
    return result


def partition_by_predicate(arr: list[int], predicate: callable) -> int:
    """
    Partition array so elements matching predicate come first.

    Similar to quicksort's partition step. Returns the index
    where the second group starts.

    Time: O(n)  Space: O(1)
    """
    write = 0
    for read in range(len(arr)):
        if predicate(arr[read]):
            arr[write], arr[read] = arr[read], arr[write]
            write += 1
    return write
