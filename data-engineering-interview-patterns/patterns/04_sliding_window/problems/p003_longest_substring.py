"""
LeetCode 3: Longest Substring Without Repeating Characters

Pattern: Sliding Window - Variable Size
Difficulty: Medium
Time Complexity: O(n)
Space Complexity: O(min(n, alphabet_size))
"""


def length_of_longest_substring(s: str) -> int:
    """
    Find the length of the longest substring without repeating characters.

    Variable-size sliding window. Expand right to include new characters.
    When a duplicate is found, shrink from the left until the duplicate
    is removed.

    Args:
        s: Input string.

    Returns:
        Length of the longest substring with all unique characters.

    Example:
        >>> length_of_longest_substring("abcabcbb")
        3
    """
    char_index: dict[str, int] = {}  # char -> most recent index
    left = 0
    max_len = 0

    for right, char in enumerate(s):
        if char in char_index and char_index[char] >= left:
            # This character is already in the window.
            # Jump left past its previous occurrence.
            left = char_index[char] + 1

        char_index[char] = right
        max_len = max(max_len, right - left + 1)

    return max_len


def length_of_longest_substring_set(s: str) -> int:
    """
    Alternative using a set. Cleaner but slightly slower due to
    incremental left movement (can't jump).

    Time: O(n) - each character is added and removed at most once.
    Space: O(min(n, alphabet_size))
    """
    char_set: set[str] = set()
    left = 0
    max_len = 0

    for right in range(len(s)):
        while s[right] in char_set:
            char_set.remove(s[left])
            left += 1
        char_set.add(s[right])
        max_len = max(max_len, right - left + 1)

    return max_len


def length_of_longest_substring_brute(s: str) -> int:
    """Brute force: check every substring. O(n^3)."""
    max_len = 0
    for i in range(len(s)):
        for j in range(i, len(s)):
            sub = s[i : j + 1]
            if len(sub) == len(set(sub)):
                max_len = max(max_len, len(sub))
            else:
                break  # Extending won't help
    return max_len


if __name__ == "__main__":
    test_cases = [
        ("abcabcbb", 3),
        ("bbbbb", 1),
        ("pwwkew", 3),
        ("", 0),
        (" ", 1),
    ]

    for s, expected in test_cases:
        result = length_of_longest_substring(s)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status}: longest_substring('{s}') = {result}")
