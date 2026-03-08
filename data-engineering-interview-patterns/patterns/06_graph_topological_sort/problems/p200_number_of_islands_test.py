"""Tests for LeetCode 200: Number of Islands."""

import copy

import pytest
from p200_number_of_islands import num_islands_bfs, num_islands_dfs, num_islands_mutate


def make_grid(g: list[list[str]]) -> list[list[str]]:
    """Deep copy a grid so tests don't share state."""
    return copy.deepcopy(g)


GRID_1 = [
    ["1", "1", "1", "1", "0"],
    ["1", "1", "0", "1", "0"],
    ["1", "1", "0", "0", "0"],
    ["0", "0", "0", "0", "0"],
]
GRID_2 = [
    ["1", "1", "0", "0", "0"],
    ["1", "1", "0", "0", "0"],
    ["0", "0", "1", "0", "0"],
    ["0", "0", "0", "1", "1"],
]


class TestNumIslandsBFS:
    def test_example_1(self):
        assert num_islands_bfs(make_grid(GRID_1)) == 1

    def test_example_2(self):
        assert num_islands_bfs(make_grid(GRID_2)) == 3

    def test_empty_grid(self):
        assert num_islands_bfs([]) == 0

    def test_all_water(self):
        assert num_islands_bfs([["0", "0"], ["0", "0"]]) == 0

    def test_all_land(self):
        assert num_islands_bfs([["1", "1"], ["1", "1"]]) == 1

    def test_single_cell_land(self):
        assert num_islands_bfs([["1"]]) == 1

    def test_single_cell_water(self):
        assert num_islands_bfs([["0"]]) == 0

    def test_diagonal_not_connected(self):
        """Diagonals are NOT connected - only up/down/left/right."""
        grid = [["1", "0"], ["0", "1"]]
        assert num_islands_bfs(grid) == 2

    def test_l_shaped_island(self):
        grid = [
            ["1", "0", "0"],
            ["1", "0", "0"],
            ["1", "1", "1"],
        ]
        assert num_islands_bfs(grid) == 1

    def test_many_single_islands(self):
        grid = [
            ["1", "0", "1"],
            ["0", "1", "0"],
            ["1", "0", "1"],
        ]
        assert num_islands_bfs(grid) == 5


class TestNumIslandsDFS:
    @pytest.mark.parametrize(
        "grid, expected",
        [
            (GRID_1, 1),
            (GRID_2, 3),
            ([], 0),
            ([["0", "0"], ["0", "0"]], 0),
            ([["1", "1"], ["1", "1"]], 1),
            ([["1", "0"], ["0", "1"]], 2),
        ],
    )
    def test_matches_bfs(self, grid, expected):
        assert num_islands_dfs(make_grid(grid)) == expected


class TestNumIslandsMutate:
    @pytest.mark.parametrize(
        "grid, expected",
        [
            (GRID_1, 1),
            (GRID_2, 3),
            ([], 0),
            ([["0", "0"], ["0", "0"]], 0),
            ([["1", "1"], ["1", "1"]], 1),
            ([["1", "0"], ["0", "1"]], 2),
        ],
    )
    def test_matches_bfs(self, grid, expected):
        assert num_islands_mutate(make_grid(grid)) == expected
