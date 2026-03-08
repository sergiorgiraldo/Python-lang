"""
LeetCode 133: Clone Graph

Pattern: Graph - BFS/DFS with reconstruction
Difficulty: Medium
Time Complexity: O(V + E)
Space Complexity: O(V)
"""

from __future__ import annotations

from collections import deque


class Node:
    """Graph node with a value and list of neighbors."""

    def __init__(self, val: int = 0, neighbors: list[Node] | None = None) -> None:
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []

    def __repr__(self) -> str:
        return f"Node({self.val})"


def clone_graph_bfs(node: Node | None) -> Node | None:
    """
    Deep clone a graph using BFS.

    Uses a hash map (old node → new node) to track which nodes
    have been cloned. BFS ensures every node and edge is copied.

    Args:
        node: Any node in the connected graph (or None).

    Returns:
        The corresponding node in the cloned graph.

    Example:
        >>> # Graph: 1--2, 1--4, 2--3, 3--4
        >>> # clone_graph_bfs(node1) returns a deep copy
    """
    if not node:
        return None

    cloned: dict[Node, Node] = {node: Node(node.val)}
    queue = deque([node])

    while queue:
        current = queue.popleft()
        for neighbor in current.neighbors:
            if neighbor not in cloned:
                cloned[neighbor] = Node(neighbor.val)
                queue.append(neighbor)
            cloned[current].neighbors.append(cloned[neighbor])

    return cloned[node]


def clone_graph_dfs(node: Node | None) -> Node | None:
    """
    Deep clone a graph using DFS (recursive).

    Time: O(V + E)  Space: O(V)
    """
    if not node:
        return None

    cloned: dict[Node, Node] = {}

    def dfs(original: Node) -> Node:
        if original in cloned:
            return cloned[original]

        copy = Node(original.val)
        cloned[original] = copy

        for neighbor in original.neighbors:
            copy.neighbors.append(dfs(neighbor))

        return copy

    return dfs(node)


def build_graph(adj_list: list[list[int]]) -> Node | None:
    """Build a graph from an adjacency list (1-indexed)."""
    if not adj_list:
        return None

    nodes = {i + 1: Node(i + 1) for i in range(len(adj_list))}
    for i, neighbors in enumerate(adj_list):
        for n in neighbors:
            nodes[i + 1].neighbors.append(nodes[n])
    return nodes[1]


def graph_to_adj_list(node: Node | None) -> list[list[int]]:
    """Convert a graph back to adjacency list (1-indexed)."""
    if not node:
        return []

    visited: dict[int, list[int]] = {}
    queue = deque([node])
    seen = {node}

    while queue:
        current = queue.popleft()
        visited[current.val] = [n.val for n in current.neighbors]
        for neighbor in current.neighbors:
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)

    return [visited.get(i, []) for i in range(1, len(visited) + 1)]


if __name__ == "__main__":
    adj_list = [[2, 4], [1, 3], [2, 4], [1, 3]]
    original = build_graph(adj_list)
    cloned = clone_graph_bfs(original)
    print(f"Original: {graph_to_adj_list(original)}")
    print(f"Cloned:   {graph_to_adj_list(cloned)}")
    print(f"Same object? {original is cloned}")
