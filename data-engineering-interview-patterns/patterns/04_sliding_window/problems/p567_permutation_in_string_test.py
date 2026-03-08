"""Tests for LeetCode 567: Permutation in String."""

import pytest
from p567_permutation_in_string import check_inclusion, check_inclusion_counter


class TestCheckInclusion:
    """Test the frequency-match sliding window."""

    def test_permutation_exists(self):
        assert check_inclusion("ab", "eidbaooo") is True

    def test_no_permutation(self):
        assert check_inclusion("ab", "eidboaoo") is False

    def test_single_char_match(self):
        assert check_inclusion("a", "a") is True

    def test_single_char_no_match(self):
        assert check_inclusion("a", "b") is False

    def test_exact_match(self):
        assert check_inclusion("abc", "abc") is True

    def test_reversed(self):
        assert check_inclusion("abc", "cba") is True

    def test_s1_longer(self):
        assert check_inclusion("abcdef", "abc") is False

    def test_at_end(self):
        assert check_inclusion("abc", "xyzabc") is True

    def test_with_repeats(self):
        assert check_inclusion("aab", "cbdaaboa") is True

    def test_all_same_chars(self):
        assert check_inclusion("aaa", "aaaa") is True

    def test_no_match_with_repeats(self):
        assert check_inclusion("aab", "ccccc") is False

    def test_match_at_start(self):
        assert check_inclusion("abc", "bca1234") is True

    def test_empty_pattern(self):
        """Empty string is a permutation of everything."""
        assert check_inclusion("", "abc") is True


class TestCounterApproachMatch:
    """Counter comparison should match frequency-match approach."""

    @pytest.mark.parametrize(
        "s1,s2",
        [
            ("ab", "eidbaooo"),
            ("ab", "eidboaoo"),
            ("a", "a"),
            ("abc", "cba"),
            ("aab", "cbdaaboa"),
            ("aaa", "aaaa"),
            ("abcdef", "abc"),
        ],
    )
    def test_matches_optimal(self, s1, s2):
        assert check_inclusion_counter(s1, s2) == check_inclusion(s1, s2)
