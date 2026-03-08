"""Tests for LeetCode 853: Car Fleet."""

import pytest

from p853_car_fleet import car_fleet


class TestCarFleet:
    """Core car fleet tests."""

    def test_example(self) -> None:
        assert car_fleet(12, [10, 8, 0, 5, 3], [2, 4, 1, 1, 3]) == 3

    def test_single_car(self) -> None:
        assert car_fleet(10, [3], [3]) == 1

    def test_no_cars(self) -> None:
        assert car_fleet(10, [], []) == 0

    def test_all_same_speed(self) -> None:
        # Same speed, different positions: no one catches up, each is its own fleet
        assert car_fleet(10, [0, 2, 4], [2, 2, 2]) == 3

    def test_all_merge_into_one(self) -> None:
        # Faster car behind catches slower car ahead before target
        assert car_fleet(10, [0, 4], [2, 1]) == 1

    def test_two_cars_no_merge(self) -> None:
        # Slower car behind faster car
        assert car_fleet(10, [0, 5], [1, 3]) == 2

    def test_exact_same_arrival(self) -> None:
        # Same arrival time = same fleet
        assert car_fleet(10, [0, 5], [2, 1]) == 1

    def test_cars_at_target(self) -> None:
        assert car_fleet(10, [10], [1]) == 1

    def test_three_fleets(self) -> None:
        # Each car is slower than the one behind, no one catches up
        assert car_fleet(100, [0, 20, 40], [1, 1, 1]) == 3
