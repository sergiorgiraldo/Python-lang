# Course Schedule (LeetCode #207)

🔗 [LeetCode 207: Course Schedule](https://leetcode.com/problems/course-schedule/)

> **Difficulty:** Medium | **Interview Frequency:** Very Common

## Problem Statement

There are `numCourses` courses labeled 0 to numCourses-1. You're given prerequisites where `prerequisites[i] = [a, b]` means you must take course b before course a. Return true if you can finish all courses (i.e., there are no circular dependencies).

**Example:**
```
Input: numCourses = 2, prerequisites = [[1,0]]
Output: true (take 0 first, then 1)

Input: numCourses = 2, prerequisites = [[1,0],[0,1]]
Output: false (circular: 0 requires 1, 1 requires 0)
```

**Constraints:**
- 1 <= numCourses <= 2000
- 0 <= prerequisites.length <= 5000

---

## Thought Process

1. **Clarify** - This is asking "does the dependency graph have a cycle?" If no cycle, a valid ordering exists. If cycle, impossible.
2. **Two approaches** - Kahn's algorithm (BFS-based topo sort) naturally detects cycles: if the output is shorter than the node count, there's a cycle. DFS with 3-state tracking explicitly finds back edges.
3. **Edge direction** - `[a, b]` means b → a (b must come before a). The edge goes from prerequisite to course.

---

## Worked Example

Can you finish all courses given their prerequisites? This is cycle detection in a directed graph. If there's a cycle (Course A requires B, B requires C, C requires A), it's impossible.

```
Input: numCourses=6, prerequisites=[[1,0],[2,1],[3,2],[4,1],[5,3],[5,4]]
  Meaning: to take course 1, you need course 0 first. Etc.

Graph (edges point from prerequisite to dependent):
  0 → 1 → 2 → 3 → 5
       ↓       ↗
       4 ------

Kahn's algorithm (BFS topological sort):
  In-degrees: 0:0, 1:1, 2:1, 3:1, 4:1, 5:2
  Queue (in-degree 0): [0]

  Process 0: decrement 1's in-degree → 0. Add 1 to queue. Processed: [0]
  Process 1: decrement 2→0, 4→0. Queue: [2, 4]. Processed: [0, 1]
  Process 2: decrement 3→0. Queue: [4, 3]. Processed: [0, 1, 2]
  Process 4: decrement 5→1. Processed: [0, 1, 2, 4]
  Process 3: decrement 5→0. Queue: [5]. Processed: [0, 1, 2, 4, 3]
  Process 5: Processed: [0, 1, 2, 4, 3, 5]

  Processed 6 courses = numCourses → return True (all courses completable).

If there were a cycle, some nodes would never reach in-degree 0.
Processed count < numCourses → return False.
```

---

## Approaches

### Approach 1: Kahn's Algorithm (BFS Topological Sort)

<details>
<summary>💡 Hint</summary>

If you can process all nodes via topological sort, there's no cycle. If some nodes remain unprocessable (stuck in a cycle), the output is too short.

</details>

<details>
<summary>📝 Explanation</summary>

Model courses as a directed graph: an edge from A to B means "A is a prerequisite for B." If there's a cycle, some courses can never be taken (each one requires another in the cycle to be completed first).

Kahn's algorithm detects cycles as a side effect of topological sort:
1. Compute in-degree (number of prerequisites) for each course.
2. Add all courses with in-degree 0 to a queue (no prerequisites).
3. Process the queue: for each course, decrement the in-degree of all courses that depend on it. If any drops to 0, add it to the queue.
4. Count how many courses were processed. If count == numCourses, no cycle exists (all courses are completable). If count < numCourses, there's a cycle.

**Time:** O(V + E) where V = number of courses and E = number of prerequisite pairs.
**Space:** O(V + E) for the graph and in-degree array.

</details>

<details>
<summary>💻 Code</summary>

```python
from collections import defaultdict, deque

def can_finish_kahn(num_courses, prerequisites):
    graph = defaultdict(list)
    in_degree = [0] * num_courses
    for course, prereq in prerequisites:
        graph[prereq].append(course)
        in_degree[course] += 1

    queue = deque(i for i in range(num_courses) if in_degree[i] == 0)
    processed = 0
    while queue:
        node = queue.popleft()
        processed += 1
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    return processed == num_courses
```

</details>

---

### Approach 2: 3-State DFS

<details>
<summary>💡 Hint</summary>

Track each node as unvisited (0), in the current DFS path (1), or fully processed (2). A back edge (revisiting a node in state 1) means cycle.

</details>

<details>
<summary>📝 Explanation</summary>

DFS with three states per node: UNVISITED, IN_PROGRESS, COMPLETED.

Start DFS from each unvisited node. When entering a node, mark it IN_PROGRESS. Visit all its neighbors recursively. When all neighbors are done, mark it COMPLETED.

If we ever reach a node that's IN_PROGRESS, we've found a back edge (a cycle). We followed a path from that node and arrived back at it.

**Time:** O(V + E). **Space:** O(V) for the state array plus recursion stack.

The three states are critical. Two-state (visited/unvisited) doesn't distinguish between "I'm currently exploring this path" and "I finished exploring this node earlier from a different starting point."

</details>

<details>
<summary>💻 Code</summary>

```python
from collections import defaultdict

def can_finish_dfs(num_courses, prerequisites):
    graph = defaultdict(list)
    for course, prereq in prerequisites:
        graph[prereq].append(course)

    state = [0] * num_courses

    def has_cycle(node):
        if state[node] == 1: return True
        if state[node] == 2: return False
        state[node] = 1
        for neighbor in graph[node]:
            if has_cycle(neighbor): return True
        state[node] = 2
        return False

    return not any(has_cycle(i) for i in range(num_courses) if state[i] == 0)
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| No prerequisites | `2, []` | `True` | No edges, no cycles |
| Simple cycle | `2, [[1,0],[0,1]]` | `False` | Direct circular dependency |
| Self-loop | `1, [[0,0]]` | `False` | Course depends on itself |
| Disconnected | `4, [[1,0],[3,2]]` | `True` | Multiple components, no cycle |
| Long chain | `0→1→2→3→4` | `True` | Deep but acyclic |

---

## Common Pitfalls

1. **Edge direction confusion** - `[a, b]` means b is a prerequisite for a, so the edge is b → a. Getting this backwards gives wrong results.
2. **Forgetting disconnected nodes** - DFS must start from every unvisited node, not just node 0. A cycle might exist in a disconnected component.
3. **Using 2-state visited for DFS** - A simple visited set can't distinguish between "I'm in the current path" and "I finished processing this subtree." You need 3 states.

---

## Interview Tips

**What to say:**
> "This is cycle detection in a directed graph. I'll use Kahn's algorithm: start with nodes that have no incoming edges, process them, and see if I can process all nodes. If not, there's a cycle."

**Common follow-ups:**
- "Can you also return where the cycle is?" → DFS approach: when you find a back edge, trace back from the current node to the node in state 1. Kahn's approach: the unprocessed nodes with non-zero in-degree are in the cycle.
- "What if you need the actual ordering?" → That's Course Schedule II (problem 210), which returns the topological order.

**What the interviewer evaluates:** Three-color DFS (white/gray/black) for cycle detection tests whether you understand graph theory beyond the template. Explaining what the gray state means (currently being processed, so encountering it again means a cycle) is the differentiator. Connecting to Airflow's DAG validation shows you've implemented this pattern in production.

---

## DE Application

Cycle detection is critical in:
- **Pipeline validation:** Before executing an Airflow or dbt DAG, verify there are no circular dependencies
- **Schema migration:** Check that migration scripts don't have circular dependencies
- **Incremental processing:** Detect cycles in table-to-table dependencies that would cause infinite update loops
- **Configuration validation:** Ensure configuration inheritance or template chains don't have cycles

Kahn's algorithm is preferred in production because it not only detects cycles but also produces the execution order (topological sort) as a side effect.

## At Scale

Cycle detection with DFS uses O(V + E) time and O(V) memory. For a pipeline DAG with 10K tasks and 30K dependencies, this runs in microseconds. In production, cycle detection is a critical safety check: Airflow runs it before executing any DAG. dbt runs it during model compilation. A cycle in a data pipeline means infinite execution. At scale, the interesting problem isn't cycle detection (the DAG is small) but managing DAG evolution: when someone adds a new dependency, check that it doesn't create a cycle BEFORE committing. This is an incremental graph algorithm problem.

---

## Related Problems

- [210. Course Schedule II](210_course_schedule_ii.md) - Returns the actual ordering (not just "is it possible?")
- [200. Number of Islands](200_number_of_islands.md) - Undirected graph traversal (no cycle concern for connected components)
- [269. Alien Dictionary](269_alien_dictionary.md) - Topo sort from derived constraints
