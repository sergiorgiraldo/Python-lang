# Graph / Topological Sort Pattern

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

## When to Use It

**Recognition signals in interviews:**
- "Find if a path exists between..."
- "Detect cycles in dependencies..."
- "Find the order to process..."
- "How many connected groups..."
- "Shortest path from A to B..."
- Grid problems where you explore from a cell to its neighbors

**Recognition signals in DE work:**
- dbt model execution order
- Airflow DAG task scheduling
- "What downstream tables are affected if I change this schema?"
- "Are there circular dependencies in this pipeline config?"
- Data lineage visualization

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

## Graph Representations in Python

Graphs can be represented several ways. For interview problems, adjacency lists using dicts are the most common:

```python
from collections import defaultdict

# Adjacency list (directed graph)
graph = defaultdict(list)
for src, dst in edges:
    graph[src].append(dst)

# Adjacency list (undirected graph)
graph = defaultdict(list)
for u, v in edges:
    graph[u].append(v)
    graph[v].append(u)

# Adjacency matrix (grid graph)
# The grid itself IS the graph. Neighbors are up/down/left/right.
grid = [
    [1, 1, 0],
    [1, 0, 0],
    [0, 0, 1],
]
```

## Five Patterns You Need to Know

### 1. BFS (Breadth-First Search)

Explore level by level using a queue. Good for shortest path in unweighted graphs and level-order traversal.

```python
from collections import deque

def bfs(graph, start):
    visited = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
```

### 2. DFS (Depth-First Search)

Explore as deep as possible before backtracking. Good for cycle detection, connected components and path finding.

```python
def dfs(graph, start):
    visited = set()

    def explore(node):
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                explore(neighbor)

    explore(start)
    return visited
```

### 3. Topological Sort (Kahn's Algorithm - BFS-based)

Process nodes with no incoming edges first. Remove their edges. Repeat. If you process all nodes, no cycle exists.

```python
from collections import deque, defaultdict

def topo_sort_kahn(num_nodes, edges):
    graph = defaultdict(list)
    in_degree = [0] * num_nodes
    for src, dst in edges:
        graph[src].append(dst)
        in_degree[dst] += 1

    queue = deque(i for i in range(num_nodes) if in_degree[i] == 0)
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return order if len(order) == num_nodes else []  # empty = cycle
```

### 4. Cycle Detection (3-State DFS)

Track three states per node: unvisited (0), in current path (1), fully processed (2). If you visit a node that's in the current path, there's a cycle.

```python
def has_cycle(num_nodes, edges):
    graph = defaultdict(list)
    for src, dst in edges:
        graph[src].append(dst)

    state = [0] * num_nodes  # 0=unvisited, 1=in-path, 2=done

    def dfs(node):
        if state[node] == 1: return True   # cycle
        if state[node] == 2: return False  # already processed
        state[node] = 1
        for neighbor in graph[node]:
            if dfs(neighbor): return True
        state[node] = 2
        return False

    return any(dfs(i) for i in range(num_nodes) if state[i] == 0)
```

### 5. Dijkstra's Shortest Path (Heap-based)

Find the shortest path from a source to all other nodes in a weighted graph. Uses a min-heap to always process the closest unvisited node.

```python
import heapq

def dijkstra(graph, start, n):
    dist = [float('inf')] * n
    dist[start] = 0
    heap = [(0, start)]

    while heap:
        d, node = heapq.heappop(heap)
        if d > dist[node]:
            continue
        for neighbor, weight in graph[node]:
            new_dist = d + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                heapq.heappush(heap, (new_dist, neighbor))
    return dist
```

## Time/Space Complexity

| Algorithm | Time | Space |
|-----------|------|-------|
| BFS/DFS | O(V + E) | O(V) |
| Topological Sort (Kahn's) | O(V + E) | O(V + E) |
| Cycle Detection (DFS) | O(V + E) | O(V) |
| Dijkstra's | O((V + E) log V) | O(V) |
| Connected Components | O(V + E) | O(V) |

V = vertices (nodes), E = edges.

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

### Scale characteristics

Graph algorithms have memory and time costs that depend on both vertices (V) and edges (E):

| Representation | Memory | Edge lookup | Best for |
|---|---|---|---|
| Adjacency list | O(V + E) | O(degree) | Sparse graphs (most DE scenarios) |
| Adjacency matrix | O(V^2) | O(1) | Dense graphs (rare in DE) |

For a pipeline DAG with 1000 tasks and 3000 dependencies, the adjacency list uses ~32KB. For a social graph with 1B users and 100B connections, it uses ~800GB - requiring distributed graph systems (Pregel, GraphX, Neo4j).

**Distributed graph processing:** Graph algorithms are hard to distribute because they involve iterative message passing between neighbors. The Bulk Synchronous Parallel (BSP) model (used by Pregel, Giraph) splits vertices across machines. Each superstep: vertices process messages, send messages to neighbors, synchronize. The synchronization barrier is the bottleneck - straggler partitions slow everything down. Key skew is severe in graph processing: a vertex with 10M edges (a celebrity in a social graph) creates massive imbalance.

**Pipeline DAGs are small graphs.** Most DE graph problems (dependency resolution, lineage tracking, impact analysis) involve small graphs (hundreds to thousands of nodes). These fit easily in memory on a single machine. Don't over-engineer: a Python dict of adjacency lists is fine for pipeline DAGs. Save distributed graph processing for truly large graphs (social networks, web crawling, entity resolution across billions of records).

### SQL equivalent

Graph traversal maps to recursive CTEs in SQL. `WITH RECURSIVE` iterates through edges, building paths level by level. This is BFS in SQL form. Cycle detection requires tracking visited nodes (using arrays in Postgres, or iteration limits in BigQuery/Snowflake). Topological sort in SQL is possible but awkward - it's usually done in the orchestration layer (Airflow, dbt) rather than in SQL. The SQL section's recursive CTE subsection covers these patterns and explicitly bridges to this pattern section.

## Problems

| # | Problem | Difficulty | Key Concept |
|---|---------|------------|-------------|
| [200](https://leetcode.com/problems/number-of-islands/) | [Number of Islands](problems/200_number_of_islands.md) | Medium | BFS/DFS on a grid |
| [547](https://leetcode.com/problems/number-of-provinces/) | [Number of Provinces](problems/547_number_of_provinces.md) | Medium | Connected components |
| [133](https://leetcode.com/problems/clone-graph/) | [Clone Graph](problems/133_clone_graph.md) | Medium | BFS/DFS with reconstruction |
| [207](https://leetcode.com/problems/course-schedule/) | [Course Schedule](problems/207_course_schedule.md) | Medium | Cycle detection |
| [210](https://leetcode.com/problems/course-schedule-ii/) | [Course Schedule II](problems/210_course_schedule_ii.md) | Medium | Topological sort |
| [269](https://leetcode.com/problems/alien-dictionary/) | [Alien Dictionary](problems/269_alien_dictionary.md) | Hard | Topo sort from constraints |
| [743](https://leetcode.com/problems/network-delay-time/) | [Network Delay Time](problems/743_network_delay_time.md) | Medium | Dijkstra's shortest path |

**Suggested order:** 200, 547 → 133 → 207, 210 → 743 → 269

Start with grid-based BFS/DFS (200) and connected components (547) to build intuition. Then graph traversal with reconstruction (133). Course Schedule pair (207, 210) teaches cycle detection and topo sort. Dijkstra's (743) connects to the heap pattern. Alien Dictionary (269) is the hardest and combines topo sort with constraint extraction.

## DE Scenarios

| Scenario | What It Demonstrates |
|----------|---------------------|
| [Pipeline Execution Order](de_scenarios/pipeline_execution_order.md) | Topological sort for DAG scheduling |
| [Dependency Resolution](de_scenarios/dependency_resolution.md) | dbt-style model ordering |
| [Impact Analysis](de_scenarios/impact_analysis.md) | Downstream effects of schema changes |
| [Cycle Detection](de_scenarios/cycle_detection.md) | Finding circular dependencies |

## Interview Tips

**What to say when you recognize this pattern:**
> "This is a graph problem. I need to figure out the right representation (adjacency list vs grid) and the right traversal (BFS for shortest path, DFS for exhaustive exploration, topo sort for ordering)."

**Common follow-ups:**
- "Can you detect a cycle?" → 3-state DFS: unvisited, in-path, done. If you revisit an in-path node, there's a cycle.
- "What if the graph has weights?" → Dijkstra's for non-negative weights. Bellman-Ford for negative weights.
- "How would you parallelize this?" → Topological sort reveals which tasks can run in parallel: all tasks at the same "level" (same in-degree removal round) are independent.

**Python-specific tips:**
- `defaultdict(list)` for adjacency lists
- `collections.deque` for BFS (O(1) popleft vs O(n) for list.pop(0))
- Use a set for visited nodes (O(1) lookup)
- For grid problems, check bounds before accessing neighbors

**What the interviewer evaluates across graph problems:**

- **200 (Islands):** Grid-as-graph recognition is the first test. BFS vs DFS choice and explaining the tradeoff (BFS is iterative and avoids stack overflow, DFS is simpler to write) shows maturity. The follow-up "what about very large grids?" tests whether you know Union-Find as an alternative. Mentioning entity resolution as the production equivalent shows DE depth.
- **133 (Clone Graph):** Managing the visited/cloned map to handle cycles tests graph traversal fundamentals. BFS vs DFS both work - the interviewer wants to see clean code with correct cycle handling. The follow-up "what if nodes have different types?" or "what about very large graphs?" pivots toward system design.
- **207 (Course Schedule):** Three-color DFS (white/gray/black) for cycle detection tests whether you understand graph theory beyond the template. Explaining what the gray state means (currently being processed, so encountering it again means a cycle) is the differentiator. Connecting to Airflow's DAG validation shows you've implemented this pattern in production.
- **210 (Course Schedule II):** Kahn's algorithm (iterative BFS with in-degree tracking) vs DFS with post-order reversal are both valid. Kahn's is more intuitive for explaining execution layers and parallelism. At principal level, discussing "how many tasks can run in parallel at each step?" demonstrates pipeline scheduling understanding. Mention that this is literally what Airflow and dbt do.
- **547 (Number of Provinces):** BFS/DFS on disconnected graphs (iterating over all nodes, starting new traversals for unvisited ones) tests completeness. The Union-Find alternative tests whether you know specialized data structures. At principal level, discussing entity resolution and the "giant component" problem shows you've dealt with real-world graph challenges.
- **269 (Alien Dictionary):** This problem combines graph construction (extracting ordering from word comparisons) with topological sort. The construction phase is where most bugs occur. Handling edge cases (like a word that's a prefix of another but appears after it, which means invalid input) tests thoroughness. This is one of the harder graph problems and is typically used for senior+ interviews.
- **743 (Network Delay):** Dijkstra's algorithm tests whether you can implement a standard algorithm under pressure. The "why not BFS?" question (answer: edges have different weights) tests understanding. The follow-up "what about negative weights?" (answer: Bellman-Ford) tests breadth. Connecting to pipeline critical path analysis shows you apply shortest-path thinking to DE problems.

## Related Patterns

- **Hash Map** - Adjacency lists are hash maps (dict of lists). Visited sets use hash-based lookup.
- **Heap / Priority Queue** - Dijkstra's algorithm uses a min-heap to select the next closest node. Direct connection to pattern 05.
- **Stack** - DFS can be implemented iteratively with a stack. Kahn's algorithm uses a queue (BFS). Both are variations of the same explore-and-process pattern.

## What's Next

After completing graph problems, move to [Intervals](../07_intervals/) for time-range operations and scheduling conflicts - another common DE interview topic.

