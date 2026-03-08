# Clone Graph (LeetCode #133)

🔗 [LeetCode 133: Clone Graph](https://leetcode.com/problems/clone-graph/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

## Problem Statement

Given a reference to a node in a connected undirected graph, return a deep copy of the graph. Each node has a value and a list of its neighbors.

**Example:**
```
Input: adjList = [[2,4],[1,3],[2,4],[1,3]]
(Node 1 connects to 2,4. Node 2 connects to 1,3. Node 3 connects to 2,4. Node 4 connects to 1,3.)
Output: deep copy of the same graph
```

**Constraints:**
- Number of nodes: [0, 100]
- 1 <= Node.val <= 100
- Node.val is unique for each node
- No self-loops or repeated edges (except the self-loop edge case)

---

## Thought Process

1. **Clarify** - "Deep copy" means new node objects with the same structure. No shared references between original and clone.
2. **Key insight** - We need to visit every node (BFS or DFS) and create a copy. The tricky part is connecting copies to copies, not copies to originals. A hash map (original → clone) solves this.
3. **Pattern** - Traverse the graph. For each node: create a clone if it doesn't exist, then connect the clone's neighbors to clones of the original's neighbors.

---

## Worked Example

Deep-copy a graph: create new node objects with the same connections. The tricky part is handling cycles and shared references. A dict maps original nodes to their clones. When we encounter a node we've already cloned, we reuse the existing clone instead of creating a duplicate.

```
Original graph:
  1 -- 2
  |    |
  4 -- 3

BFS clone:
  Start at node 1. Create clone of 1. Map: {1: clone_1}
  Queue: [1]

  Process 1: neighbors = [2, 4]
    Node 2: not cloned yet → create clone_2. Map: {1:c1, 2:c2}. Queue: [2]
    Connect clone_1 ↔ clone_2.
    Node 4: not cloned yet → create clone_4. Map: {1:c1, 2:c2, 4:c4}. Queue: [2, 4]
    Connect clone_1 ↔ clone_4.

  Process 2: neighbors = [1, 3]
    Node 1: already cloned → reuse clone_1. Connect clone_2 ↔ clone_1.
    Node 3: not cloned → create clone_3. Queue: [4, 3]
    Connect clone_2 ↔ clone_3.

  Process 4: neighbors = [1, 3]
    Both already cloned → connect clone_4 ↔ clone_1 and clone_4 ↔ clone_3.

  Process 3: neighbors = [2, 4]
    Both already cloned → connections already exist.

Result: complete deep copy. No shared references with original.
The dict prevents infinite loops on cycles and ensures each node is cloned exactly once.
```

---

## Approaches

### Approach 1: BFS

<details>
<summary>📝 Explanation</summary>

BFS through the original graph. Maintain a dict mapping original nodes to their clones. When visiting a node:
1. For each neighbor of the original node, check if it's in the dict (already cloned).
2. If not, create a clone and add the mapping.
3. Connect the current clone to the neighbor's clone.

The dict serves two purposes: it tracks visited nodes (preventing infinite loops on cycles) and stores the clone references (so we can wire up connections).

**Time:** O(V + E) - visit every node and edge once.
**Space:** O(V) - the clone map holds one entry per node.

The DFS version is the same logic with a stack or recursion instead of a queue.

</details>

<details>
<summary>💻 Code</summary>

```python
from collections import deque

def clone_graph_bfs(node):
    if not node:
        return None
    cloned = {node: Node(node.val)}
    queue = deque([node])
    while queue:
        current = queue.popleft()
        for neighbor in current.neighbors:
            if neighbor not in cloned:
                cloned[neighbor] = Node(neighbor.val)
                queue.append(neighbor)
            cloned[current].neighbors.append(cloned[neighbor])
    return cloned[node]
```

</details>

---

### Approach 2: DFS (Recursive)

<details>
<summary>📝 Explanation</summary>

Recursively clone each node. For each node, check if it's already in the hash map (already cloned). If so, return the existing clone. If not, create a new clone, add it to the map, then recursively clone all neighbors and attach them.

The hash map prevents infinite loops on cycles: when DFS reaches a node that's already been cloned, it returns the existing clone instead of recursing further. This is the same termination logic as BFS checking "already in the map."

**Time:** O(V + E) - each node is cloned once, each edge is traversed once.
**Space:** O(V) for the hash map plus O(V) worst-case recursion stack depth (a chain graph).

Recursive DFS is the most concise implementation for this problem. The BFS version requires more boilerplate but avoids stack overflow concerns on very large graphs.

</details>

<details>
<summary>💻 Code</summary>

```python
def clone_graph_dfs(node):
    if not node:
        return None
    cloned = {}

    def dfs(original):
        if original in cloned:
            return cloned[original]
        copy = Node(original.val)
        cloned[original] = copy
        for neighbor in original.neighbors:
            copy.neighbors.append(dfs(neighbor))
        return copy

    return dfs(node)
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| None input | `None` | `None` | Empty graph |
| Single node | `Node(1)` | `Node(1)` copy | No neighbors to clone |
| Self-loop | Node pointing to itself | Clone pointing to clone-self | Must not point to original |
| Two nodes | `1--2` | Deep copy | Simplest non-trivial graph |

---

## Common Pitfalls

1. **Connecting clones to originals** - If you forget the hash map, cloned nodes will reference original neighbors. The "deep copy" won't be independent.
2. **Infinite loop on cycles** - Without checking `if neighbor in cloned`, you'll create duplicates endlessly on cyclic graphs.
3. **Creating duplicates** - If you create a new clone every time you encounter a node (instead of checking the hash map), you'll end up with multiple copies of the same node.

---

## Interview Tips

**What to say:**
> "I'll BFS through the graph, maintaining a hash map from original nodes to their clones. For each node, I create its clone (if it doesn't exist) and connect the clone's neighbors to clones of the original's neighbors."

**Common follow-ups:**
- "How do you know the clone is truly independent?" → No clone references any original node. The hash map maps old→new but the final graph contains only new nodes.
- "What about disconnected graphs?" → This problem guarantees connected. For disconnected, you'd need a reference to all nodes and run BFS/DFS from each unvisited one.

**What the interviewer evaluates:** Managing the visited/cloned map to handle cycles tests graph traversal fundamentals. BFS vs DFS both work - the interviewer wants to see clean code with correct cycle handling. The follow-up "what if nodes have different types?" or "what about very large graphs?" pivots toward system design.

---

## DE Application

Graph cloning/serialization shows up in:
- Serializing pipeline DAGs for storage or transfer (Airflow serializes DAGs to the database)
- Deep copying configuration graphs before applying mutations
- Snapshotting dependency graphs for point-in-time lineage analysis
- Testing: creating isolated copies of graph structures for unit tests

## At Scale

Cloning uses O(V + E) memory for both the visited map and the cloned graph. For small graphs (pipeline DAGs, org charts), this is negligible. At 1M nodes with 5M edges, the clone takes ~200MB. Deep cloning a large graph is rarely done in production - instead you'd store the graph in a database and query it. The BFS/DFS traversal pattern here is more important than the cloning: traversing a graph while maintaining a visited map is the template for lineage tracking, impact analysis and dependency resolution.

---

## Related Problems

- [200. Number of Islands](200_number_of_islands.md) - Graph traversal (BFS/DFS) without reconstruction
- [207. Course Schedule](207_course_schedule.md) - Directed graph traversal
- [547. Number of Provinces](547_number_of_provinces.md) - Connected components
