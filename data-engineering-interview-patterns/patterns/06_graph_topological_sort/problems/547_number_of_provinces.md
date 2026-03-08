# Number of Provinces (LeetCode #547)

🔗 [LeetCode 547: Number of Provinces](https://leetcode.com/problems/number-of-provinces/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

## Problem Statement

There are n cities. Some are connected directly, some indirectly, some not at all. A province is a group of directly or indirectly connected cities. Given an n x n adjacency matrix `isConnected` where `isConnected[i][j] = 1` means cities i and j are directly connected, return the number of provinces.

This is the same as LeetCode 323 (Number of Connected Components in an Undirected Graph) but with a different input format. 323 uses an edge list; 547 uses an adjacency matrix.

**Example:**
```
Input: isConnected = [[1,1,0],[1,1,0],[0,0,1]]
Output: 2
Explanation: Cities 0 and 1 are connected (one province). City 2 is alone (second province).
```

**Constraints:**
- 1 <= n <= 200
- isConnected[i][i] == 1 (every city is connected to itself)
- isConnected[i][j] == isConnected[j][i] (undirected)

---

## Thought Process

1. **Clarify** - This is an undirected graph. The adjacency matrix is symmetric. We need to count connected components.
2. **Three approaches** - BFS/DFS from each unvisited node (same as Islands), or Union-Find.
3. **Key insight** - Same algorithm as Number of Islands but the graph is given as an adjacency matrix instead of a grid. The mechanics are identical: visit unvisited nodes, explore their component, count how many explorations you start.

---

## Worked Example

Same concept as Number of Islands but with an adjacency matrix instead of a grid. Each row/column represents a city. `isConnected[i][j]=1` means cities i and j are directly connected. A "province" is a connected component - a group of cities reachable from each other.

```
Input (adjacency matrix):
  [[1,1,0,0,0],
   [1,1,1,0,0],
   [0,1,1,0,0],
   [0,0,0,1,1],
   [0,0,0,1,1]]

Cities: 0,1,2,3,4

  City 0: unvisited → NEW PROVINCE #1
    BFS from 0: neighbors = {1}. From 1: neighbors = {0,2}. From 2: neighbors = {1}.
    Visited: {0, 1, 2}

  City 1: already visited → skip
  City 2: already visited → skip

  City 3: unvisited → NEW PROVINCE #2
    BFS from 3: neighbors = {4}. From 4: neighbors = {3}.
    Visited: {0, 1, 2, 3, 4}

  City 4: already visited → skip

Answer: 2 provinces. Province 1: {0,1,2}. Province 2: {3,4}.
```

---

## Approaches

### Approach 1: BFS

<details>
<summary>📝 Explanation</summary>

Same connected-component counting as Number of Islands, but the input is an adjacency matrix instead of a grid. For each unvisited city, start BFS/DFS and mark all reachable cities as visited. Each time you start a new traversal, that's a new province.

The adjacency matrix tells you neighbors directly: city j is a neighbor of city i if `isConnected[i][j] == 1`.

**Time:** O(n²) - checking the adjacency matrix for each city's neighbors is O(n), and we do this for each of n cities.
**Space:** O(n) - visited set and queue/stack.

</details>

<details>
<summary>💻 Code</summary>

```python
from collections import deque

def find_circle_num_bfs(is_connected):
    n = len(is_connected)
    visited = set()
    provinces = 0

    for city in range(n):
        if city not in visited:
            provinces += 1
            queue = deque([city])
            visited.add(city)
            while queue:
                current = queue.popleft()
                for neighbor in range(n):
                    if is_connected[current][neighbor] == 1 and neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
    return provinces
```

</details>

---

### Approach 2: DFS

<details>
<summary>📝 Explanation</summary>

Same connected-component counting logic as BFS but with recursive DFS. For each unvisited city, call a recursive function that marks the city as visited and recurses on all unvisited neighbors.

Recursive DFS is more concise than BFS (no explicit queue management) and reads more naturally. The tradeoff is recursion depth: for n=200 cities in a single chain, the call stack goes 200 deep, which is well within Python's default limit of 1000.

**Time:** O(n²) - same as BFS. Checking neighbors in the adjacency matrix is O(n) per city.
**Space:** O(n) - visited set plus recursion stack (at most n frames deep).

</details>

<details>
<summary>💻 Code</summary>

```python
def find_circle_num_dfs(is_connected):
    n = len(is_connected)
    visited = set()
    provinces = 0

    def dfs(city):
        visited.add(city)
        for neighbor in range(n):
            if is_connected[city][neighbor] == 1 and neighbor not in visited:
                dfs(neighbor)

    for city in range(n):
        if city not in visited:
            provinces += 1
            dfs(city)
    return provinces
```

</details>

---

### Approach 3: Union-Find

<details>
<summary>💡 Hint</summary>

Instead of exploring components, merge them. For each edge, union the two endpoints. The final number of distinct roots is the component count.

</details>

<details>
<summary>📝 Explanation</summary>

Union-Find (Disjoint Set Union) maintains a forest of trees where each tree is a component. For each edge (i, j) in the adjacency matrix, union i and j. Path compression and union by rank keep operations nearly O(1).

**Time:** O(n^2 × α(n)) where α is the inverse Ackermann function (effectively constant)
**Space:** O(n)

Union-Find is worth knowing because it handles dynamic connectivity: you can add edges and query components incrementally. BFS/DFS requires restarting from scratch.

</details>

<details>
<summary>💻 Code</summary>

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.count = n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry: return
        if self.rank[rx] < self.rank[ry]: rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]: self.rank[rx] += 1
        self.count -= 1

def find_circle_num_union_find(is_connected):
    n = len(is_connected)
    uf = UnionFind(n)
    for i in range(n):
        for j in range(i + 1, n):
            if is_connected[i][j] == 1:
                uf.union(i, j)
    return uf.count
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| All separate | `[[1,0,0],[0,1,0],[0,0,1]]` | `3` | No connections |
| All connected | `[[1,1,1],[1,1,1],[1,1,1]]` | `1` | One big province |
| Single city | `[[1]]` | `1` | Minimal input |
| Chain | 1→2→3, 4 alone | `2` | Transitive connectivity |

---

## Common Pitfalls

1. **Scanning the full row for BFS/DFS** - Unlike grid problems with 4 neighbors, the adjacency matrix requires checking all n columns for each city. This is O(n) per city, leading to O(n^2) total.
2. **Not handling self-loops** - `isConnected[i][i] = 1` always. Don't count this as an edge to a neighbor.
3. **Union-Find without path compression** - Without optimization, Union-Find degrades to O(n) per operation. Path compression keeps it nearly O(1).

---

## Interview Tips

**What to say:**
> "This is a connected components problem. I can use BFS, DFS or Union-Find. All three are O(n^2) on an adjacency matrix since we need to read every entry. I'll go with BFS for clarity."

**Common follow-ups:**
- "When would you use Union-Find over BFS/DFS?" → When edges arrive incrementally (streaming). Union-Find handles dynamic connectivity without restarting from scratch.
- "Can you optimize the O(n^2) scan?" → Not with an adjacency matrix - you have to read it all. With an adjacency list (edge list), BFS/DFS is O(V + E) which can be much less than O(n^2) for sparse graphs.

**What the interviewer evaluates:** BFS/DFS on disconnected graphs (iterating over all nodes, starting new traversals for unvisited ones) tests completeness. The Union-Find alternative tests whether you know specialized data structures. At principal level, discussing entity resolution and the "giant component" problem shows you've dealt with real-world graph challenges.

---

## DE Application

Connected components is the core algorithm behind:
- **Entity resolution:** Grouping records that refer to the same real-world entity (customer deduplication across systems)
- **Data lineage grouping:** Finding isolated clusters in a table dependency graph
- **User graph analysis:** Identifying user communities or social clusters
- **Impact analysis:** Which tables are in the same "blast radius" when a source changes?

Union-Find is particularly useful in DE for incremental entity resolution: as new records arrive, union them with existing matches without re-scanning all previous records.

## At Scale

Finding connected components with DFS/BFS uses O(V + E) time and O(V) memory. For the Union-Find approach, the memory is O(V) with near-O(1) amortized operations per edge. At 10M nodes and 50M edges, both approaches complete in seconds on a single machine. At 1B+ nodes, you need distributed algorithms: GraphX's connectedComponents or iterative label propagation. Entity resolution (matching duplicate records across datasets) is the most common large-scale connected components problem in DE. Spark's GraphFrames library provides connected components out of the box. The key challenge at scale is handling the "giant component" problem: if many records are transitively connected, one component dominates and creates partition skew.

---

## Related Problems

- [200. Number of Islands](200_number_of_islands.md) - Connected components on a grid
- [207. Course Schedule](207_course_schedule.md) - Directed graph, different problem (cycle detection)
- [133. Clone Graph](133_clone_graph.md) - Traversal with reconstruction
