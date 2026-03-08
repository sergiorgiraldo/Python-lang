# CC Prompt: Rework README - Pattern 06 Graph (BFS/DFS)

## What This Prompt Does

Rewrites the README.md "What Is It?", "Visual Aid" and "Trade-offs" sections with deep teaching.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- Only modify `patterns/06_graph_topological_sort/README.md`
- REPLACE specified sections only.
- NO Oxford commas, NO em dashes, NO exclamation points

---

## Replace `## What Is It?` (everything up to `## When to Use It`)

```markdown
## What Is It?

### The basics

A graph is a set of **nodes** (also called vertices) connected by **edges**. Unlike arrays and trees, graphs have no required structure. Nodes can connect to any number of other nodes, connections can be one-way or two-way, and there's no concept of "first" or "last."

In Python, graphs are typically represented as adjacency lists using a dict:

```python
# each key is a node, each value is a list of nodes it connects to
graph = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A", "D", "E"],
    "D": ["B", "C"],
    "E": ["C"]
}
```

This is just a dict where keys are nodes and values are lists of neighbors. Looking up a node's neighbors is O(1). If you've used a dict before, you already know the data structure.

### Directed vs undirected

An **undirected** graph has two-way connections: if A connects to B, then B connects to A. Like a road between two cities.

A **directed** graph has one-way connections: A→B doesn't mean B→A. Like a one-way street or a dependency ("task B depends on task A" doesn't mean A depends on B).

```python
# undirected: add both directions
graph["A"].append("B")
graph["B"].append("A")

# directed: add only one direction
graph["A"].append("B")  # A → B, but B does NOT point to A
```

Most data engineering graph problems involve directed graphs because dependencies, pipelines and data lineage are naturally one-directional.

### BFS: explore level by level

**Breadth-first search** starts at a node and explores all its immediate neighbors first, then all *their* neighbors, then the next level out. Think of ripples spreading from a stone dropped in water.

Implementation uses a **queue** (FIFO: first in, first out):

```python
from collections import deque

def bfs(graph, start):
    visited = set()
    queue = deque([start])
    visited.add(start)
    while queue:
        node = queue.popleft()  # process oldest item first
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
```

BFS naturally finds the **shortest path** (fewest edges) between two nodes. Level 1 is distance 1, level 2 is distance 2, and so on. If you find your target at level 3, there's no shorter path (you already checked levels 1 and 2).

### DFS: explore as deep as possible

**Depth-first search** picks one neighbor and follows that path as far as it goes before backtracking to try other paths. Think of exploring a maze by always turning left until you hit a dead end, then backing up.

Implementation uses a **stack** (LIFO: last in, first out) or recursion (which uses the call stack):

```python
def dfs(graph, start):
    visited = set()
    stack = [start]
    while stack:
        node = stack.pop()  # process newest item first
        if node not in visited:
            visited.add(node)
            for neighbor in graph[node]:
                stack.append(neighbor)
```

The only difference from BFS in code: `stack.pop()` instead of `queue.popleft()`. That one change completely changes the exploration order.

DFS is useful for detecting cycles, computing topological order and any problem where you need to fully explore one path before trying others.

### BFS vs DFS: when to use which

| Use BFS when | Use DFS when |
|---|---|
| Finding shortest path (fewest edges) | Detecting cycles |
| Level-order exploration | Exploring all paths to completion |
| "Minimum steps to reach X" | Topological sorting |
| Ripple-out from a starting point | "Does a path exist from A to B?" |

Both visit every reachable node exactly once. Both are O(V + E) where V is the number of nodes (vertices) and E is the number of edges. The difference is the *order* of exploration.

### Topological sort: ordering dependencies

A **topological sort** arranges nodes in a directed graph so that every node comes after all the nodes it depends on. It only works on **DAGs** (directed acyclic graphs). If there's a cycle (A depends on B, B depends on C, C depends on A), no valid ordering exists.

This is the most directly relevant graph algorithm for data engineering. Pipeline execution order, table build dependencies and package installation order are all topological sorts.

**Kahn's algorithm** (BFS-based) is the most intuitive implementation:
1. Count the in-degree (number of incoming edges) for each node.
2. Add all nodes with in-degree 0 to a queue (they have no dependencies).
3. Process the queue: for each node, add it to the result, then decrement the in-degree of all its dependents. If any dependent's in-degree drops to 0, add it to the queue.
4. If the result contains all nodes, you have a valid topological order. If not, there's a cycle.

### Cycle detection

If a topological sort can't include all nodes, there's a cycle. Kahn's algorithm detects this automatically (step 4).

For explicit cycle detection, DFS with three states works:
- **Unvisited** (white): haven't started processing this node
- **In progress** (gray): currently exploring this node's descendants
- **Completed** (black): finished exploring all descendants

If DFS reaches a gray node (a node we're currently in the middle of processing), we've found a cycle - we've followed edges back to a node on the current path.

### Connection to data engineering

Graphs show up constantly in data engineering:

- **Pipeline DAGs:** Airflow, dbt, Prefect and Dagster all model task dependencies as directed graphs. Topological sort determines execution order.
- **Table lineage:** "table C depends on tables A and B" is a graph. Impact analysis (what breaks if I change table A?) is graph traversal.
- **Schema dependencies:** Foreign key relationships form a graph. Determining safe migration order is topological sort.
- **Dependency resolution:** Package managers (pip, npm) use topological sort to install dependencies before the packages that need them.

### What the problems in this section use

| Problem | Algorithm | Graph type | What it models |
|---|---|---|---|
| Number of Islands | BFS or DFS | Implicit grid graph | Connected component counting |
| Number of Provinces | BFS or DFS | Adjacency matrix | Connected component counting |
| Clone Graph | BFS or DFS | Undirected adjacency list | Deep copy with reference tracking |
| Course Schedule | Topological sort / cycle detection | Directed prerequisite graph | "Can I finish all courses?" |
| Course Schedule II | Topological sort (Kahn's) | Directed prerequisite graph | "In what order should I take courses?" |
| Alien Dictionary | Topological sort | Directed character-ordering graph | Infer ordering rules from examples |
| Network Delay Time | Dijkstra's (BFS + heap) | Weighted directed graph | Shortest path with edge weights |
```

## Replace `## Visual Aid` (up to `## Template`)

```markdown
## Visual Aid

```
BFS vs DFS on the same graph:

    A
   / \
  B   C
 / \   \
D   E   F

BFS (level by level, using a queue):
  Level 0: A
  Level 1: B, C
  Level 2: D, E, F
  Visit order: A → B → C → D → E → F

DFS (deep first, using a stack):
  Follow A→B→D (dead end), backtrack to B→E (dead end),
  backtrack to A→C→F (dead end). Done.
  Visit order: A → B → D → E → C → F

Topological Sort (pipeline dependencies):

  extract → transform → validate → load
                    ↘           ↗
                   clean_nulls

  In-degrees: extract=0, transform=1, clean_nulls=1, validate=2, load=1
  Start with in-degree 0: [extract]
  Process extract → transform and clean_nulls drop to in-degree 0
  Process transform → validate drops to 1
  Process clean_nulls → validate drops to 0
  Process validate → load drops to 0
  Process load → done

  Valid order: extract, transform, clean_nulls, validate, load
  (transform and clean_nulls could swap - both have in-degree 0 at the same time)
```
```

## Replace `## Trade-offs` (up to `## Problems in This Section`)

```markdown
## Trade-offs

**BFS vs DFS trade-offs:**
- BFS uses O(W) memory where W is the maximum width of the graph (the largest level). DFS uses O(D) memory where D is the maximum depth. For wide, shallow graphs, DFS uses less memory. For deep, narrow graphs, BFS uses less.
- BFS finds the shortest path by edges. DFS does not (it might find a longer path first).
- DFS is simpler to implement recursively. BFS requires an explicit queue.

**Adjacency list vs adjacency matrix:**
- Adjacency list (dict of lists): O(V + E) space, efficient for sparse graphs. This is what you'll use 99% of the time.
- Adjacency matrix (2D array): O(V²) space, efficient only for dense graphs. Rarely used in practice.

**When graphs don't apply:**
- If the data is inherently linear or sorted, arrays and two-pointer techniques are simpler.
- If relationships are hierarchical with no cross-links, a tree is a better model (simpler traversal, no cycle concerns).
```

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns
git diff --name-only | grep -v '.md$'
uv run pytest patterns/06_graph_topological_sort/ -v --tb=short 2>&1 | tail -5

echo "=== README subsections ==="
grep "^### " patterns/06_graph_topological_sort/README.md

for section in "The basics" "Directed vs undirected" "BFS" "DFS" "BFS vs DFS" "Topological sort" "Cycle detection" "Connection to data" "problems in this section"; do
    grep -qi "$section" patterns/06_graph_topological_sort/README.md && echo "✅ $section" || echo "❌ $section"
done
```
