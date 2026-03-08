"""Tests for LeetCode 621: Task Scheduler."""

import pytest

from p621_task_scheduler import least_interval, least_interval_math


@pytest.mark.parametrize("func", [least_interval, least_interval_math])
class TestTaskScheduler:

    def test_example_1(self, func) -> None:
        assert func(["A", "A", "A", "B", "B", "B"], 2) == 8

    def test_example_2(self, func) -> None:
        assert func(["A", "A", "A", "B", "B", "B"], 0) == 6

    def test_single_task(self, func) -> None:
        assert func(["A"], 2) == 1

    def test_no_cooldown(self, func) -> None:
        assert func(["A", "A", "A", "A"], 0) == 4

    def test_all_same_task(self, func) -> None:
        assert func(["A", "A", "A"], 2) == 7

    def test_many_different_tasks(self, func) -> None:
        # Enough variety to fill cooldown slots
        tasks = ["A", "B", "C", "D", "E", "F", "A", "B", "C", "D", "E", "F"]
        assert func(tasks, 2) == 12  # no idle needed

    def test_cooldown_1(self, func) -> None:
        assert func(["A", "A", "B", "B"], 1) == 4

    def test_single_type_high_cooldown(self, func) -> None:
        assert func(["A", "A"], 3) == 5  # A _ _ _ A
