"""
LeetCode 380: Insert Delete GetRandom O(1)

Pattern: Hash Map + Dynamic Array
Difficulty: Medium
Time Complexity: O(1) average for all operations
Space Complexity: O(n)
"""

import random


class RandomizedSet:
    """
    Data structure supporting insert, delete and getRandom in O(1) average time.

    The trick: use a list for O(1) random access (pick a random index)
    and a hash map for O(1) lookup/delete (map value to its index in the list).

    Deletion swaps the target element with the last element in the list,
    then pops from the end. This avoids the O(n) cost of removing from
    the middle of a list.

    Example:
        >>> rs = RandomizedSet()
        >>> rs.insert(1)
        True
        >>> rs.insert(2)
        True
        >>> rs.remove(1)
        True
        >>> rs.get_random() in (1, 2)
        True
    """

    def __init__(self) -> None:
        self.val_to_index: dict[int, int] = {}
        self.values: list[int] = []

    def insert(self, val: int) -> bool:
        """
        Insert a value. Returns True if the value was not already present.
        """
        if val in self.val_to_index:
            return False
        self.val_to_index[val] = len(self.values)
        self.values.append(val)
        return True

    def remove(self, val: int) -> bool:
        """
        Remove a value. Returns True if the value was present.

        Swaps with the last element to maintain O(1) deletion from the list.
        """
        if val not in self.val_to_index:
            return False

        # Swap target with last element
        idx = self.val_to_index[val]
        last_val = self.values[-1]

        self.values[idx] = last_val
        self.val_to_index[last_val] = idx

        # Remove the last element (now a duplicate)
        self.values.pop()
        del self.val_to_index[val]

        return True

    def get_random(self) -> int:
        """Return a random element. Each element has equal probability."""
        return random.choice(self.values)


if __name__ == "__main__":
    rs = RandomizedSet()
    print(f"insert(1): {rs.insert(1)}")  # True
    print(f"insert(2): {rs.insert(2)}")  # True
    print(f"insert(2): {rs.insert(2)}")  # False (duplicate)
    print(f"remove(1): {rs.remove(1)}")  # True
    print(f"remove(3): {rs.remove(3)}")  # False (not found)
    print(f"getRandom: {rs.get_random()}")  # 2
