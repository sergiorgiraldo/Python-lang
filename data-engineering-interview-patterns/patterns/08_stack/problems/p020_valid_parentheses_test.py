"""Tests for LeetCode 20: Valid Parentheses."""

import pytest

from p020_valid_parentheses import is_valid


class TestValidParentheses:
    """Core bracket matching."""

    def test_simple_parens(self) -> None:
        assert is_valid("()") is True

    def test_multiple_types(self) -> None:
        assert is_valid("()[]{}") is True

    def test_nested(self) -> None:
        assert is_valid("({[]})") is True

    def test_mismatch(self) -> None:
        assert is_valid("(]") is False

    def test_wrong_order(self) -> None:
        assert is_valid("([)]") is False

    def test_unclosed(self) -> None:
        assert is_valid("((") is False

    def test_extra_closer(self) -> None:
        assert is_valid("))") is False

    def test_empty_string(self) -> None:
        assert is_valid("") is True

    def test_single_opener(self) -> None:
        assert is_valid("(") is False

    def test_single_closer(self) -> None:
        assert is_valid(")") is False

    def test_deeply_nested(self) -> None:
        assert is_valid("(((())))") is True

    def test_alternating(self) -> None:
        assert is_valid("(){}[](){}[]") is True
