"""
LeetCode 743: Network Delay Time

Pattern: Graph - Dijkstra's shortest path (uses heap from pattern 05)
Difficulty: Medium
Time Complexity: O((V + E) log V)
Space Complexity: O(V + E)
"""

import heapq
from collections import defaultdict


def network_delay_time(times: list[list[int]], n: int, k: int) -> int:
    """
    Find the time for a signal to reach all nodes from node k.

    Uses Dijkstra's algorithm to find shortest paths from k to all
    other nodes. The answer is the maximum shortest path.

    Args:
        times: List of [source, target, weight] edges.
        n: Number of nodes (1-indexed).
        k: Starting node.

    Returns:
        Time for all nodes to receive the signal, or -1 if impossible.

    Example:
        >>> network_delay_time([[2,1,1],[2,3,1],[3,4,1]], 4, 2)
        2
    """
    graph: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for u, v, w in times:
        graph[u].append((v, w))

    dist: dict[int, int] = {}
    heap: list[tuple[int, int]] = [(0, k)]

    while heap:
        d, node = heapq.heappop(heap)
        if node in dist:
            continue
        dist[node] = d
        for neighbor, weight in graph[node]:
            if neighbor not in dist:
                heapq.heappush(heap, (d + weight, neighbor))

    if len(dist) != n:
        return -1

    return max(dist.values())


def network_delay_time_bellman_ford(times: list[list[int]], n: int, k: int) -> int:
    """
    Bellman-Ford algorithm. Simpler but slower. Works with negative weights.

    Time: O(V * E)  Space: O(V)
    """
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


if __name__ == "__main__":
    times = [[2, 1, 1], [2, 3, 1], [3, 4, 1]]
    print(f"Dijkstra: {network_delay_time(times, 4, 2)}")
    print(f"Bellman-Ford: {network_delay_time_bellman_ford(times, 4, 2)}")
