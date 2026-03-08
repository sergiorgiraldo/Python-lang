"""
LeetCode 424: Longest Repeating Character Replacement

Pattern: Sliding Window - Variable Size with Constraint
Difficulty: Medium
Time Complexity: O(n)
Space Complexity: O(26) = O(1)
"""

from collections import defaultdict


def character_replacement(s: str, k: int) -> int:
    """
    Find the longest substring where all characters are the same
    after replacing at most k characters.

    Variable window: expand right, track frequency of each character.
    The number of replacements needed = window_size - max_frequency.
    If that exceeds k, shrink from the left.

    Args:
        s: Input string of uppercase English letters.
        k: Maximum number of replacements allowed.

    Returns:
        Length of the longest valid substring.

    Example:
        >>> character_replacement("AABABBA", 1)
        4
    """
    counts: dict[str, int] = defaultdict(int)
    left = 0
    max_freq = 0
    max_len = 0

    for right in range(len(s)):
        counts[s[right]] += 1
        max_freq = max(max_freq, counts[s[right]])

        # If we need more than k replacements, shrink window
        window_size = right - left + 1
        if window_size - max_freq > k:
            counts[s[left]] -= 1
            left += 1

        max_len = max(max_len, right - left + 1)

    return max_len


def character_replacement_brute(s: str, k: int) -> int:
    """
    Brute force: check every substring. O(n^2 * 26).

    For each substring, count character frequencies and check if
    length - max_frequency <= k.
    """
    max_len = 0
    for i in range(len(s)):
        counts: dict[str, int] = defaultdict(int)
        for j in range(i, len(s)):
            counts[s[j]] += 1
            window_size = j - i + 1
            max_freq = max(counts.values())
            if window_size - max_freq <= k:
                max_len = max(max_len, window_size)
            # Don't break - a longer substring might have a
            # higher max_freq that makes it valid again
    return max_len


if __name__ == "__main__":
    test_cases = [
        ("ABAB", 2, 4),
        ("AABABBA", 1, 4),
        ("A", 0, 1),
        ("AAAA", 2, 4),
    ]

    for s, k, expected in test_cases:
        result = character_replacement(s, k)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status}: character_replacement('{s}', {k}) = {result}")
