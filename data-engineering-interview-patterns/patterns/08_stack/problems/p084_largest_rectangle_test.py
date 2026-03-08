"""Tests for LeetCode 84: Largest Rectangle in Histogram."""

import pytest

from p084_largest_rectangle import largest_rectangle_area, largest_rectangle_brute


@pytest.mark.parametrize("func", [largest_rectangle_area, largest_rectangle_brute])
class TestLargestRectangle:
    """Test both implementations."""

    def test_example(self, func) -> None:
        assert func([2, 1, 5, 6, 2, 3]) == 10

    def test_increasing(self, func) -> None:
        assert func([1, 2, 3, 4, 5]) == 9  # 3*3 at indices 2-4

    def test_decreasing(self, func) -> None:
        assert func([5, 4, 3, 2, 1]) == 9

    def test_single_bar(self, func) -> None:
        assert func([5]) == 5

    def test_equal_heights(self, func) -> None:
        assert func([3, 3, 3, 3]) == 12

    def test_two_bars(self, func) -> None:
        assert func([2, 4]) == 4

    def test_valley(self, func) -> None:
        assert func([6, 2, 5, 4, 5, 1, 6]) == 12

    def test_all_ones(self, func) -> None:
        assert func([1, 1, 1, 1, 1]) == 5

    def test_spike(self, func) -> None:
        assert func([1, 100, 1]) == 100

    def test_empty(self, func) -> None:
        assert func([]) == 0
