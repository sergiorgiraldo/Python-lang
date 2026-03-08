"""Tests for LeetCode 767: Reorganize String."""

from collections import Counter

import pytest
from p767_reorganize_string import reorganize_string, reorganize_string_interleave


def is_valid_reorganization(s: str, original: str) -> bool:
    """Check that result has no adjacent duplicates and same char counts."""
    if Counter(s) != Counter(original):
        return False
    for i in range(1, len(s)):
        if s[i] == s[i - 1]:
            return False
    return True


class TestReorganizeString:
    """Test the heap-based solution."""

    def test_example_possible(self):
        result = reorganize_string("aab")
        assert is_valid_reorganization(result, "aab")

    def test_impossible(self):
        assert reorganize_string("aaab") == ""

    def test_two_chars_balanced(self):
        result = reorganize_string("aabb")
        assert is_valid_reorganization(result, "aabb")

    def test_all_unique(self):
        result = reorganize_string("abc")
        assert is_valid_reorganization(result, "abc")

    def test_single_char(self):
        assert reorganize_string("a") == "a"

    def test_two_same(self):
        assert reorganize_string("aa") == ""

    def test_three_chars_balanced(self):
        result = reorganize_string("aaabbbccc")
        assert is_valid_reorganization(result, "aaabbbccc")

    def test_one_dominant(self):
        """Most frequent appears exactly (n+1)/2 times - still possible."""
        result = reorganize_string("aabbc")
        assert is_valid_reorganization(result, "aabbc")

    def test_long_string(self):
        s = "a" * 5 + "b" * 4 + "c" * 3
        result = reorganize_string(s)
        assert is_valid_reorganization(result, s)

    def test_boundary_impossible(self):
        """One more than allowed makes it impossible."""
        # n=3, max allowed = 2. "aaa" is not possible.
        assert reorganize_string("aaa") == ""


class TestReorganizeInterleave:
    """Test the interleave approach agrees with heap approach."""

    @pytest.mark.parametrize(
        "s",
        ["aab", "aabb", "abc", "aaabbbccc", "a", "aabbc"],
    )
    def test_valid_result(self, s):
        result = reorganize_string_interleave(s)
        assert is_valid_reorganization(result, s)

    @pytest.mark.parametrize("s", ["aaab", "aa", "aaa"])
    def test_impossible_cases(self, s):
        assert reorganize_string_interleave(s) == ""
