"""
LeetCode 200: Number of Islands

Pattern: Graph - BFS/DFS on a grid
Difficulty: Medium
Time Complexity: O(m * n)
Space Complexity: O(m * n) worst case for BFS queue / DFS stack
"""

from collections import deque


def num_islands_bfs(grid: list[list[str]]) -> int:
    """
    Count islands using BFS.

    When we find a '1' (land), start BFS to mark all connected
    land cells as visited. Each BFS discovers one island.

    Args:
        grid: 2D grid of '1' (land) and '0' (water).

    Returns:
        Number of distinct islands.

    Example:
        >>> num_islands_bfs([["1","1","0"],["1","0","0"],["0","0","1"]])
        2
    """
    if not grid or not grid[0]:
        return 0

    rows, cols = len(grid), len(grid[0])
    visited: set[tuple[int, int]] = set()
    count = 0

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1" and (r, c) not in visited:
                count += 1
                # BFS to mark all cells in this island
                queue = deque([(r, c)])
                visited.add((r, c))
                while queue:
                    row, col = queue.popleft()
                    for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        nr, nc = row + dr, col + dc
                        if (
                            0 <= nr < rows
                            and 0 <= nc < cols
                            and grid[nr][nc] == "1"
                            and (nr, nc) not in visited
                        ):
                            visited.add((nr, nc))
                            queue.append((nr, nc))
    return count


def num_islands_dfs(grid: list[list[str]]) -> int:
    """
    Count islands using DFS (iterative).

    Same logic as BFS but uses a stack instead of a queue.
    DFS explores one direction deeply before backtracking.

    Time: O(m * n)  Space: O(m * n)
    """
    if not grid or not grid[0]:
        return 0

    rows, cols = len(grid), len(grid[0])
    visited: set[tuple[int, int]] = set()
    count = 0

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1" and (r, c) not in visited:
                count += 1
                stack = [(r, c)]
                visited.add((r, c))
                while stack:
                    row, col = stack.pop()
                    for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        nr, nc = row + dr, col + dc
                        if (
                            0 <= nr < rows
                            and 0 <= nc < cols
                            and grid[nr][nc] == "1"
                            and (nr, nc) not in visited
                        ):
                            visited.add((nr, nc))
                            stack.append((nr, nc))
    return count


def num_islands_mutate(grid: list[list[str]]) -> int:
    """
    Count islands by mutating the grid (marking visited as '0').

    Avoids the visited set by overwriting land with water after
    visiting. Uses less memory but destroys the input.

    Time: O(m * n)  Space: O(min(m, n)) for BFS queue
    """
    if not grid or not grid[0]:
        return 0

    rows, cols = len(grid), len(grid[0])
    count = 0

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1":
                count += 1
                queue = deque([(r, c)])
                grid[r][c] = "0"
                while queue:
                    row, col = queue.popleft()
                    for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        nr, nc = row + dr, col + dc
                        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == "1":
                            grid[nr][nc] = "0"
                            queue.append((nr, nc))
    return count


if __name__ == "__main__":
    grid = [
        ["1", "1", "1", "1", "0"],
        ["1", "1", "0", "1", "0"],
        ["1", "1", "0", "0", "0"],
        ["0", "0", "0", "0", "0"],
    ]
    print(f"Number of islands: {num_islands_bfs(grid)}")
