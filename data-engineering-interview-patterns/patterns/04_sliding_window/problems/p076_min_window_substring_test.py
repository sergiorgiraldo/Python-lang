"""Tests for LeetCode 76: Minimum Window Substring."""

import pytest
from p076_min_window_substring import min_window, min_window_brute


class TestMinWindow:
    """Test the variable window with frequency matching."""

    def test_basic(self):
        assert min_window("ADOBECODEBANC", "ABC") == "BANC"

    def test_single_char_match(self):
        assert min_window("a", "a") == "a"

    def test_insufficient_chars(self):
        assert min_window("a", "aa") == ""

    def test_exact_match(self):
        assert min_window("aa", "aa") == "aa"

    def test_t_longer_than_s(self):
        assert min_window("a", "abc") == ""

    def test_empty_s(self):
        assert min_window("", "a") == ""

    def test_empty_t(self):
        assert min_window("abc", "") == ""

    def test_window_at_start(self):
        assert min_window("abcdef", "abc") == "abc"

    def test_window_at_end(self):
        assert min_window("defabc", "abc") == "abc"

    def test_repeated_chars_in_t(self):
        """t has duplicate characters that must all be present."""
        assert min_window("adobecodebanc", "aab") == "adobecodeba"

    def test_all_same_chars(self):
        assert min_window("aaaa", "aa") == "aa"

    def test_minimum_is_middle(self):
        """Shortest window is in the middle, not at edges."""
        result = min_window("xxxxxABCxxxxx", "ABC")
        assert result == "ABC"

    def test_multiple_valid_windows(self):
        """Multiple valid windows exist; return the shortest."""
        result = min_window("ADOBECODEBANC", "ABC")
        # BANC (4) is shorter than ADOBEC (6) and CODEBA (6)
        assert len(result) == 4


class TestBruteForceMatch:
    """Brute force should agree with sliding window."""

    @pytest.mark.parametrize(
        "s,t",
        [
            ("ADOBECODEBANC", "ABC"),
            ("a", "a"),
            ("a", "aa"),
            ("aa", "aa"),
            ("abcdef", "abc"),
            ("aaaa", "aa"),
        ],
    )
    def test_matches_optimal(self, s, t):
        assert min_window_brute(s, t) == min_window(s, t)
