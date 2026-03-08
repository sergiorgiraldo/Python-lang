"""
LeetCode 767: Reorganize String

Pattern: Heap - Greedy with max-heap
Difficulty: Medium
Time Complexity: O(n log k) where k is unique characters
Space Complexity: O(k)
"""

import heapq
from collections import Counter


def reorganize_string(s: str) -> str:
    """
    Rearrange characters so no two adjacent characters are the same.

    Strategy: always place the most frequent remaining character,
    alternating between the top two. A max-heap gives O(log k) access
    to the most frequent character at each step.

    Args:
        s: Input string of lowercase English letters.

    Returns:
        A valid reorganization, or "" if impossible.

    Example:
        >>> reorganize_string("aab")
        'aba'
    """
    counts = Counter(s)

    # Impossible if any character appears more than (n+1)/2 times
    max_count = max(counts.values())
    if max_count > (len(s) + 1) // 2:
        return ""

    # Max-heap of (-count, char)
    heap = [(-count, char) for char, count in counts.items()]
    heapq.heapify(heap)

    result: list[str] = []
    prev_count, prev_char = 0, ""

    while heap:
        count, char = heapq.heappop(heap)
        result.append(char)

        # Re-add the previous character (it's now eligible again)
        if prev_count < 0:
            heapq.heappush(heap, (prev_count, prev_char))

        # Save current as previous (decrement count)
        prev_count = count + 1  # count is negative, so +1 means decrement
        prev_char = char

    return "".join(result)


def reorganize_string_interleave(s: str) -> str:
    """
    Alternative: fill even indices first, then odd.

    Sort characters by frequency. Place the most frequent at
    indices 0, 2, 4, ... then fill remaining at 1, 3, 5, ...

    Time: O(n log n) for sorting  Space: O(n)
    """
    counts = Counter(s)
    max_count = max(counts.values())
    if max_count > (len(s) + 1) // 2:
        return ""

    # Sort by frequency (most frequent first)
    sorted_chars = sorted(counts.keys(), key=lambda c: -counts[c])

    # Build character list with counts
    chars: list[str] = []
    for c in sorted_chars:
        chars.extend([c] * counts[c])

    # Interleave: fill even positions, then odd
    result = [""] * len(s)
    idx = 0
    for char in chars:
        result[idx] = char
        idx += 2
        if idx >= len(s):
            idx = 1
    return "".join(result)


if __name__ == "__main__":
    test_cases = ["aab", "aaab", "aabb", "abc", "aaabbbccc"]
    for s in test_cases:
        result = reorganize_string(s)
        print(f'reorganize_string("{s}") = "{result}"')
