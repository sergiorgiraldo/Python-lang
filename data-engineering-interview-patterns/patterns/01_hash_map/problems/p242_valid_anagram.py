"""
LeetCode 242: Valid Anagram

Pattern: Hash Map - Frequency Counting
Difficulty: Easy
Time Complexity: O(n)
Space Complexity: O(1) - bounded by alphabet size
"""

from collections import Counter


def is_anagram(s: str, t: str) -> bool:
    """
    Determine if t is an anagram of s.

    Two strings are anagrams if they contain the same characters
    with the same frequencies, just in different order.

    Args:
        s: First string.
        t: Second string.

    Returns:
        True if t is an anagram of s.

    Example:
        >>> is_anagram("anagram", "nagaram")
        True
    """
    if len(s) != len(t):
        return False
    return Counter(s) == Counter(t)


def is_anagram_manual(s: str, t: str) -> bool:
    """
    Manual frequency counting without Counter.

    Shows the underlying pattern explicitly. Build a frequency map
    for one string, then decrement for the other. If all counts
    end at zero, it's an anagram.

    Time: O(n)  Space: O(1) - at most 26 keys for lowercase English
    """
    if len(s) != len(t):
        return False

    counts: dict[str, int] = {}
    for char in s:
        counts[char] = counts.get(char, 0) + 1
    for char in t:
        counts[char] = counts.get(char, 0) - 1

    return all(v == 0 for v in counts.values())


def is_anagram_sort(s: str, t: str) -> bool:
    """
    Sort-based approach. Two anagrams produce identical sorted strings.

    Time: O(n log n)  Space: O(n)

    Simpler to write but slower. Mention in interviews as your
    first thought before optimizing to hash map.
    """
    return sorted(s) == sorted(t)


if __name__ == "__main__":
    test_cases = [
        ("anagram", "nagaram", True),
        ("rat", "car", False),
        ("", "", True),
        ("a", "ab", False),
    ]

    for s, t, expected in test_cases:
        result = is_anagram(s, t)
        status = "PASS" if result == expected else "FAIL"
        print(f'{status}: is_anagram("{s}", "{t}") = {result}')
