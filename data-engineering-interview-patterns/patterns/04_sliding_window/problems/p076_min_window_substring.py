"""
LeetCode 76: Minimum Window Substring

Pattern: Sliding Window - Variable Size + Frequency Matching
Difficulty: Hard
Time Complexity: O(n + m) where n = len(s), m = len(t)
Space Complexity: O(m) for frequency map
"""

from collections import Counter


def min_window(s: str, t: str) -> str:
    """
    Find the smallest substring of s that contains all characters of t.

    Variable-size window. Expand right until all characters of t are
    covered. Then shrink from the left to minimize the window, recording
    the shortest valid window found.

    Args:
        s: Text string to search in.
        t: Target characters that must all be present.

    Returns:
        The minimum window substring, or "" if no valid window exists.

    Example:
        >>> min_window("ADOBECODEBANC", "ABC")
        'BANC'
    """
    if not t or not s:
        return ""

    need = Counter(t)
    chars_needed = len(need)  # Distinct characters still to satisfy
    left = 0
    min_start = 0
    min_len = float("inf")

    for right in range(len(s)):
        # Expand: add s[right] to window
        char_in = s[right]
        if char_in in need:
            need[char_in] -= 1
            if need[char_in] == 0:
                chars_needed -= 1

        # Contract: shrink from left while window is still valid
        while chars_needed == 0:
            # Record this valid window if it's the shortest
            window_size = right - left + 1
            if window_size < min_len:
                min_len = window_size
                min_start = left

            # Remove s[left] from window
            char_out = s[left]
            if char_out in need:
                if need[char_out] == 0:
                    chars_needed += 1
                need[char_out] += 1
            left += 1

    if min_len == float("inf"):
        return ""
    return s[min_start : min_start + min_len]


def min_window_brute(s: str, t: str) -> str:
    """
    Brute force: check every substring. O(n^2 * m).

    For each possible window, check if it contains all characters of t.
    """
    if not t or not s:
        return ""

    target = Counter(t)
    best = ""

    for i in range(len(s)):
        for j in range(i + len(t), len(s) + 1):
            window = s[i:j]
            window_counts = Counter(window)
            if all(window_counts.get(c, 0) >= target[c] for c in target):
                if not best or len(window) < len(best):
                    best = window
                break  # First valid j for this i is shortest from i

    return best


if __name__ == "__main__":
    test_cases = [
        ("ADOBECODEBANC", "ABC", "BANC"),
        ("a", "a", "a"),
        ("a", "aa", ""),
        ("aa", "aa", "aa"),
    ]

    for s, t, expected in test_cases:
        result = min_window(s, t)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status}: min_window('{s}', '{t}') = '{result}'")
