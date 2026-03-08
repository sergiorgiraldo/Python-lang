# Network Delay Time (LeetCode #743)

🔗 [LeetCode 743: Network Delay Time](https://leetcode.com/problems/network-delay-time/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

## Problem Statement

You have a network of n nodes labeled 1 to n. Given `times[i] = [u, v, w]` meaning a signal from u to v takes w time, find how long it takes for all nodes to receive a signal sent from node k. Return -1 if not all nodes can be reached.

**Example:**
```
Input: times = [[2,1,1],[2,3,1],[3,4,1]], n = 4, k = 2
Output: 2  (2→1 takes 1, 2→3 takes 1, 2→3→4 takes 2. Max = 2.)
```

**Constraints:**
- 1 <= k <= n <= 100
- 1 <= times.length <= 6000
- 1 <= u, v <= n
- 0 <= w <= 100

---

## Thought Process

1. **Clarify** - This is single-source shortest path. Find the shortest distance from k to every other node. The answer is the maximum of those distances.
2. **Dijkstra's** - The graph has non-negative weights, so Dijkstra's works. Uses a min-heap (pattern 05) to always process the closest unvisited node.
3. **Bellman-Ford alternative** - Simpler but O(V * E) vs Dijkstra's O((V + E) log V). Worth mentioning but not the primary approach.

---

## Worked Example

Shortest path with weighted edges. Dijkstra's algorithm uses a min-heap: always process the node with the smallest known distance. When we process a node, its distance is finalized (can't be improved).

```
Input: times=[[1,2,1],[1,3,4],[2,3,2],[3,4,1]], n=4, k=1
  (edge from node 1 to 2 costs 1, etc.)

Graph:
  1 --(1)--> 2 --(2)--> 3 --(1)--> 4
  1 --(4)--> 3

Dijkstra from node 1:
  dist = {1:0, 2:inf, 3:inf, 4:inf}
  heap = [(0, node1)]

  Pop (0, 1): process neighbors
    2: dist[2] = min(inf, 0+1) = 1. Push (1, 2).
    3: dist[3] = min(inf, 0+4) = 4. Push (4, 3).

  Pop (1, 2): process neighbors
    3: dist[3] = min(4, 1+2) = 3. Push (3, 3). (shorter path found)

  Pop (3, 3): process neighbors
    4: dist[4] = min(inf, 3+1) = 4. Push (4, 4).

  Pop (4, 3): already processed at distance 3. Skip.
  Pop (4, 4): process. No outgoing edges.

  Final distances: {1:0, 2:1, 3:3, 4:4}
  All nodes reachable. Max distance = 4. Answer: 4.

The key: the path 1→2→3 (cost 3) is shorter than 1→3 (cost 4).
The heap ensures we discover this shorter path first.
```

---

## Approaches

### Approach 1: Dijkstra's Algorithm

<details>
<summary>💡 Hint</summary>

Always process the closest unvisited node. A min-heap gives you that in O(log V).

</details>

<details>
<summary>📝 Explanation</summary>

Dijkstra finds the shortest weighted path from a source to all other nodes. It's BFS with a priority queue (min-heap) instead of a regular queue. Always process the node with the smallest known distance next. Once a node is processed, its distance is final.

1. Initialize distances: source = 0, all others = infinity.
2. Push (0, source) onto the min-heap.
3. Pop the minimum. If we've already finalized this node, skip it. Otherwise, for each neighbor, check if `current_dist + edge_weight < known_dist[neighbor]`. If so, update and push the new distance.
4. After the heap is empty, all reachable nodes have final distances. The answer (time for signal to reach all nodes) is the maximum distance. If any node is still infinity, return -1 (unreachable).

**Time:** O(E log V) - each edge causes at most one heap operation.
**Space:** O(V + E) for the graph and heap.

Important: Dijkstra only works with non-negative edge weights. Negative weights require Bellman-Ford (rarely asked in interviews).

</details>

<details>
<summary>💻 Code</summary>

```python
import heapq
from collections import defaultdict

def network_delay_time(times, n, k):
    graph = defaultdict(list)
    for u, v, w in times:
        graph[u].append((v, w))

    dist = {}
    heap = [(0, k)]
    while heap:
        d, node = heapq.heappop(heap)
        if node in dist:
            continue
        dist[node] = d
        for neighbor, weight in graph[node]:
            if neighbor not in dist:
                heapq.heappush(heap, (d + weight, neighbor))

    return max(dist.values()) if len(dist) == n else -1
```

</details>

---

### Approach 2: Bellman-Ford

<details>
<summary>📝 Explanation</summary>

Relax all edges V-1 times. In each pass, check every edge and update the destination's distance if a shorter path is found through the source. After V-1 passes, all shortest paths are finalized (a shortest path uses at most V-1 edges).

Simpler to implement than Dijkstra's (no heap needed) but slower. The main advantage is that Bellman-Ford handles negative edge weights correctly, which Dijkstra's cannot. Not needed for this problem since all weights are non-negative, but worth mentioning in interviews.

**Time:** O(V × E) - V-1 passes over all E edges. The early termination optimization (stop if no updates in a pass) helps in practice.
**Space:** O(V) - only the distance array. No heap or adjacency list needed since we iterate over the raw edge list.

</details>

<details>
<summary>💻 Code</summary>

```python
def network_delay_time_bellman_ford(times, n, k):
    dist = [float("inf")] * (n + 1)
    dist[k] = 0
    for _ in range(n - 1):
        updated = False
        for u, v, w in times:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                updated = True
        if not updated:
            break
    max_dist = max(dist[1:])
    return max_dist if max_dist < float("inf") else -1
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Unreachable node | `[[1,2,1]], n=2, k=2` | `-1` | Node 1 can't be reached from 2 |
| Single node | `[], n=1, k=1` | `0` | Trivially reached |
| Multiple paths | `1→2 (10), 1→3→2 (2)` | `2` | Must find shortest |
| Parallel edges | `1→2 (10), 1→2 (1)` | `1` | Use the cheaper edge |

---

## Common Pitfalls

1. **Forgetting the `if node in dist: continue` check** - Without this, you process the same node multiple times with different distances, potentially corrupting results.
2. **1-indexed nodes** - LeetCode uses 1-indexed nodes. Off-by-one errors are common. Using a dict for dist instead of a list avoids this.
3. **Not returning -1 for unreachable** - If `len(dist) != n`, some nodes weren't reached.

---

## Interview Tips

**What to say:**
> "This is single-source shortest path with non-negative weights, so Dijkstra's is the right choice. I'll use a min-heap to always process the closest unvisited node. The answer is the maximum shortest-path distance across all nodes."

**Common follow-ups:**
- "Why not BFS?" → BFS finds shortest path in unweighted graphs. This graph has weights, so we need Dijkstra's.
- "What if there were negative weights?" → Bellman-Ford handles negative weights. Dijkstra's greedy property breaks with negative edges.
- "How does this connect to the heap pattern?" → Dijkstra's is essentially a BFS where the queue is replaced by a min-heap. The heap ensures we process nodes in order of distance, not discovery order.

**What the interviewer evaluates:** Dijkstra's algorithm tests whether you can implement a standard algorithm under pressure. The "why not BFS?" question (answer: edges have different weights) tests understanding. The follow-up "what about negative weights?" (answer: Bellman-Ford) tests breadth. Connecting to pipeline critical path analysis shows you apply shortest-path thinking to DE problems.

---

## DE Application

Shortest path algorithms apply to:
- **Network latency analysis:** "What's the worst-case propagation time in our distributed system?"
- **Cost optimization:** Finding the cheapest path through a data pipeline (compute costs per transformation step)
- **Dependency analysis:** "What's the longest critical path in our DAG?" (determines minimum pipeline runtime)
- **Data freshness:** "How stale can this derived table get?" (sum of lag through dependency chain)

The critical path through a pipeline DAG is the longest shortest path - the same concept as this problem but maximized instead of taking the overall max.

## At Scale

Dijkstra's algorithm with a binary heap runs O((V + E) log V). For a network with 10K nodes and 100K edges, this takes milliseconds. For graphs with millions of nodes, the heap operations become the bottleneck: Fibonacci heaps improve the theoretical complexity to O(V log V + E) but are rarely used in practice due to high constant factors. At web scale (billions of nodes), single-source shortest path is computed with distributed BFS variants or approximate algorithms. In DE, the more common application is critical path analysis in pipeline DAGs: "what's the end-to-end execution time of my pipeline?" This is the longest (not shortest) path in a DAG, computed with a topological sort and dynamic programming in O(V + E).

---

## Related Problems

- [200. Number of Islands](200_number_of_islands.md) - Unweighted BFS (no heap needed)
- [207. Course Schedule](207_course_schedule.md) - Directed graph, different problem (cycle detection)
