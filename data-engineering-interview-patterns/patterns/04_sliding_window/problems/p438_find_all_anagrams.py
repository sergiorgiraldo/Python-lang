"""
LeetCode 438: Find All Anagrams in a String

Pattern: Sliding Window - Fixed Size + Frequency Matching
Difficulty: Medium
Time Complexity: O(n) where n = len(s)
Space Complexity: O(26) = O(1)
"""

from collections import Counter


def find_anagrams(s: str, p: str) -> list[int]:
    """
    Find all start indices where an anagram of p begins in s.

    Same mechanism as LeetCode 567 (Permutation in String) but
    collects all matching positions instead of returning boolean.

    Args:
        s: Text string to search in.
        p: Pattern string (find anagram positions).

    Returns:
        List of starting indices of p's anagrams in s.

    Example:
        >>> find_anagrams("cbaebabacd", "abc")
        [0, 6]
    """
    if len(p) > len(s):
        return []

    need = Counter(p)
    window_size = len(p)
    matches_needed = len(need)
    result = []

    for i in range(len(s)):
        # Add character entering the window
        char_in = s[i]
        if char_in in need:
            need[char_in] -= 1
            if need[char_in] == 0:
                matches_needed -= 1

        # Remove character leaving the window
        if i >= window_size:
            char_out = s[i - window_size]
            if char_out in need:
                if need[char_out] == 0:
                    matches_needed += 1
                need[char_out] += 1

        # Record match
        if matches_needed == 0:
            result.append(i - window_size + 1)

    return result


def find_anagrams_counter(s: str, p: str) -> list[int]:
    """
    Simpler approach: compare Counter objects at each position.
    O(26 * n) but cleaner code.
    """
    if len(p) > len(s):
        return []

    target = Counter(p)
    window = Counter(s[: len(p)])
    result = []

    if window == target:
        result.append(0)

    for i in range(len(p), len(s)):
        window[s[i]] += 1
        old = s[i - len(p)]
        window[old] -= 1
        if window[old] == 0:
            del window[old]
        if window == target:
            result.append(i - len(p) + 1)

    return result


if __name__ == "__main__":
    test_cases = [
        ("cbaebabacd", "abc", [0, 6]),
        ("abab", "ab", [0, 1, 2]),
        ("a", "ab", []),
    ]

    for s, p, expected in test_cases:
        result = find_anagrams(s, p)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status}: find_anagrams('{s}', '{p}') = {result}")
