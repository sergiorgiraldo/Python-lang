"""Tests for LeetCode 787: Cheapest Flights Within K Stops."""

import pytest

from p787_cheapest_flights import find_cheapest_price, find_cheapest_price_dijkstra


@pytest.mark.parametrize("func", [find_cheapest_price, find_cheapest_price_dijkstra])
class TestCheapestFlights:

    def test_example_1(self, func) -> None:
        flights = [[0, 1, 100], [1, 2, 100], [0, 2, 500]]
        assert func(3, flights, 0, 2, 1) == 200

    def test_example_2(self, func) -> None:
        flights = [[0, 1, 100], [1, 2, 100], [0, 2, 500]]
        assert func(3, flights, 0, 2, 0) == 500

    def test_no_route(self, func) -> None:
        flights = [[0, 1, 100]]
        assert func(3, flights, 0, 2, 1) == -1

    def test_direct_flight(self, func) -> None:
        flights = [[0, 1, 50]]
        assert func(2, flights, 0, 1, 0) == 50

    def test_k_too_small(self, func) -> None:
        flights = [[0, 1, 100], [1, 2, 100], [2, 3, 100]]
        assert func(4, flights, 0, 3, 1) == -1  # need 2 stops, only 1 allowed

    def test_k_exactly_right(self, func) -> None:
        flights = [[0, 1, 100], [1, 2, 100], [2, 3, 100]]
        assert func(4, flights, 0, 3, 2) == 300

    def test_cheaper_with_more_stops(self, func) -> None:
        # Direct: 0->2 costs 500. Via 1: 0->1->2 costs 200 (1 stop).
        flights = [[0, 1, 100], [1, 2, 100], [0, 2, 500]]
        assert func(3, flights, 0, 2, 1) == 200

    def test_single_node(self, func) -> None:
        assert func(1, [], 0, 0, 0) == 0
