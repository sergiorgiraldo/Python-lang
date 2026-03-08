"""Tests for LeetCode 210: Course Schedule II."""

import pytest
from p210_course_schedule_ii import find_order_dfs, find_order_kahn


def is_valid_order(order, num_courses, prerequisites):
    """Verify that the order respects all prerequisites."""
    if len(order) != num_courses:
        return False
    if set(order) != set(range(num_courses)):
        return False
    position = {course: i for i, course in enumerate(order)}
    for course, prereq in prerequisites:
        if position[prereq] >= position[course]:
            return False  # prereq must come before course
    return True


class TestFindOrder:
    @pytest.mark.parametrize("fn", [find_order_kahn, find_order_dfs])
    def test_example_1(self, fn):
        order = fn(2, [[1, 0]])
        assert is_valid_order(order, 2, [[1, 0]])

    @pytest.mark.parametrize("fn", [find_order_kahn, find_order_dfs])
    def test_example_2(self, fn):
        order = fn(4, [[1, 0], [2, 0], [3, 1], [3, 2]])
        assert is_valid_order(order, 4, [[1, 0], [2, 0], [3, 1], [3, 2]])

    @pytest.mark.parametrize("fn", [find_order_kahn, find_order_dfs])
    def test_cycle(self, fn):
        assert fn(2, [[1, 0], [0, 1]]) == []

    @pytest.mark.parametrize("fn", [find_order_kahn, find_order_dfs])
    def test_no_prereqs(self, fn):
        order = fn(3, [])
        assert is_valid_order(order, 3, [])

    @pytest.mark.parametrize("fn", [find_order_kahn, find_order_dfs])
    def test_single_course(self, fn):
        assert fn(1, []) == [0]

    @pytest.mark.parametrize("fn", [find_order_kahn, find_order_dfs])
    def test_linear_chain(self, fn):
        edges = [[i + 1, i] for i in range(4)]
        order = fn(5, edges)
        assert is_valid_order(order, 5, edges)

    @pytest.mark.parametrize("fn", [find_order_kahn, find_order_dfs])
    def test_disconnected(self, fn):
        order = fn(4, [[1, 0], [3, 2]])
        assert is_valid_order(order, 4, [[1, 0], [3, 2]])

    @pytest.mark.parametrize("fn", [find_order_kahn, find_order_dfs])
    def test_three_node_cycle(self, fn):
        assert fn(3, [[1, 0], [2, 1], [0, 2]]) == []
