"""
LeetCode 787: Cheapest Flights Within K Stops

Combined Patterns: Graph + Modified BFS (Bellman-Ford variant)
Difficulty: Medium
Time Complexity: O(K * E) where K is max stops, E is number of flights
Space Complexity: O(V) for the distance array
"""

import heapq
from collections import defaultdict


def find_cheapest_price(
    n: int,
    flights: list[list[int]],
    src: int,
    dst: int,
    k: int,
) -> int:
    """
    Find cheapest price from src to dst with at most k stops.

    Standard Dijkstra fails here because it optimizes for shortest
    distance globally, but a shorter-distance path might use too many
    stops. We need to track both cost AND stops simultaneously.

    Bellman-Ford variant: relax all edges K+1 times. After i rounds,
    dist[v] is the cheapest price using at most i edges (i-1 stops).
    """
    prices = [float("inf")] * n
    prices[src] = 0

    for _ in range(k + 1):
        # Copy to avoid using updates from this round
        temp = prices.copy()
        for u, v, w in flights:
            if prices[u] != float("inf") and prices[u] + w < temp[v]:
                temp[v] = prices[u] + w
        prices = temp

    return prices[dst] if prices[dst] != float("inf") else -1


def find_cheapest_price_dijkstra(
    n: int,
    flights: list[list[int]],
    src: int,
    dst: int,
    k: int,
) -> int:
    """
    Modified Dijkstra that tracks stops.

    Standard Dijkstra skips revisiting nodes. Here we may need to
    revisit a node via a more expensive but shorter (fewer stops)
    path. Track the minimum stops to reach each node; only skip
    if we've visited with fewer or equal stops.
    """
    graph: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for u, v, w in flights:
        graph[u].append((v, w))

    # (cost, node, stops_used)
    heap: list[tuple[int, int, int]] = [(0, src, 0)]
    # min stops to reach each node (for pruning)
    best_stops: dict[int, int] = {}

    while heap:
        cost, node, stops = heapq.heappop(heap)

        if node == dst:
            return cost

        if stops > k:
            continue

        # Skip if we've reached this node with fewer stops
        if node in best_stops and best_stops[node] <= stops:
            continue
        best_stops[node] = stops

        for neighbor, price in graph[node]:
            heapq.heappush(heap, (cost + price, neighbor, stops + 1))

    return -1
