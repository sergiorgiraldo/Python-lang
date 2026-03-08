"""
LeetCode 49: Group Anagrams

Pattern: Hash Map - Grouping by Computed Key
Difficulty: Medium
Time Complexity: O(n * k log k) where k is max string length
Space Complexity: O(n * k)
"""

from collections import defaultdict


def group_anagrams(strs: list[str]) -> list[list[str]]:
    """
    Group strings that are anagrams of each other.

    Uses sorted string as a canonical key. All anagrams produce
    the same sorted string, so they land in the same bucket.

    Args:
        strs: List of strings.

    Returns:
        List of groups where each group contains mutual anagrams.

    Example:
        >>> result = group_anagrams(["eat", "tea", "tan", "ate"])
        >>> sorted([sorted(g) for g in result])
        [['ate', 'eat', 'tea'], ['tan']]
    """
    groups: dict[str, list[str]] = defaultdict(list)
    for s in strs:
        key = "".join(sorted(s))
        groups[key].append(s)
    return list(groups.values())


def group_anagrams_count(strs: list[str]) -> list[list[str]]:
    """
    Use character frequency tuple as key instead of sorting.

    Avoids the O(k log k) sort per string. Instead, count character
    frequencies and use the count tuple as the hash key.

    Time: O(n * k) where k is max string length
    Space: O(n * k)

    Faster for long strings since counting is O(k) vs sorting O(k log k).
    """
    groups: dict[tuple[int, ...], list[str]] = defaultdict(list)
    for s in strs:
        count = [0] * 26
        for char in s:
            count[ord(char) - ord("a")] += 1
        groups[tuple(count)].append(s)
    return list(groups.values())


if __name__ == "__main__":
    strs = ["eat", "tea", "tan", "ate", "nat", "bat"]
    result = group_anagrams(strs)
    for group in result:
        print(sorted(group))
