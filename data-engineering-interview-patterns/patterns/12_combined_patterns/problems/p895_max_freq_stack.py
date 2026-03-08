"""
LeetCode 895: Maximum Frequency Stack

Combined Patterns: Hash Map (frequency tracking) + Stack (LIFO per frequency)
Difficulty: Hard
Time Complexity: O(1) per push and pop
Space Complexity: O(n)
"""


class FreqStack:
    """
    Stack where pop removes the most frequent element.
    Ties broken by recency (most recently pushed).

    Two hash maps work together:
    - freq: element -> current frequency
    - group: frequency -> stack of elements at that frequency

    Push: increment freq[x], append x to group[freq[x]].
    Pop: pop from group[max_freq]. If that group is now empty, decrement max_freq.

    The key insight: an element pushed 3 times appears in group[1],
    group[2] AND group[3]. Popping from group[3] "demotes" it back
    to frequency 2, where it still exists in group[2].
    """

    def __init__(self) -> None:
        self.freq: dict[int, int] = {}
        self.group: dict[int, list[int]] = {}
        self.max_freq: int = 0

    def push(self, val: int) -> None:
        f = self.freq.get(val, 0) + 1
        self.freq[val] = f

        if f not in self.group:
            self.group[f] = []
        self.group[f].append(val)

        self.max_freq = max(self.max_freq, f)

    def pop(self) -> int:
        val = self.group[self.max_freq].pop()
        self.freq[val] -= 1

        if not self.group[self.max_freq]:
            self.max_freq -= 1

        return val
