"""Tests for LeetCode 394: Decode String."""

import pytest

from p394_decode_string import decode_string, decode_string_recursive


@pytest.mark.parametrize("func", [decode_string, decode_string_recursive])
class TestDecodeString:
    """Test both implementations."""

    def test_simple(self, func) -> None:
        assert func("3[a]") == "aaa"

    def test_nested(self, func) -> None:
        assert func("3[a2[c]]") == "accaccacc"

    def test_adjacent(self, func) -> None:
        assert func("2[abc]3[cd]ef") == "abcabccdcdcdef"

    def test_deeply_nested(self, func) -> None:
        assert func("2[a2[b3[c]]]") == "abcccbcccabcccbccc"

    def test_no_encoding(self, func) -> None:
        assert func("abc") == "abc"

    def test_single_repeat(self, func) -> None:
        assert func("1[abc]") == "abc"

    def test_multi_digit(self, func) -> None:
        assert func("10[a]") == "aaaaaaaaaa"

    def test_empty_brackets(self, func) -> None:
        assert func("3[]") == ""

    def test_letters_between(self, func) -> None:
        assert func("ab3[c]de") == "abcccde"

    def test_complex(self, func) -> None:
        assert func("3[a]2[bc]") == "aaabcbc"
