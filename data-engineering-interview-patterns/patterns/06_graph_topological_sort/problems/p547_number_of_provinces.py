"""
LeetCode 547: Number of Provinces (replaces 323: Number of Connected Components)

Pattern: Graph - Connected components
Difficulty: Medium
Time Complexity: O(n^2) for adjacency matrix, O(V+E) for BFS/DFS
Space Complexity: O(n)
"""

from collections import deque


def find_circle_num_bfs(is_connected: list[list[int]]) -> int:
    """
    Count provinces (connected components) using BFS.

    The input is an adjacency matrix: isConnected[i][j] = 1 means
    city i and city j are directly connected.

    Args:
        is_connected: n x n adjacency matrix.

    Returns:
        Number of connected components (provinces).

    Example:
        >>> find_circle_num_bfs([[1,1,0],[1,1,0],[0,0,1]])
        2
    """
    n = len(is_connected)
    visited: set[int] = set()
    provinces = 0

    for city in range(n):
        if city not in visited:
            provinces += 1
            queue = deque([city])
            visited.add(city)
            while queue:
                current = queue.popleft()
                for neighbor in range(n):
                    if is_connected[current][neighbor] == 1 and neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
    return provinces


def find_circle_num_dfs(is_connected: list[list[int]]) -> int:
    """
    Count provinces using DFS.

    Time: O(n^2) - check all entries in adjacency matrix
    Space: O(n) for visited set and recursion stack
    """
    n = len(is_connected)
    visited: set[int] = set()
    provinces = 0

    def dfs(city: int) -> None:
        visited.add(city)
        for neighbor in range(n):
            if is_connected[city][neighbor] == 1 and neighbor not in visited:
                dfs(neighbor)

    for city in range(n):
        if city not in visited:
            provinces += 1
            dfs(city)
    return provinces


class UnionFind:
    """Union-Find (Disjoint Set Union) with path compression and union by rank."""

    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.rank = [0] * n
        self.count = n  # number of components

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # path compression
        return self.parent[x]

    def union(self, x: int, y: int) -> None:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        self.count -= 1


def find_circle_num_union_find(is_connected: list[list[int]]) -> int:
    """
    Count provinces using Union-Find.

    For each edge in the adjacency matrix, union the two cities.
    The final count of components is the number of provinces.

    Time: O(n^2 * α(n)) ≈ O(n^2)  Space: O(n)
    """
    n = len(is_connected)
    uf = UnionFind(n)

    for i in range(n):
        for j in range(i + 1, n):
            if is_connected[i][j] == 1:
                uf.union(i, j)

    return uf.count


if __name__ == "__main__":
    matrix = [[1, 1, 0], [1, 1, 0], [0, 0, 1]]
    print(f"BFS: {find_circle_num_bfs(matrix)}")
    print(f"DFS: {find_circle_num_dfs(matrix)}")
    print(f"Union-Find: {find_circle_num_union_find(matrix)}")
