/*
Graph Traversal in SQL with Recursive CTEs

Demonstrates:
1. Finding connected components
2. Shortest path (BFS) in an unweighted graph
3. Cycle detection with a path array
*/

CREATE TABLE edges (src INTEGER, dst INTEGER);

-- Simple graph: two connected components
-- Component 1: 1-2-3-4
-- Component 2: 5-6
INSERT INTO edges VALUES (1,2), (2,3), (3,4), (5,6);
-- Make bidirectional
INSERT INTO edges SELECT dst, src FROM edges;

-- ============================================================
-- 1. BFS shortest path from node 1 to all reachable nodes
-- ============================================================
WITH RECURSIVE bfs AS (
    -- Base case: start from node 1
    SELECT 1 AS node, 0 AS distance, [1] AS path

    UNION ALL

    -- Recursive case: visit neighbors not yet in path
    SELECT e.dst AS node,
           b.distance + 1,
           list_append(b.path, e.dst)
    FROM edges e
    JOIN bfs b ON e.src = b.node
    WHERE NOT list_contains(b.path, e.dst)
)
-- Keep shortest path to each node (first arrival = shortest in BFS)
SELECT node, MIN(distance) AS shortest_distance
FROM bfs
GROUP BY node
ORDER BY node;

-- ============================================================
-- 2. Full path reconstruction from node 1
-- ============================================================
-- WITH RECURSIVE bfs AS ( ... same as above ... )
-- SELECT node, distance, path
-- FROM bfs
-- WHERE distance = (SELECT MIN(distance) FROM bfs b2 WHERE b2.node = bfs.node)
-- ORDER BY node;

-- ============================================================
-- 3. Connected components (simplified)
-- For each node, find the minimum reachable node as component ID
-- ============================================================
WITH RECURSIVE reachable AS (
    -- Base case: each node can reach itself
    SELECT src AS node, src AS reachable_node
    FROM (SELECT DISTINCT src FROM edges) nodes

    UNION

    -- Recursive case: if node can reach X, and X connects to Y, node can reach Y
    -- Using UNION (not UNION ALL) for automatic deduplication
    SELECT r.node, e.dst AS reachable_node
    FROM reachable r
    JOIN edges e ON r.reachable_node = e.src
)
SELECT node, MIN(reachable_node) AS component_id
FROM reachable
GROUP BY node
ORDER BY component_id, node;
