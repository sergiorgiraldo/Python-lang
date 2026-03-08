"""
LeetCode 74: Search a 2D Matrix

Pattern: Binary Search - Treat 2D as Sorted 1D
Difficulty: Medium
Time Complexity: O(log(m * n))
Space Complexity: O(1)
"""


def search_matrix(matrix: list[list[int]], target: int) -> bool:
    """
    Search for target in a matrix where each row is sorted and
    the first element of each row is greater than the last element
    of the previous row.

    Treat the 2D matrix as a flattened sorted array. Convert
    1D index to row/col with divmod.

    Args:
        matrix: m x n matrix with sorted rows and row-to-row ordering.
        target: Value to find.

    Returns:
        True if target exists in the matrix.

    Example:
        >>> search_matrix([[1,3,5,7],[10,11,16,20],[23,30,34,60]], 3)
        True
    """
    if not matrix or not matrix[0]:
        return False

    m, n = len(matrix), len(matrix[0])
    left, right = 0, m * n - 1

    while left <= right:
        mid = (left + right) // 2
        row, col = divmod(mid, n)
        val = matrix[row][col]

        if val == target:
            return True
        elif val < target:
            left = mid + 1
        else:
            right = mid - 1

    return False


def search_matrix_two_binary(matrix: list[list[int]], target: int) -> bool:
    """
    Alternative: binary search for row, then binary search within row.

    Same O(log(m * n)) = O(log m + log n) complexity but sometimes
    clearer to reason about.
    """
    if not matrix or not matrix[0]:
        return False

    m, n = len(matrix), len(matrix[0])

    # Find the row where target could be
    top, bottom = 0, m - 1
    while top <= bottom:
        mid_row = (top + bottom) // 2
        if matrix[mid_row][0] > target:
            bottom = mid_row - 1
        elif matrix[mid_row][-1] < target:
            top = mid_row + 1
        else:
            # Target is in this row's range
            break
    else:
        return False  # No valid row found

    # Binary search within the row
    row = (top + bottom) // 2
    left, right = 0, n - 1
    while left <= right:
        mid = (left + right) // 2
        if matrix[row][mid] == target:
            return True
        elif matrix[row][mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return False


if __name__ == "__main__":
    matrix = [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]]
    test_cases = [
        (matrix, 3, True),
        (matrix, 13, False),
        (matrix, 1, True),
        (matrix, 60, True),
        ([[1]], 1, True),
        ([[1]], 2, False),
        ([], 1, False),
    ]

    for mat, target, expected in test_cases:
        result = search_matrix(mat, target)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status}: search_matrix(..., {target}) = {result}")
