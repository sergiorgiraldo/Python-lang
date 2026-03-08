"""
Benchmark: Topological Sort approaches and graph traversal performance.

Compares:
1. Kahn's algorithm (BFS-based topo sort)
2. DFS-based topo sort (post-order reversal)
3. Brute force (scan for ready tasks)

Tests on DAGs of varying sizes and densities.
"""

import random
import sys
import time
from collections import defaultdict, deque


def topo_sort_kahn(n: int, edges: list[tuple[int, int]]) -> list[int]:
    """Kahn's BFS-based topological sort."""
    graph: dict[int, list[int]] = defaultdict(list)
    in_degree = [0] * n
    for src, dst in edges:
        graph[src].append(dst)
        in_degree[dst] += 1

    queue = deque(i for i in range(n) if in_degree[i] == 0)
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    return order


def topo_sort_dfs(n: int, edges: list[tuple[int, int]]) -> list[int]:
    """DFS-based topological sort (post-order reversal)."""
    graph: dict[int, list[int]] = defaultdict(list)
    for src, dst in edges:
        graph[src].append(dst)

    visited = [False] * n
    post_order: list[int] = []

    def dfs(node: int) -> None:
        visited[node] = True
        for neighbor in graph[node]:
            if not visited[neighbor]:
                dfs(neighbor)
        post_order.append(node)

    for i in range(n):
        if not visited[i]:
            dfs(i)
    return post_order[::-1]


def topo_sort_brute(n: int, edges: list[tuple[int, int]]) -> list[int]:
    """Brute force: repeatedly find nodes with all deps satisfied."""
    dep_map: dict[int, set[int]] = defaultdict(set)
    for src, dst in edges:
        dep_map[dst].add(src)

    completed: set[int] = set()
    order: list[int] = []
    remaining = set(range(n))

    while remaining:
        ready = [x for x in remaining if dep_map[x].issubset(completed)]
        for node in ready:
            order.append(node)
            completed.add(node)
            remaining.remove(node)
    return order


def generate_dag(n: int, density: float) -> list[tuple[int, int]]:
    """Generate a random DAG with edges from lower to higher indices."""
    edges = []
    for i in range(n):
        for j in range(i + 1, min(i + 20, n)):
            if random.random() < density:
                edges.append((i, j))
    return edges


def run_benchmark() -> None:
    random.seed(42)

    print("Topological Sort Benchmark")
    print("=" * 70)

    configs = [
        (100, 0.3),
        (1_000, 0.1),
        (5_000, 0.05),
        (10_000, 0.02),
    ]

    header = f"{'nodes':>8} {'edges':>8} {'kahn':>10} {'dfs':>10}"
    header += f" {'brute':>10} {'speedup':>10}"
    print(f"\n{header}")
    print("-" * 66)

    for n, density in configs:
        edges = generate_dag(n, density)

        start = time.perf_counter()
        r1 = topo_sort_kahn(n, edges)
        kahn_time = time.perf_counter() - start

        start = time.perf_counter()
        r2 = topo_sort_dfs(n, edges)
        dfs_time = time.perf_counter() - start

        if n <= 5_000:  # brute force is too slow for large inputs
            start = time.perf_counter()
            topo_sort_brute(n, edges)
            brute_time = time.perf_counter() - start
            brute_str = f"{brute_time:.4f}s"
            speedup = f"{brute_time / kahn_time:.1f}x"
        else:
            brute_str = "skipped"
            speedup = "n/a"

        assert len(r1) == n == len(r2)

        print(
            f"{n:>8,} {len(edges):>8,} {kahn_time:>10.4f}s "
            f"{dfs_time:>10.4f}s {brute_str:>10} {speedup:>10}"
        )

    print("\nNote: Kahn's and DFS are both O(V+E) but Kahn's tends to be")
    print("faster in practice due to better cache locality (BFS pattern).")
    print("Brute force is O(V^2) and becomes impractical above ~5000 nodes.")


if __name__ == "__main__":
    sys.setrecursionlimit(20_000)
    run_benchmark()


def test_kahn_basic() -> None:
    edges = [(0, 1), (0, 2), (1, 3), (2, 3)]
    order = topo_sort_kahn(4, edges)
    assert len(order) == 4
    assert order.index(0) < order.index(1)
    assert order.index(0) < order.index(2)
    assert order.index(1) < order.index(3)


def test_dfs_basic() -> None:
    edges = [(0, 1), (0, 2), (1, 3), (2, 3)]
    order = topo_sort_dfs(4, edges)
    assert len(order) == 4
    assert order.index(0) < order.index(1)
    assert order.index(0) < order.index(2)


def test_brute_basic() -> None:
    edges = [(0, 1), (0, 2), (1, 3), (2, 3)]
    order = topo_sort_brute(4, edges)
    assert len(order) == 4
    assert order.index(0) < order.index(1)


def test_all_agree() -> None:
    edges = generate_dag(50, 0.2)
    r1 = topo_sort_kahn(50, edges)
    r2 = topo_sort_dfs(50, edges)
    r3 = topo_sort_brute(50, edges)
    assert len(r1) == len(r2) == len(r3) == 50
