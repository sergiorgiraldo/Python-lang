"""Tests for LeetCode 739: Daily Temperatures."""

import pytest

from p739_daily_temperatures import daily_temperatures, daily_temperatures_brute


@pytest.mark.parametrize("func", [daily_temperatures, daily_temperatures_brute])
class TestDailyTemperatures:
    """Test both implementations."""

    def test_example(self, func) -> None:
        assert func([73, 74, 75, 71, 69, 72, 76, 73]) == [1, 1, 4, 2, 1, 1, 0, 0]

    def test_decreasing(self, func) -> None:
        assert func([76, 75, 74, 73]) == [0, 0, 0, 0]

    def test_increasing(self, func) -> None:
        assert func([70, 71, 72, 73]) == [1, 1, 1, 0]

    def test_single(self, func) -> None:
        assert func([50]) == [0]

    def test_two_elements_warmer(self, func) -> None:
        assert func([30, 60]) == [1, 0]

    def test_two_elements_same(self, func) -> None:
        assert func([50, 50]) == [0, 0]

    def test_plateau_then_spike(self, func) -> None:
        assert func([70, 70, 70, 80]) == [3, 2, 1, 0]

    def test_all_same(self, func) -> None:
        assert func([65, 65, 65, 65]) == [0, 0, 0, 0]

    def test_valley_pattern(self, func) -> None:
        assert func([80, 70, 60, 70, 80]) == [0, 3, 1, 1, 0]
