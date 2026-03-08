"""Tests for LeetCode 150: Evaluate Reverse Polish Notation."""

import pytest

from p150_eval_rpn import eval_rpn


class TestEvalRPN:
    """Core expression evaluation."""

    def test_simple_addition(self) -> None:
        assert eval_rpn(["2", "1", "+"]) == 3

    def test_complex_expression(self) -> None:
        assert eval_rpn(["2", "1", "+", "3", "*"]) == 9

    def test_division_truncation(self) -> None:
        assert eval_rpn(["10", "3", "/"]) == 3

    def test_negative_division(self) -> None:
        # -1 / 2 should truncate toward zero = 0 (not -1)
        tokens = ["4", "13", "5", "/", "+"]
        assert eval_rpn(tokens) == 6

    def test_longer_expression(self) -> None:
        tokens = ["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"]
        assert eval_rpn(tokens) == 22

    def test_single_number(self) -> None:
        assert eval_rpn(["42"]) == 42

    def test_subtraction_order(self) -> None:
        # "5 3 -" means 5 - 3 = 2, not 3 - 5
        assert eval_rpn(["5", "3", "-"]) == 2

    def test_negative_numbers(self) -> None:
        assert eval_rpn(["-2", "3", "+"]) == 1

    def test_all_operators(self) -> None:
        assert eval_rpn(["6", "2", "+", "3", "*", "2", "/"]) == 12

    def test_negative_result(self) -> None:
        assert eval_rpn(["3", "5", "-"]) == -2
