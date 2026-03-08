"""Tests for LeetCode 3: Longest Substring Without Repeating Characters."""

import pytest
from p003_longest_substring import (
    length_of_longest_substring,
    length_of_longest_substring_brute,
    length_of_longest_substring_set,
)


class TestLongestSubstring:
    """Test the hash-map-based variable window."""

    def test_basic(self):
        assert length_of_longest_substring("abcabcbb") == 3

    def test_all_same(self):
        assert length_of_longest_substring("bbbbb") == 1

    def test_partial_repeat(self):
        assert length_of_longest_substring("pwwkew") == 3

    def test_empty(self):
        assert length_of_longest_substring("") == 0

    def test_single_char(self):
        assert length_of_longest_substring("a") == 1

    def test_space(self):
        assert length_of_longest_substring(" ") == 1

    def test_all_unique(self):
        assert length_of_longest_substring("abcdef") == 6

    def test_two_chars(self):
        assert length_of_longest_substring("au") == 2

    def test_repeat_at_end(self):
        assert length_of_longest_substring("abca") == 3

    def test_long_then_short(self):
        """Longest window is in the first half."""
        assert length_of_longest_substring("abcdeaa") == 5

    def test_numbers_and_letters(self):
        assert length_of_longest_substring("a1b2c3a") == 6

    def test_dvdf(self):
        """Classic tricky case: left must jump, not slide by one."""
        assert length_of_longest_substring("dvdf") == 3


class TestSetApproach:
    """Set-based approach should match hash map approach."""

    @pytest.mark.parametrize(
        "s",
        ["abcabcbb", "bbbbb", "pwwkew", "", "a", "abcdef", "dvdf"],
    )
    def test_matches_hashmap(self, s):
        assert length_of_longest_substring_set(s) == length_of_longest_substring(s)


class TestBruteForceMatch:
    """Brute force should match optimal."""

    @pytest.mark.parametrize(
        "s",
        ["abcabcbb", "bbbbb", "pwwkew", "", "a", "au", "dvdf"],
    )
    def test_matches_optimal(self, s):
        assert length_of_longest_substring_brute(s) == length_of_longest_substring(s)
