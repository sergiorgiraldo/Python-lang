# Time Complexity Cheat Sheet

Quick reference for complexity analysis during interviews.

---

## Common Time Complexities

| Complexity | Name | Intuition | Example |
|---|---|---|---|
| O(1) | Constant | Hash map lookup, array index | dict[key], arr[i] |
| O(log n) | Logarithmic | Halving the search space each step | Binary search |
| O(n) | Linear | Touch every element once | Single pass, hash map build |
| O(n log n) | Linearithmic | Sort, then linear work | Merge sort, sort + scan |
| O(n^2) | Quadratic | Nested loops | Brute force pair comparison |
| O(2^n) | Exponential | All subsets | Recursive without memoization |
| O(n * k) | Linear with parameter | k passes over n elements | Sliding window of size k |

---

## Complexity by Pattern

| Pattern | Typical Time | Typical Space | Key Operation |
|---|---|---|---|
| Hash map (build + query) | O(n) | O(n) | dict insertion/lookup |
| Two pointers (sorted) | O(n) | O(1) | Pointer movement |
| Binary search | O(log n) | O(1) | Halving |
| Binary search the answer | O(n log M) | O(1) | n=check cost, M=solution space |
| Sliding window (fixed) | O(n) | O(k) | Window slide |
| Sliding window (variable) | O(n) | O(k) or O(alphabet) | Expand/shrink |
| Heap top-k | O(n log k) | O(k) | Heap push/pop |
| Heap k-way merge | O(n log k) | O(k) | Merge step |
| BFS/DFS on graph | O(V + E) | O(V) | Visit each vertex/edge once |
| Topological sort | O(V + E) | O(V) | Kahn's or DFS |
| Sort + merge intervals | O(n log n) | O(n) | Sort dominates |
| Monotonic stack | O(n) | O(n) | Each element pushed/popped once |
| Tree traversal | O(n) | O(h) | Visit each node, stack depth = height |
| DENSE_RANK (SQL) | O(n log n) | O(n) | Sort on the rank column |
| GROUP BY (SQL) | O(n) | O(groups) | Hash aggregation |
| Window function (SQL) | O(n log n) | O(n) | Sort on partition + order keys |

---

## Data Structure Operations

| Data Structure | Access | Search | Insert | Delete | Notes |
|---|---|---|---|---|---|
| Array | O(1) | O(n) | O(n) | O(n) | O(1) append amortized |
| Hash Map | - | O(1) avg | O(1) avg | O(1) avg | O(n) worst case (rare) |
| Hash Set | - | O(1) avg | O(1) avg | O(1) avg | Same as hash map |
| Min/Max Heap | O(1) top | O(n) | O(log n) | O(log n) | O(n) to build |
| Sorted Array | O(1) | O(log n) | O(n) | O(n) | Binary search for lookup |
| Linked List | O(n) | O(n) | O(1) head | O(1) if ref | O(n) to find node |
| BST (balanced) | - | O(log n) | O(log n) | O(log n) | Degrades to O(n) if unbalanced |

---

## Sorting Algorithm Comparison

| Algorithm | Best | Average | Worst | Space | Stable | Notes |
|---|---|---|---|---|---|---|
| Python sort (Timsort) | O(n) | O(n log n) | O(n log n) | O(n) | Yes | Default, use this |
| Merge sort | O(n log n) | O(n log n) | O(n log n) | O(n) | Yes | Basis of external sort |
| Quick sort | O(n log n) | O(n log n) | O(n^2) | O(log n) | No | Fast in practice |
| Heap sort | O(n log n) | O(n log n) | O(n log n) | O(1) | No | In-place but slow constants |
| Counting sort | O(n + k) | O(n + k) | O(n + k) | O(k) | Yes | Only for bounded integers |

---

## Grounding Big-O in Real Numbers

| n | O(log n) | O(n) | O(n log n) | O(n^2) |
|---|---|---|---|---|
| 1,000 | 10 | 1,000 | 10,000 | 1,000,000 |
| 1,000,000 | 20 | 1,000,000 | 20,000,000 | 1,000,000,000,000 |
| 1,000,000,000 | 30 | 1,000,000,000 | 30,000,000,000 | Don't even try |

At ~10^8 operations per second:

| Complexity | n = 1,000 | n = 1,000,000 | n = 1,000,000,000 |
|---|---|---|---|
| O(n) | ~0.01 ms | ~10 ms | ~10 seconds |
| O(n log n) | ~0.1 ms | ~200 ms | ~5 minutes |
| O(n^2) | ~10 ms | ~3 hours | ~30 years |

---

## Interview Rules of Thumb

- 10^8 operations per second is a safe estimate for Python
- If n <= 1,000: O(n^2) is fine
- If n <= 100,000: need O(n log n) or better
- If n <= 10,000,000: need O(n) or O(n log n)
- Hash map almost always trades O(n) space for O(1) lookup time
- "Can you do better?" usually means there's an O(n) or O(n log n) solution
- "Can you do it in place?" means O(1) extra space, think two pointers or swaps

---

## SQL-Specific Complexity Notes

| SQL Operation | Engine Cost | Watch For |
|---|---|---|
| Full table scan | O(n) | SELECT * without WHERE on large tables |
| Index lookup | O(log n) | Only works with sargable predicates |
| Hash join | O(n + m) | Smaller table must fit in memory |
| Sort-merge join | O(n log n + m log m) | Preferred when both sides are large |
| Nested loop join | O(n * m) | Only efficient with index on inner table |
| Hash aggregation | O(n) | Default for GROUP BY |
| Window function | O(n log n) | Sort on PARTITION BY + ORDER BY keys |
| APPROX_COUNT_DISTINCT | O(n) time, O(1) space | ~2% error, uses HyperLogLog |
