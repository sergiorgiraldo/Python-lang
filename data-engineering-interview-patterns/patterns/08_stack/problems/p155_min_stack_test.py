"""Tests for LeetCode 155: Min Stack."""

import pytest

from p155_min_stack import MinStackTuple, MinStackTwoStacks


@pytest.mark.parametrize("StackClass", [MinStackTuple, MinStackTwoStacks])
class TestMinStack:
    """Test both implementations."""

    def test_basic_operations(self, StackClass) -> None:
        s = StackClass()
        s.push(-2)
        s.push(0)
        s.push(-3)
        assert s.get_min() == -3
        s.pop()
        assert s.top() == 0
        assert s.get_min() == -2

    def test_single_element(self, StackClass) -> None:
        s = StackClass()
        s.push(42)
        assert s.top() == 42
        assert s.get_min() == 42

    def test_increasing_order(self, StackClass) -> None:
        s = StackClass()
        for val in [1, 2, 3, 4, 5]:
            s.push(val)
        assert s.get_min() == 1
        s.pop()
        assert s.get_min() == 1

    def test_decreasing_order(self, StackClass) -> None:
        s = StackClass()
        for val in [5, 4, 3, 2, 1]:
            s.push(val)
        assert s.get_min() == 1
        s.pop()
        assert s.get_min() == 2
        s.pop()
        assert s.get_min() == 3

    def test_duplicate_minimums(self, StackClass) -> None:
        s = StackClass()
        s.push(0)
        s.push(1)
        s.push(0)
        assert s.get_min() == 0
        s.pop()
        assert s.get_min() == 0

    def test_negative_values(self, StackClass) -> None:
        s = StackClass()
        s.push(-1)
        s.push(-2)
        s.push(-3)
        assert s.get_min() == -3
        s.pop()
        assert s.get_min() == -2

    def test_pop_and_push_again(self, StackClass) -> None:
        s = StackClass()
        s.push(3)
        s.push(1)
        s.pop()
        s.push(2)
        assert s.get_min() == 2  # min was 1 but we popped it
        # Actually min should be min(3, 2) = 2
        s.pop()
        assert s.get_min() == 3
