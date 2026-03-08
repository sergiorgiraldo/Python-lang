"""
LeetCode 981: Time Based Key-Value Store

Pattern: Binary Search in Design
Difficulty: Medium
Time Complexity: O(log n) per get, O(1) per set
Space Complexity: O(n) total storage
"""

import bisect
from collections import defaultdict


class TimeMap:
    """
    Key-value store with versioned values by timestamp.

    set(key, value, timestamp) stores a value at a given time.
    get(key, timestamp) returns the value with the largest timestamp
    that is <= the given timestamp.

    Values for each key are stored in timestamp order. Since timestamps
    are strictly increasing per the constraints, we can append and
    binary search.
    """

    def __init__(self):
        # key -> list of (timestamp, value) pairs, sorted by timestamp
        self.store: dict[str, list[tuple[int, str]]] = defaultdict(list)

    def set(self, key: str, value: str, timestamp: int) -> None:
        """Store value at timestamp. O(1) since timestamps are increasing."""
        self.store[key].append((timestamp, value))

    def get(self, key: str, timestamp: int) -> str:
        """
        Get value at or before timestamp. O(log n) via binary search.

        Find the rightmost entry with ts <= timestamp using bisect_right.
        bisect_right gives the insertion point for (timestamp + 1),
        which is one past the last entry with ts <= timestamp.
        """
        entries = self.store[key]
        if not entries:
            return ""

        # bisect_right on the timestamp component.
        # (timestamp, chr(127)) sorts after any (timestamp, value) for
        # ASCII values, so bisect_right returns one past the last match.
        # Alternative: bisect_left(entries, (timestamp + 1,)) avoids
        # the chr(127) trick entirely and works for any string values.
        idx = bisect.bisect_right(entries, (timestamp, chr(127)))

        if idx == 0:
            return ""  # All timestamps are after the query time

        return entries[idx - 1][1]


class TimeMapManual:
    """
    Same behavior, manual binary search instead of bisect.

    Use this version if the interviewer wants to see the binary search
    implementation rather than a library call.
    """

    def __init__(self):
        self.store: dict[str, list[tuple[int, str]]] = defaultdict(list)

    def set(self, key: str, value: str, timestamp: int) -> None:
        self.store[key].append((timestamp, value))

    def get(self, key: str, timestamp: int) -> str:
        entries = self.store[key]
        if not entries:
            return ""

        # Find rightmost entry with ts <= timestamp
        left, right = 0, len(entries) - 1
        result = ""

        while left <= right:
            mid = (left + right) // 2
            if entries[mid][0] <= timestamp:
                result = entries[mid][1]  # Candidate answer
                left = mid + 1  # Look for a later valid timestamp
            else:
                right = mid - 1

        return result


if __name__ == "__main__":
    tm = TimeMap()
    tm.set("foo", "bar", 1)
    tm.set("foo", "bar2", 4)

    tests = [
        ("foo", 1, "bar"),
        ("foo", 3, "bar"),
        ("foo", 4, "bar2"),
        ("foo", 5, "bar2"),
        ("foo", 0, ""),
        ("missing", 1, ""),
    ]

    for key, ts, expected in tests:
        result = tm.get(key, ts)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status}: get('{key}', {ts}) = '{result}'")
