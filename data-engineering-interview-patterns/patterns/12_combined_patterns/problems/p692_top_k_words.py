"""
LeetCode 692: Top K Frequent Words

Combined Patterns: Hash Map (counting) + Heap (selection with custom ordering)
Difficulty: Medium
Time Complexity: O(n log k) for heap approach
Space Complexity: O(n)
"""

import heapq
from collections import Counter


class WordFreq:
    """
    Wrapper for heap comparison: higher frequency first,
    then lexicographically smaller first for ties.
    """

    def __init__(self, word: str, freq: int):
        self.word = word
        self.freq = freq

    def __lt__(self, other: "WordFreq") -> bool:
        # For min-heap: we want to KEEP high freq and low lex order.
        # So the "smallest" (gets popped first) is:
        # lower frequency, or same frequency but lexicographically LARGER
        if self.freq != other.freq:
            return self.freq < other.freq
        return self.word > other.word


def top_k_frequent(words: list[str], k: int) -> list[str]:
    """
    Return the k most frequent words, sorted by frequency (desc)
    then lexicographically (asc) for ties.

    Phase 1 (Hash Map): count word frequencies.
    Phase 2 (Heap): min-heap of size k with custom comparison.
    """
    counts = Counter(words)

    heap: list[WordFreq] = []
    for word, freq in counts.items():
        heapq.heappush(heap, WordFreq(word, freq))
        if len(heap) > k:
            heapq.heappop(heap)

    # Extract in reverse order (heap gives smallest first)
    result: list[str] = []
    while heap:
        result.append(heapq.heappop(heap).word)

    return result[::-1]


def top_k_frequent_sort(words: list[str], k: int) -> list[str]:
    """
    Alternative: sort by (-frequency, word) and take first k.
    Simpler but O(n log n) instead of O(n log k).
    """
    counts = Counter(words)
    sorted_words = sorted(counts.keys(), key=lambda w: (-counts[w], w))
    return sorted_words[:k]
