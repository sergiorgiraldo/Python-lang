# Graph Traversal in SQL

## Overview

Recursive CTEs can implement graph algorithms in SQL. Each recursion level corresponds to one BFS layer: all nodes at distance N are discovered in recursion level N. This makes recursive CTEs a natural fit for BFS-style graph traversal, though with significant limitations for large or dense graphs.

## BFS Shortest Path

```sql
WITH RECURSIVE bfs AS (
    SELECT :start AS node, 0 AS distance, [:start] AS path

    UNION ALL

    SELECT e.dst, b.distance + 1, list_append(b.path, e.dst)
    FROM edges e
    JOIN bfs b ON e.src = b.node
    WHERE NOT list_contains(b.path, e.dst)
)
SELECT node, MIN(distance) AS shortest_distance
FROM bfs
GROUP BY node;
```

Each recursion level discovers nodes one hop further from the start. The path array tracks visited nodes to prevent cycles. MIN(distance) per node gives the shortest path length (BFS guarantees first arrival is shortest in unweighted graphs).

## Cycle Detection

Cycle detection is critical for graphs (unlike trees, which are acyclic by definition). Three strategies:

**Path array (recommended for small graphs):**
```sql
WHERE NOT list_contains(b.path, e.dst)
```
Tracks the full path and rejects nodes already visited on the current path. Prevents infinite loops. Memory cost: O(path_length) per row in the working set.

**Depth limit (simple but lossy):**
```sql
WHERE b.distance < 20
```
Caps recursion depth. Simple but may miss long legitimate paths.

**UNION instead of UNION ALL:**
```sql
UNION  -- deduplicates automatically
```
Prevents the same (node, reachable_node) pair from appearing twice, which stops the recursion when no new pairs are discovered. Works for reachability but not for path reconstruction.

## Connected Components

Finding connected components assigns each node to a group such that all nodes in the group can reach each other. The recursive approach:

1. Start: each node can reach itself
2. Recurse: if node A reaches node B, and B connects to C, then A reaches C
3. Use UNION (not UNION ALL) so recursion terminates when no new reachable pairs are found
4. Component ID: MIN(reachable_node) per node

This is O(V * E) in the worst case (each node potentially explores all edges). For large graphs, union-find algorithms in application code are O(V * alpha(V)), which is effectively O(V).

## Limitations of SQL Graph Traversal

SQL is not designed for graph processing. Recursive CTEs work for small graphs but have significant limitations:

| Limitation | Impact |
|---|---|
| No native visited set | Must track in path array (memory-heavy) |
| Set-based processing | Cannot prioritize nodes (no priority queue for Dijkstra) |
| Per-level overhead | Each recursion level is a separate query execution |
| No early termination | Cannot stop BFS when target is found mid-level |
| Intermediate result size | BFS on dense graphs creates exponentially many paths |

## When to Use SQL for Graphs

| Scenario | Recommendation |
|---|---|
| Small graph (< 10K nodes) with occasional queries | Recursive CTE is fine |
| Large graph with frequent traversals | Graph database (Neo4j) or graph processing framework (GraphFrames, NetworkX) |
| Reachability queries on moderate graphs | Recursive CTE with UNION for deduplication |
| Shortest path in weighted graphs | Application code (Dijkstra) or graph database |
| Known, fixed-depth traversal | Self-joins (simpler, faster) |

## At Scale

For a graph with V vertices and E edges:
- BFS via recursive CTE: O(V + E) per traversal in theory, but SQL overhead per level adds a constant factor of 10-100x compared to application code
- Connected components via recursive CTE: O(V * E) worst case due to set-based processing
- Connected components via union-find in Python: O(V * alpha(V)), effectively linear

For a graph with 1M nodes and 10M edges, a recursive CTE BFS from a single node takes seconds to minutes. Finding all connected components takes minutes to hours. The same operations in NetworkX or GraphFrames take seconds.

## Connection to Algorithmic Patterns

Recursive CTEs directly implement the BFS algorithm pattern:

- **Pattern 06 (Graph/Topological Sort):** BFS, DFS, connected components, topological sort all map to recursive CTEs. The SQL version processes level-by-level (BFS), not node-by-node.
- **Pattern 10 (Recursion/Trees):** Tree traversal is a special case of graph traversal where cycles are impossible. Recursive CTEs are more natural for trees than for general graphs.

The key insight: a recursive CTE processes one BFS "layer" per recursion level. All nodes at distance N are discovered simultaneously in level N. This is natural parallelism for wide graphs but adds overhead for deep, narrow graphs.

## Production Examples

- **Data lineage:** "Which tables depend on this source table?" Traverse the dependency graph from a source table to find all downstream consumers.
- **Impact analysis:** "What breaks if I drop this column?" Traverse column-level lineage to find all downstream references.
- **Network topology:** "Is server A reachable from server B?" BFS through the network adjacency graph.
- **Social networks:** "Friends of friends" queries for recommendation engines (typically limited to 2-3 hops).
- **Dependency resolution:** "What packages need to be installed before this one?" Topological sort of the dependency graph.
