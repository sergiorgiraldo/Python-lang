"""Tests for LeetCode 547: Number of Provinces."""

import pytest
from p547_number_of_provinces import (
    find_circle_num_bfs,
    find_circle_num_dfs,
    find_circle_num_union_find,
)

ALL_APPROACHES = [find_circle_num_bfs, find_circle_num_dfs, find_circle_num_union_find]


class TestNumberOfProvinces:
    """Test all approaches on shared cases."""

    @pytest.mark.parametrize("fn", ALL_APPROACHES)
    def test_example_1(self, fn):
        assert fn([[1, 1, 0], [1, 1, 0], [0, 0, 1]]) == 2

    @pytest.mark.parametrize("fn", ALL_APPROACHES)
    def test_example_2(self, fn):
        assert fn([[1, 0, 0], [0, 1, 0], [0, 0, 1]]) == 3

    @pytest.mark.parametrize("fn", ALL_APPROACHES)
    def test_all_connected(self, fn):
        assert fn([[1, 1, 1], [1, 1, 1], [1, 1, 1]]) == 1

    @pytest.mark.parametrize("fn", ALL_APPROACHES)
    def test_single_city(self, fn):
        assert fn([[1]]) == 1

    @pytest.mark.parametrize("fn", ALL_APPROACHES)
    def test_two_separate(self, fn):
        assert fn([[1, 0], [0, 1]]) == 2

    @pytest.mark.parametrize("fn", ALL_APPROACHES)
    def test_two_connected(self, fn):
        assert fn([[1, 1], [1, 1]]) == 1

    @pytest.mark.parametrize("fn", ALL_APPROACHES)
    def test_chain(self, fn):
        """1-2-3 connected in a chain → 1 province."""
        matrix = [
            [1, 1, 0, 0],
            [1, 1, 1, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 1],
        ]
        assert fn(matrix) == 2

    @pytest.mark.parametrize("fn", ALL_APPROACHES)
    def test_transitive(self, fn):
        """1 connected to 2, 2 connected to 3 → 1 and 3 in same province."""
        matrix = [
            [1, 1, 0],
            [1, 1, 1],
            [0, 1, 1],
        ]
        assert fn(matrix) == 1
