"""Tests for LeetCode 722: Remove Comments."""

import pytest

from p722_remove_comments import remove_comments


class TestRemoveComments:
    """Core comment removal tests."""

    def test_line_comments(self) -> None:
        source = [
            "int x = 1; // initialize x",
            "int y = 2; // initialize y",
        ]
        assert remove_comments(source) == ["int x = 1; ", "int y = 2; "]

    def test_block_comment_single_line(self) -> None:
        source = ["int x = 1; /* comment */ int y = 2;"]
        assert remove_comments(source) == ["int x = 1;  int y = 2;"]

    def test_block_comment_multiline(self) -> None:
        source = [
            "int x = 1;",
            "/* this is a",
            "   multiline comment */",
            "int y = 2;",
        ]
        assert remove_comments(source) == ["int x = 1;", "int y = 2;"]

    def test_block_removes_lines(self) -> None:
        source = [
            "a",
            "/*",
            "b",
            "*/",
            "c",
        ]
        assert remove_comments(source) == ["a", "c"]

    def test_mixed_comments(self) -> None:
        source = [
            "// full line comment",
            "int x = 1;",
            "/* block */ int y = 2;",
        ]
        assert remove_comments(source) == ["int x = 1;", " int y = 2;"]

    def test_block_comment_joins_lines(self) -> None:
        source = [
            "a /* block",
            "comment */ b",
        ]
        assert remove_comments(source) == ["a  b"]

    def test_no_comments(self) -> None:
        source = ["int x = 1;", "int y = 2;"]
        assert remove_comments(source) == ["int x = 1;", "int y = 2;"]

    def test_empty_input(self) -> None:
        assert remove_comments([]) == []

    def test_leetcode_example(self) -> None:
        source = [
            "/*Test program */",
            "int main()",
            "{ ",
            "  // variable declaration ",
            "int a, b, c;",
            "/* This is a test",
            "   multiline  ",
            "   comment for ",
            "   testing */",
            "a = b + c;",
            "}",
        ]
        expected = ["int main()", "{ ", "  ", "int a, b, c;", "a = b + c;", "}"]
        assert remove_comments(source) == expected
