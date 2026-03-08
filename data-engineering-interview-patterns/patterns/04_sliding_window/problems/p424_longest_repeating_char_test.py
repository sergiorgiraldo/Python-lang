"""Tests for LeetCode 424: Longest Repeating Character Replacement."""

import pytest
from p424_longest_repeating_char import (
    character_replacement,
    character_replacement_brute,
)


class TestCharacterReplacement:
    """Test the variable sliding window approach."""

    def test_basic_alternating(self):
        assert character_replacement("ABAB", 2) == 4

    def test_mixed(self):
        assert character_replacement("AABABBA", 1) == 4

    def test_single_char(self):
        assert character_replacement("A", 0) == 1

    def test_all_same(self):
        assert character_replacement("AAAA", 2) == 4

    def test_no_replacements(self):
        assert character_replacement("ABCDE", 0) == 1

    def test_full_replacement(self):
        """k large enough to replace entire string."""
        assert character_replacement("ABCDE", 4) == 5

    def test_two_chars(self):
        assert character_replacement("AABB", 1) == 3

    def test_empty(self):
        assert character_replacement("", 1) == 0

    def test_k_zero_repeated(self):
        assert character_replacement("AABAA", 0) == 2

    def test_long_run_with_interruption(self):
        """AAABAAAA with k=1: can fix the B for 8 total."""
        assert character_replacement("AAABAAAA", 1) == 8


class TestBruteForceMatch:
    """Brute force should agree with sliding window."""

    @pytest.mark.parametrize(
        "s,k",
        [
            ("ABAB", 2),
            ("AABABBA", 1),
            ("A", 0),
            ("AAAA", 2),
            ("ABCDE", 0),
            ("ABCDE", 4),
            ("AABB", 1),
            ("AABAA", 0),
            ("AAABAAAA", 1),
        ],
    )
    def test_matches_sliding(self, s, k):
        assert character_replacement_brute(s, k) == character_replacement(s, k)
