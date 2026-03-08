"""
LeetCode 207: Course Schedule

Pattern: Graph - Cycle detection in directed graph
Difficulty: Medium
Time Complexity: O(V + E)
Space Complexity: O(V + E)
"""

from collections import defaultdict, deque


def can_finish_kahn(num_courses: int, prerequisites: list[list[int]]) -> bool:
    """
    Determine if all courses can be finished (no cycles) using Kahn's algorithm.

    If topological sort processes all nodes, the graph is a DAG (no cycles).
    If some nodes remain unprocessed, there's a cycle.

    Args:
        num_courses: Total number of courses (nodes 0 to n-1).
        prerequisites: List of [course, prereq] pairs (edges prereq → course).

    Returns:
        True if all courses can be completed (no circular dependencies).

    Example:
        >>> can_finish_kahn(2, [[1, 0]])
        True
        >>> can_finish_kahn(2, [[1, 0], [0, 1]])
        False
    """
    graph: dict[int, list[int]] = defaultdict(list)
    in_degree = [0] * num_courses

    for course, prereq in prerequisites:
        graph[prereq].append(course)
        in_degree[course] += 1

    queue = deque(i for i in range(num_courses) if in_degree[i] == 0)
    processed = 0

    while queue:
        node = queue.popleft()
        processed += 1
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return processed == num_courses


def can_finish_dfs(num_courses: int, prerequisites: list[list[int]]) -> bool:
    """
    Cycle detection using 3-state DFS.

    States: 0 = unvisited, 1 = in current DFS path, 2 = fully processed.
    If we visit a node in state 1, we've found a back edge (cycle).

    Time: O(V + E)  Space: O(V + E)
    """
    graph: dict[int, list[int]] = defaultdict(list)
    for course, prereq in prerequisites:
        graph[prereq].append(course)

    state = [0] * num_courses  # 0=unvisited, 1=in-path, 2=done

    def has_cycle(node: int) -> bool:
        if state[node] == 1:
            return True  # back edge = cycle
        if state[node] == 2:
            return False  # already fully processed
        state[node] = 1
        for neighbor in graph[node]:
            if has_cycle(neighbor):
                return True
        state[node] = 2
        return False

    return not any(has_cycle(i) for i in range(num_courses) if state[i] == 0)


if __name__ == "__main__":
    print(f"No cycle: {can_finish_kahn(4, [[1, 0], [2, 0], [3, 1], [3, 2]])}")
    print(f"Cycle: {can_finish_kahn(2, [[1, 0], [0, 1]])}")
