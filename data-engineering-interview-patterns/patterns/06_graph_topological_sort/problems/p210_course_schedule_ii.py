"""
LeetCode 210: Course Schedule II

Pattern: Graph - Topological sort
Difficulty: Medium
Time Complexity: O(V + E)
Space Complexity: O(V + E)
"""

from collections import defaultdict, deque


def find_order_kahn(num_courses: int, prerequisites: list[list[int]]) -> list[int]:
    """
    Return a valid course ordering using Kahn's algorithm.

    This is the same as Course Schedule (207) but returns the
    topological order instead of just True/False.

    Args:
        num_courses: Total number of courses.
        prerequisites: List of [course, prereq] pairs.

    Returns:
        A valid ordering, or [] if impossible (cycle exists).

    Example:
        >>> find_order_kahn(4, [[1,0],[2,0],[3,1],[3,2]])
        [0, 1, 2, 3]  # or [0, 2, 1, 3]
    """
    graph: dict[int, list[int]] = defaultdict(list)
    in_degree = [0] * num_courses

    for course, prereq in prerequisites:
        graph[prereq].append(course)
        in_degree[course] += 1

    queue = deque(i for i in range(num_courses) if in_degree[i] == 0)
    order: list[int] = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return order if len(order) == num_courses else []


def find_order_dfs(num_courses: int, prerequisites: list[list[int]]) -> list[int]:
    """
    Topological sort using DFS (post-order reversal).

    Process a node AFTER all its descendants are processed.
    The reverse of this post-order is a valid topological order.

    Time: O(V + E)  Space: O(V + E)
    """
    graph: dict[int, list[int]] = defaultdict(list)
    for course, prereq in prerequisites:
        graph[prereq].append(course)

    state = [0] * num_courses  # 0=unvisited, 1=in-path, 2=done
    post_order: list[int] = []
    has_cycle = False

    def dfs(node: int) -> None:
        nonlocal has_cycle
        if has_cycle or state[node] == 2:
            return
        if state[node] == 1:
            has_cycle = True
            return
        state[node] = 1
        for neighbor in graph[node]:
            dfs(neighbor)
        state[node] = 2
        post_order.append(node)

    for i in range(num_courses):
        if state[i] == 0:
            dfs(i)

    if has_cycle:
        return []
    return post_order[::-1]


if __name__ == "__main__":
    print(f"Order: {find_order_kahn(4, [[1, 0], [2, 0], [3, 1], [3, 2]])}")
    print(f"Cycle: {find_order_kahn(2, [[1, 0], [0, 1]])}")
