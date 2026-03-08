# Course Schedule II (LeetCode #210)

🔗 [LeetCode 210: Course Schedule II](https://leetcode.com/problems/course-schedule-ii/)

> **Difficulty:** Medium | **Interview Frequency:** Common

## Problem Statement

Return a valid ordering of courses given their prerequisites, or an empty array if impossible (cycle exists). This extends Course Schedule (#207) from "is it possible?" to "in what order?"

**Example:**
```
Input: numCourses = 4, prerequisites = [[1,0],[2,0],[3,1],[3,2]]
Output: [0,1,2,3] or [0,2,1,3]  (multiple valid orderings exist)
```

**Constraints:**
- 1 <= numCourses <= 2000
- 0 <= prerequisites.length <= numCourses * (numCourses - 1)

---

## Thought Process

1. **Same as 207 but return the order** - Kahn's algorithm already produces the topological order as a side effect. Just collect it.
2. **DFS alternative** - Process a node after all its descendants. The reverse post-order is a valid topological sort.
3. **Multiple valid orderings** - If multiple nodes have in-degree 0 simultaneously, any processing order among them is valid. The problem accepts any correct answer.

---

## Worked Example

Same as Course Schedule but return the actual ordering instead of just True/False. The processed order from Kahn's algorithm IS the topological sort.

```
Input: numCourses=4, prerequisites=[[1,0],[2,0],[3,1],[3,2]]

Graph: 0 → 1 → 3
       0 → 2 → 3

  In-degrees: 0:0, 1:1, 2:1, 3:2
  Queue: [0]

  Process 0: 1→0, 2→0. Queue: [1, 2]. Order: [0]
  Process 1: 3→1. Order: [0, 1]
  Process 2: 3→0. Queue: [3]. Order: [0, 1, 2]
  Process 3: Order: [0, 1, 2, 3]

  Return [0, 1, 2, 3]. (Also valid: [0, 2, 1, 3] - multiple valid orderings exist.)
  If cycle detected: return [].
```

---

## Approaches

### Approach 1: Kahn's Algorithm

<details>
<summary>📝 Explanation</summary>

Identical to Course Schedule (207) but instead of returning True/False, return the processing order. The order in which nodes are dequeued from Kahn's algorithm IS the topological sort.

1. Build the graph and compute in-degrees.
2. Initialize queue with all in-degree-0 nodes.
3. Process queue, appending each node to the result list.
4. If result length == numCourses, return result. Otherwise return [] (cycle exists).

**Time:** O(V + E). **Space:** O(V + E).

Multiple valid orderings may exist when several nodes have in-degree 0 simultaneously. Any valid topological order is acceptable.

</details>

<details>
<summary>💻 Code</summary>

```python
from collections import defaultdict, deque

def find_order_kahn(num_courses, prerequisites):
    graph = defaultdict(list)
    in_degree = [0] * num_courses
    for course, prereq in prerequisites:
        graph[prereq].append(course)
        in_degree[course] += 1

    queue = deque(i for i in range(num_courses) if in_degree[i] == 0)
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    return order if len(order) == num_courses else []
```

</details>

---

### Approach 2: DFS Post-Order Reversal

<details>
<summary>📝 Explanation</summary>

DFS visits each node's descendants first, then adds the node to the result list after all descendants are processed. This post-order means a node always appears after everything it depends on in the reversed result.

Reversing the post-order gives a valid topological sort. The 3-state tracking (unvisited, in-progress, completed) serves double duty: it prevents revisiting nodes and detects cycles (if we reach an in-progress node, there's a cycle).

**Time:** O(V + E) - each node and edge visited once.
**Space:** O(V + E) for the graph representation plus O(V) for the state array and recursion stack.

The main gotcha with DFS topological sort is forgetting to reverse the post-order. Kahn's BFS gives the order directly, which makes it less error-prone in interviews.

</details>

<details>
<summary>💻 Code</summary>

```python
from collections import defaultdict

def find_order_dfs(num_courses, prerequisites):
    graph = defaultdict(list)
    for course, prereq in prerequisites:
        graph[prereq].append(course)

    state = [0] * num_courses
    post_order = []
    has_cycle = False

    def dfs(node):
        nonlocal has_cycle
        if has_cycle or state[node] == 2: return
        if state[node] == 1:
            has_cycle = True; return
        state[node] = 1
        for neighbor in graph[node]:
            dfs(neighbor)
        state[node] = 2
        post_order.append(node)

    for i in range(num_courses):
        if state[i] == 0: dfs(i)
    return [] if has_cycle else post_order[::-1]
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| No prereqs | `3, []` | `[0,1,2]` or any permutation | All independent |
| Cycle | `2, [[1,0],[0,1]]` | `[]` | Impossible |
| Single course | `1, []` | `[0]` | Trivial |
| Linear chain | `0→1→2→3` | `[0,1,2,3]` | Only one valid order |

---

## Common Pitfalls

1. **Returning wrong value on cycle** - Return an empty list, not None or False.
2. **DFS post-order not reversed** - DFS gives reverse topological order. Forgetting to reverse is the most common DFS bug.
3. **Not handling disconnected components** - Must start DFS from every unvisited node, not just node 0.

---

## Interview Tips

**What to say:**
> "I'll use Kahn's algorithm which gives me the topological order directly. Start with nodes that have no dependencies, process them, and the order they come off the queue is a valid execution order."

**The parallelism insight:**
> "Nodes that enter the queue in the same round have no dependencies between them - they can execute in parallel. This is how Airflow determines which tasks can run concurrently."

**What the interviewer evaluates:** Kahn's algorithm (iterative BFS with in-degree tracking) vs DFS with post-order reversal are both valid. Kahn's is more intuitive for explaining execution layers and parallelism. At principal level, discussing "how many tasks can run in parallel at each step?" demonstrates pipeline scheduling understanding. Mention that this is literally what Airflow and dbt do.

---

## DE Application

This is the core algorithm behind:
- **Airflow task scheduling:** Determine which tasks can run and in what order
- **dbt model execution:** Build models in dependency order, run independent models in parallel
- **Build systems:** Make, Bazel, Gradle all use topological sort for build ordering
- **Data pipeline orchestration:** Any system that manages task dependencies uses this

The "parallel execution" insight is particularly important: tasks at the same topological level (entering the queue in the same round of Kahn's algorithm) can run concurrently. This directly maps to Airflow's `max_active_tasks` and dbt's `--threads` parameter.

## At Scale

Topological sort with Kahn's algorithm (BFS-based) naturally produces execution layers: all tasks with in-degree 0 form the first layer (can run in parallel), then the next layer, and so on. This is exactly how Airflow schedules tasks. For a DAG with 10K tasks, topological sort takes milliseconds. The parallelism insight matters at scale: "how many layers does the DAG have?" determines the minimum end-to-end execution time assuming unlimited workers. The critical path (longest path through the DAG) is the theoretical minimum execution time. Airflow's scheduler, dbt's multi-threading and Spark's DAG scheduler all use topological ordering internally.

---

## Related Problems

- [207. Course Schedule](207_course_schedule.md) - Same graph, just checks feasibility
- [269. Alien Dictionary](269_alien_dictionary.md) - Topo sort with derived edge constraints
