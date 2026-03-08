# Search a 2D Matrix (LeetCode #74)

🔗 [LeetCode 74: Search a 2D Matrix](https://leetcode.com/problems/search-a-2d-matrix/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

## Problem Statement

Write an algorithm to search for a value in an m x n matrix with these properties:
- Each row is sorted in ascending order
- The first element of each row is greater than the last element of the previous row

**Example:**
```
Input: matrix = [[1,3,5,7],[10,11,16,20],[23,30,34,60]], target = 3
Output: true
```

**Constraints:**
- m == matrix.length, n == matrix[i].length
- 1 <= m, n <= 100
- -10^4 <= matrix[i][j], target <= 10^4

---

## Thought Process

1. **The matrix is effectively one sorted array** - Row-to-row ordering means if you flattened all rows into one array, it would be sorted.
2. **Map between 1D and 2D** - Index `k` in the flattened array maps to `row = k // n, col = k % n` in the matrix.
3. **Run standard binary search on the flattened indices** - Same exact match logic as #704, just with the coordinate conversion.

---

## Worked Example

The matrix is sorted row by row, and each row starts with a value larger than the previous row's last value. This means if you read the matrix left-to-right, top-to-bottom, it's one continuous sorted sequence. We can treat the 2D matrix as a 1D sorted array and do a single binary search.

The trick: convert between a 1D index and 2D (row, col) coordinates. For a matrix with `m` rows and `n` columns: `row = index // n`, `col = index % n`. For example, in a 3×4 matrix, 1D index 7 maps to row 1, col 3 (7 // 4 = 1, 7 % 4 = 3).

```
Input: matrix = [[1,  3,  5,  7],
                 [10, 11, 16, 20],
                 [23, 30, 34, 50]]
       target = 16

  m=3 rows, n=4 cols. Total elements = 12.
  Treat as 1D: [1, 3, 5, 7, 10, 11, 16, 20, 23, 30, 34, 50]

  left=0, right=11, mid=5 → row=5//4=1, col=5%4=1 → matrix[1][1] = 11
  11 < 16 → left = 6

  left=6, right=11, mid=8 → row=8//4=2, col=8%4=0 → matrix[2][0] = 23
  23 > 16 → right = 7

  left=6, right=7, mid=6 → row=6//4=1, col=6%4=2 → matrix[1][2] = 16
  16 == 16 → found it at row 1, col 2.

3 steps for a 3×4 matrix (12 elements). log₂(12) ≈ 4, so that's expected.
```

---

## Approaches

### Approach 1: Flatten to 1D Binary Search

<details>
<summary>💡 Hint</summary>

You don't need to flatten the matrix. Just treat index `mid` as a position in a virtual 1D array and convert to row/col when you need to read a value.

</details>

<details>
<summary>📝 Explanation</summary>

Since the matrix rows are sorted and each row starts larger than the previous row ends, the entire matrix is one sorted sequence read left-to-right, top-to-bottom. Apply standard binary search on the conceptual 1D array.

The only trick is index conversion. For a matrix with `n` columns:
- 1D index → 2D: `row = idx // n`, `col = idx % n`
- 2D → 1D: `idx = row * n + col`

Search range is `left = 0` to `right = m * n - 1`. At each step, convert `mid` to (row, col) to look up the value in the matrix.

**Time:** O(log(m × n)) - binary search over all elements.
**Space:** O(1) - no actual flattening, just index math.

This is the cleanest approach and what most interviewers expect. The index conversion is the only thing you need beyond standard binary search.

</details>

<details>
<summary>💻 Code</summary>

```python
def search_matrix(matrix: list[list[int]], target: int) -> bool:
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
```

</details>

### Approach 2: Binary Search Row, Then Column

<details>
<summary>📝 Explanation</summary>

Alternatively, find the correct row first, then search within that row. Two binary searches instead of one.

Step 1: Binary search on the first column to find which row the target belongs in. The target is in row `r` if `matrix[r][0] <= target <= matrix[r][n-1]`.

Step 2: Binary search within row `r` for the target.

**Time:** O(log m + log n) = O(log(m × n)) - same as the flatten approach.
**Space:** O(1).

Mathematically identical complexity, but conceptually simpler for some people since each binary search is standard. The flatten approach does it in one search instead of two.

</details>

<details>
<summary>💻 Code</summary>

```python
def search_matrix_two_binary(matrix: list[list[int]], target: int) -> bool:
    if not matrix or not matrix[0]:
        return False
    m, n = len(matrix), len(matrix[0])

    # Find the row
    top, bottom = 0, m - 1
    while top <= bottom:
        mid_row = (top + bottom) // 2
        if matrix[mid_row][0] > target:
            bottom = mid_row - 1
        elif matrix[mid_row][-1] < target:
            top = mid_row + 1
        else:
            break
    else:
        return False

    # Search within the row
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
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Found | `matrix, 3` | `True` | Standard case |
| Not found | `matrix, 13` | `False` | Between rows |
| First element | `matrix, 1` | `True` | Top-left corner |
| Last element | `matrix, 60` | `True` | Bottom-right corner |
| Row boundary | `matrix, 7` then `10` | Both `True` | Last of row / first of next |
| Single element | `[[1]], 1` | `True` | 1x1 matrix |
| Empty matrix | `[], 1` | `False` | No data |
| Single row | `[[1,3,5]], 3` | `True` | Degenerates to 1D |
| Single column | `[[1],[5],[10]], 5` | `True` | Degenerates to column scan |

---

## Common Pitfalls

1. **Confusing with LeetCode 240** - That problem has sorted rows and sorted columns but no row-to-row ordering. It needs a different approach (staircase search from top-right). Make sure you check which variant the interviewer means.
2. **Off-by-one on `m * n - 1`** - The flattened array has `m * n` elements, indexed 0 to `m * n - 1`.
3. **Empty matrix check** - Need to check both `not matrix` and `not matrix[0]` for the edge case of `[[]]`.

---

## Interview Tips

**What to say:**
> "Since each row's first element is larger than the previous row's last, the matrix is effectively one sorted array. I can binary search on the flattened index and convert to row/col with divmod."

**If the interviewer says "what if rows are sorted but the row ordering doesn't hold?"**
> "That's a different problem. I'd use a staircase search starting from the top-right corner - that gives O(m + n)."

**What the interviewer evaluates:** Can you see the flat sorted array within the 2D structure? The index math (row = mid // cols, col = mid % cols) tests whether you think in abstractions. Mentioning row group statistics and zone maps as the production equivalent shows systems awareness.

---

## DE Application

Searching structured 2D data shows up when:
- Looking up values in a partition index (partition boundaries form a sorted structure)
- Searching in columnar storage where data is sorted within and across row groups
- Any lookup in a B-tree index is conceptually similar - the tree structure maps a multi-level sorted organization to efficient binary search

The `divmod` trick for flattening coordinates is also useful for working with data stored in row-major vs column-major order.

---

## At Scale

Treating the 2D matrix as a flat sorted array (row * cols + col) is a conceptual tool. In practice, data stored in row-major order in columnar formats (Parquet, ORC) has different access patterns. Columnar storage is optimized for scanning entire columns, not random row access. Binary search on columnar data is inefficient because each comparison reads from a different row group. This is why columnar databases use min/max statistics per row group (zone maps) for pruning rather than binary search: "this row group's values range from 50-100, so skip it if looking for 42."

---

## Related Problems

- [704. Binary Search](704_binary_search.md) - Same core algorithm, simpler setting
- [35. Search Insert Position](035_search_insert.md) - Left boundary variant
- [240. Search a 2D Matrix II](https://leetcode.com/problems/search-a-2d-matrix-ii/) - Different matrix properties, needs staircase search
