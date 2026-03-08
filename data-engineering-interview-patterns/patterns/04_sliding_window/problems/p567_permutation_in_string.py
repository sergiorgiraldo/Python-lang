"""
LeetCode 567: Permutation in String

Pattern: Sliding Window - Fixed Size + Frequency Matching
Difficulty: Medium
Time Complexity: O(n) where n = len(s2)
Space Complexity: O(26) = O(1)
"""

from collections import Counter


def check_inclusion(s1: str, s2: str) -> bool:
    """
    Check if any permutation of s1 exists as a substring of s2.

    Fixed-size window of len(s1) sliding over s2. Track how many
    characters still need to match using a frequency difference map.

    Args:
        s1: Pattern string (check if its permutation exists in s2).
        s2: Text string to search in.

    Returns:
        True if any permutation of s1 is a substring of s2.

    Example:
        >>> check_inclusion("ab", "eidbaooo")
        True
    """
    if len(s1) > len(s2):
        return False

    # Count characters needed
    need = Counter(s1)
    window_size = len(s1)
    # Track how many distinct characters still need to be matched
    matches_needed = len(need)

    for i in range(len(s2)):
        # Add character entering the window
        char_in = s2[i]
        if char_in in need:
            need[char_in] -= 1
            if need[char_in] == 0:
                matches_needed -= 1

        # Remove character leaving the window
        if i >= window_size:
            char_out = s2[i - window_size]
            if char_out in need:
                if need[char_out] == 0:
                    matches_needed += 1
                need[char_out] += 1

        # All characters matched
        if matches_needed == 0:
            return True

    return False


def check_inclusion_counter(s1: str, s2: str) -> bool:
    """
    Simpler approach: compare Counter objects directly. O(26 * n).

    Easier to understand but slightly slower due to Counter comparison
    at each step.
    """
    if len(s1) > len(s2):
        return False

    target = Counter(s1)
    window = Counter(s2[: len(s1)])

    if window == target:
        return True

    for i in range(len(s1), len(s2)):
        # Add new character
        window[s2[i]] += 1
        # Remove old character
        old = s2[i - len(s1)]
        window[old] -= 1
        if window[old] == 0:
            del window[old]

        if window == target:
            return True

    return False


if __name__ == "__main__":
    test_cases = [
        ("ab", "eidbaooo", True),
        ("ab", "eidboaoo", False),
        ("a", "a", True),
        ("abc", "bbbca", True),
    ]

    for s1, s2, expected in test_cases:
        result = check_inclusion(s1, s2)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status}: check_inclusion('{s1}', '{s2}') = {result}")
