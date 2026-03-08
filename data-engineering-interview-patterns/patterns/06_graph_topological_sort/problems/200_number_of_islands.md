# Number of Islands (LeetCode #200)

🔗 [LeetCode 200: Number of Islands](https://leetcode.com/problems/number-of-islands/)

> **Difficulty:** Medium | **Interview Frequency:** Very Common

## Problem Statement

Given a 2D grid of `'1'`s (land) and `'0'`s (water), count the number of islands. An island is surrounded by water and formed by connecting adjacent land cells horizontally or vertically (not diagonally).

**Example:**
```
Input: grid = [
  ["1","1","0","0","0"],
  ["1","1","0","0","0"],
  ["0","0","1","0","0"],
  ["0","0","0","1","1"]
]
Output: 3
```

**Constraints:**
- m == grid.length, n == grid[i].length
- 1 <= m, n <= 300
- grid[i][j] is '0' or '1'

---

## Thought Process

1. **Clarify** - Diagonals don't count as connected. Each cell is a character '1' or '0' (strings, not ints).
2. **Key insight** - This is a connected components problem on a grid graph. Each cell is a node. Edges connect adjacent land cells. An island is a connected component.
3. **Approach** - Scan every cell. When we find unvisited land, start BFS/DFS to mark all cells in that island. Increment the count. The number of times we start a new BFS/DFS equals the number of islands.

---

## Worked Example

A grid of '1's (land) and '0's (water). Each connected group of land cells is an island. We count islands by scanning the grid. When we find an unvisited '1', that's a new island. We BFS/DFS from that cell to mark all connected land as visited. Each new unvisited '1' we encounter in the scan starts another island.

```
Input grid:
  1 1 0 0 1
  1 0 0 0 0
  0 0 1 1 0
  0 0 0 1 0

Scan left-to-right, top-to-bottom:
  (0,0)='1' unvisited → NEW ISLAND #1
    BFS: visit (0,0)→(0,1)→(1,0). All connected land marked.
  (0,1)='1' already visited → skip
  (0,2)='0' → skip
  (0,3)='0' → skip
  (0,4)='1' unvisited → NEW ISLAND #2
    BFS: visit (0,4). No connected land neighbors.
  (1,0)='1' already visited → skip
  ...
  (2,2)='1' unvisited → NEW ISLAND #3
    BFS: visit (2,2)→(2,3)→(3,3). All connected land marked.
  ...scan remaining, all visited or water.

Answer: 3 islands.
Each cell visited at most once during BFS + once during scan = O(m×n).
```

---

## Approaches

### Approach 1: BFS

<details>
<summary>💡 Hint</summary>

Treat the grid as a graph where each '1' cell is a node with edges to its 4 neighbors. Finding islands = finding connected components.

</details>

<details>
<summary>📝 Explanation</summary>

Scan the grid cell by cell. When you find an unvisited '1' (land), that's a new island. Start BFS from that cell: add it to a queue, mark it visited, then process the queue by checking all four neighbors (up/down/left/right). Any neighbor that's '1' and unvisited gets added to the queue and marked visited. When the queue empties, you've marked the entire island.

Continue scanning. The next unvisited '1' starts another island. Cells already visited (from earlier BFS runs) are skipped.

**Time:** O(m × n) - every cell visited at most once during scanning, at most once during BFS. Total work proportional to grid size.
**Space:** O(m × n) - the visited set. The BFS queue holds at most O(min(m, n)) entries (the diagonal of the grid).

DFS works identically - just use a stack instead of a queue (or use recursion). The choice doesn't affect correctness or complexity, only visit order.

</details>

<details>
<summary>💻 Code</summary>

```python
from collections import deque

def num_islands_bfs(grid):
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])
    visited = set()
    count = 0

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1" and (r, c) not in visited:
                count += 1
                queue = deque([(r, c)])
                visited.add((r, c))
                while queue:
                    row, col = queue.popleft()
                    for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
                        nr, nc = row+dr, col+dc
                        if 0<=nr<rows and 0<=nc<cols and grid[nr][nc]=="1" and (nr,nc) not in visited:
                            visited.add((nr, nc))
                            queue.append((nr, nc))
    return count
```

</details>

---

### Approach 2: DFS (Iterative)

<details>
<summary>📝 Explanation</summary>

Same logic as BFS but uses a stack (or recursion). When you find an unvisited '1', explore as deep as possible in one direction before backtracking. Mark each cell visited as you go.

Recursive DFS is the most concise implementation: call dfs(row, col), which marks the cell visited and recursively calls itself on all valid unvisited neighbors.

**Time:** O(m × n). **Space:** O(m × n) for visited set plus O(m × n) worst-case recursion depth (a grid that's all '1's).

Watch for recursion depth limits on large grids. Python's default recursion limit is 1000. For grids larger than ~30×30, use iterative DFS or BFS.

</details>

<details>
<summary>💻 Code</summary>

```python
def num_islands_dfs(grid):
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])
    visited = set()
    count = 0

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1" and (r, c) not in visited:
                count += 1
                stack = [(r, c)]
                visited.add((r, c))
                while stack:
                    row, col = stack.pop()
                    for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
                        nr, nc = row+dr, col+dc
                        if 0<=nr<rows and 0<=nc<cols and grid[nr][nc]=="1" and (nr,nc) not in visited:
                            visited.add((nr, nc))
                            stack.append((nr, nc))
    return count
```

</details>

---

### Approach 3: Mutate Grid (Space Optimization)

<details>
<summary>📝 Explanation</summary>

Instead of a separate visited set, mark visited cells by changing '1' to '0' as you process them. This eliminates the O(m × n) visited set since the grid itself tracks which cells have been explored.

The tradeoff is that the input grid is destroyed. In an interview, always ask whether mutating the input is acceptable before using this approach.

**Time:** O(m × n) - same as the BFS/DFS approaches. Every cell is visited at most once.
**Space:** O(min(m, n)) - only the BFS queue, which holds at most one diagonal's worth of cells. No visited set needed.

This is a common interview optimization pattern: reuse the input data structure for bookkeeping instead of allocating a separate one.

</details>

<details>
<summary>💻 Code</summary>

```python
from collections import deque

def num_islands_mutate(grid):
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])
    count = 0

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1":
                count += 1
                queue = deque([(r, c)])
                grid[r][c] = "0"
                while queue:
                    row, col = queue.popleft()
                    for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
                        nr, nc = row+dr, col+dc
                        if 0<=nr<rows and 0<=nc<cols and grid[nr][nc]=="1":
                            grid[nr][nc] = "0"
                            queue.append((nr, nc))
    return count
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Empty grid | `[]` | `0` | Guard against empty input |
| All water | `[["0","0"],["0","0"]]` | `0` | No islands |
| All land | `[["1","1"],["1","1"]]` | `1` | One big island |
| Diagonal only | `[["1","0"],["0","1"]]` | `2` | Diagonals are not connected |
| Single cell land | `[["1"]]` | `1` | Smallest possible island |
| L-shaped island | L-shape | `1` | Non-rectangular islands are still one island |

---

## Common Pitfalls

1. **Forgetting to mark as visited BEFORE enqueueing** - If you mark after dequeuing, you'll add the same cell multiple times. Always mark visited when you first discover a cell, not when you process it.
2. **Treating diagonals as connected** - The problem specifies horizontal and vertical only. Using 8 directions gives wrong answers.
3. **Not checking grid bounds** - Off-by-one in boundary checks causes index errors. The `0 <= nr < rows and 0 <= nc < cols` pattern is standard.

---

## Interview Tips

**What to say:**
> "This is a connected components problem on a grid. I'll scan every cell, and when I find unvisited land, I'll BFS to mark the entire island. The number of BFS starts equals the number of islands."

**Common follow-ups:**
- "BFS or DFS?" → Either works for counting. BFS is slightly easier to reason about for grids. DFS can cause stack overflow on very large grids if recursive.
- "Can you do it without extra space?" → Mutate the grid by turning '1' to '0' after visiting. Ask the interviewer if that's acceptable first.
- "What about larger grids?" → For very large grids, union-find gives the same result and can be parallelized more easily.

**What the interviewer evaluates:** Grid-as-graph recognition is the first test. BFS vs DFS choice and explaining the tradeoff (BFS is iterative and avoids stack overflow, DFS is simpler to write) shows maturity. The follow-up "what about very large grids?" tests whether you know Union-Find as an alternative. Mentioning entity resolution as the production equivalent shows DE depth.

---

## DE Application

Grid-based connected components show up in:
- Geospatial data: finding contiguous regions in satellite imagery or map tiles
- Data quality: identifying clusters of missing values in a dataset matrix
- Network analysis: finding isolated subnetworks in infrastructure graphs

The more direct DE application is the general connected components concept (see problem 547) applied to entity resolution, user graph analysis and data lineage.

## At Scale

BFS/DFS on a grid uses O(V) memory for the visited set. For a 10K x 10K grid (100M cells), that's ~400MB. For larger grids, connected component algorithms on distributed frameworks (GraphX, NetworkX on a single machine for millions of nodes) are needed. The practical DE equivalent is entity resolution: given records that might refer to the same entity, find connected components of matches. At 1B records with sparse connections, Union-Find (disjoint set) is more efficient than BFS because it processes edges without building the full adjacency list. Spark GraphX's connectedComponents uses the Pregel model for distributed component finding.

---

## Related Problems

- [547. Number of Provinces](547_number_of_provinces.md) - Connected components with an adjacency matrix (not a grid)
- [133. Clone Graph](133_clone_graph.md) - BFS/DFS for graph reconstruction
- [207. Course Schedule](207_course_schedule.md) - Directed graph, cycle detection
