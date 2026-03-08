"""
LeetCode 269: Alien Dictionary (Premium)

Pattern: Graph - Topological sort from derived constraints
Difficulty: Hard
Time Complexity: O(C) where C = total characters across all words
Space Complexity: O(1) since alphabet size is bounded (26 letters)
"""

from collections import defaultdict, deque


def alien_order(words: list[str]) -> str:
    """
    Determine the character ordering in an alien language.

    Given a sorted list of words in the alien language, derive the
    character ordering by comparing adjacent words. The first
    differing character between adjacent words gives one ordering
    constraint (edge in the graph).

    Args:
        words: List of words sorted in alien language order.

    Returns:
        A string of characters in alien language order,
        or "" if the ordering is invalid (cycle or contradiction).

    Example:
        >>> alien_order(["wrt", "wrf", "er", "ett", "rftt"])
        'wertf'
    """
    graph: dict[str, set[str]] = defaultdict(set)
    in_degree: dict[str, int] = {c: 0 for word in words for c in word}

    for i in range(len(words) - 1):
        word1, word2 = words[i], words[i + 1]
        min_len = min(len(word1), len(word2))

        if len(word1) > len(word2) and word1[:min_len] == word2[:min_len]:
            return ""

        for j in range(min_len):
            if word1[j] != word2[j]:
                if word2[j] not in graph[word1[j]]:
                    graph[word1[j]].add(word2[j])
                    in_degree[word2[j]] = in_degree.get(word2[j], 0) + 1
                break

    queue = deque(c for c in in_degree if in_degree[c] == 0)
    result: list[str] = []

    while queue:
        char = queue.popleft()
        result.append(char)
        for neighbor in graph[char]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(result) != len(in_degree):
        return ""

    return "".join(result)


def alien_order_dfs(words: list[str]) -> str:
    """
    DFS-based approach with post-order reversal.

    Time: O(C)  Space: O(1) (bounded by alphabet size)
    """
    graph: dict[str, set[str]] = defaultdict(set)
    all_chars: set[str] = {c for word in words for c in word}

    for i in range(len(words) - 1):
        word1, word2 = words[i], words[i + 1]
        min_len = min(len(word1), len(word2))

        if len(word1) > len(word2) and word1[:min_len] == word2[:min_len]:
            return ""

        for j in range(min_len):
            if word1[j] != word2[j]:
                graph[word1[j]].add(word2[j])
                break

    state: dict[str, int] = {}
    post_order: list[str] = []
    has_cycle = False

    def dfs(char: str) -> None:
        nonlocal has_cycle
        if has_cycle:
            return
        if char in state:
            if state[char] == 1:
                has_cycle = True
            return
        state[char] = 1
        for neighbor in graph[char]:
            dfs(neighbor)
        state[char] = 2
        post_order.append(char)

    for char in all_chars:
        if char not in state:
            dfs(char)

    if has_cycle:
        return ""
    return "".join(reversed(post_order))


if __name__ == "__main__":
    words = ["wrt", "wrf", "er", "ett", "rftt"]
    print(f"alien_order({words}) = '{alien_order(words)}'")
    words2 = ["z", "x", "z"]
    print(f"alien_order({words2}) = '{alien_order(words2)}'")
