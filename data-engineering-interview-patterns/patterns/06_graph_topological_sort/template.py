"""
Graph / Topological Sort Pattern Templates

Reusable code patterns for graph traversal, cycle detection,
topological sorting and shortest path problems. Graph problems
show up in DE interviews as pipeline DAGs, dependency resolution
and lineage analysis.
"""

import heapq
from collections import defaultdict, deque
from typing import Hashable


def bfs(graph: dict[Hashable, list[Hashable]], start: Hashable) -> list[Hashable]:
    """
    Breadth-first search from a starting node.

    Explores level by level. Returns nodes in BFS order.
    Useful for shortest path in unweighted graphs.

    Time: O(V + E)  Space: O(V)
    """
    visited = {start}
    queue = deque([start])
    order: list[Hashable] = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order


def dfs(graph: dict[Hashable, list[Hashable]], start: Hashable) -> list[Hashable]:
    """
    Depth-first search from a starting node (iterative).

    Explores as deep as possible before backtracking.

    Time: O(V + E)  Space: O(V)
    """
    visited = set()
    stack = [start]
    order: list[Hashable] = []

    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                stack.append(neighbor)
    return order


def topological_sort_kahn(num_nodes: int, edges: list[tuple[int, int]]) -> list[int]:
    """
    Topological sort using Kahn's algorithm (BFS-based).

    Returns a valid ordering if the graph is a DAG.
    Returns an empty list if a cycle is detected.

    Time: O(V + E)  Space: O(V + E)
    """
    graph: dict[int, list[int]] = defaultdict(list)
    in_degree = [0] * num_nodes

    for src, dst in edges:
        graph[src].append(dst)
        in_degree[dst] += 1

    queue = deque(i for i in range(num_nodes) if in_degree[i] == 0)
    order: list[int] = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return order if len(order) == num_nodes else []


def has_cycle_directed(num_nodes: int, edges: list[tuple[int, int]]) -> bool:
    """
    Detect if a directed graph has a cycle using 3-state DFS.

    States: 0 = unvisited, 1 = in current path, 2 = fully processed.
    A back edge (visiting a node in state 1) indicates a cycle.

    Time: O(V + E)  Space: O(V)
    """
    graph: dict[int, list[int]] = defaultdict(list)
    for src, dst in edges:
        graph[src].append(dst)

    state = [0] * num_nodes

    def _dfs(node: int) -> bool:
        if state[node] == 1:
            return True
        if state[node] == 2:
            return False
        state[node] = 1
        for neighbor in graph[node]:
            if _dfs(neighbor):
                return True
        state[node] = 2
        return False

    return any(_dfs(i) for i in range(num_nodes) if state[i] == 0)


def connected_components(
    num_nodes: int, edges: list[tuple[int, int]]
) -> list[list[int]]:
    """
    Find all connected components in an undirected graph.

    Uses BFS from each unvisited node to discover all nodes
    in that component.

    Time: O(V + E)  Space: O(V + E)
    """
    graph: dict[int, list[int]] = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)

    visited: set[int] = set()
    components: list[list[int]] = []

    for node in range(num_nodes):
        if node not in visited:
            component: list[int] = []
            queue = deque([node])
            visited.add(node)
            while queue:
                current = queue.popleft()
                component.append(current)
                for neighbor in graph[current]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            components.append(component)
    return components


def dijkstra(
    graph: dict[int, list[tuple[int, int]]], start: int, num_nodes: int
) -> list[float]:
    """
    Dijkstra's shortest path from a source to all nodes.

    Uses a min-heap (pattern 05) to always process the closest node.
    Only works with non-negative edge weights.

    Time: O((V + E) log V)  Space: O(V)
    """
    dist: list[float] = [float("inf")] * num_nodes
    dist[start] = 0
    heap: list[tuple[float, int]] = [(0, start)]

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
