"""
LeetCode 146: LRU Cache

Pattern: Hash Map + Doubly Linked List
Difficulty: Medium
Time Complexity: O(1) for get and put
Space Complexity: O(capacity)
"""

from collections import OrderedDict


class LRUCache:
    """
    Least Recently Used cache with O(1) get and put.

    Uses OrderedDict which combines a hash map with a doubly linked
    list internally. This is the Pythonic approach.

    Args:
        capacity: Maximum number of entries.

    Example:
        >>> cache = LRUCache(2)
        >>> cache.put(1, 1)
        >>> cache.put(2, 2)
        >>> cache.get(1)
        1
        >>> cache.put(3, 3)  # evicts key 2
        >>> cache.get(2)
        -1
    """

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.cache: OrderedDict[int, int] = OrderedDict()

    def get(self, key: int) -> int:
        """Return value for key and mark as recently used. -1 if not found."""
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        """Insert or update key-value pair. Evict LRU if at capacity."""
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)


class LRUCacheManual:
    """
    Manual implementation using a hash map and doubly linked list.

    Shows what OrderedDict does under the hood. This is what
    interviewers want to see if they ask you to implement from scratch.

    The hash map gives O(1) lookup by key.
    The doubly linked list gives O(1) insert/delete for ordering.
    """

    class _Node:
        """Doubly linked list node."""

        __slots__ = ("key", "val", "prev", "next")

        def __init__(self, key: int = 0, val: int = 0) -> None:
            self.key = key
            self.val = val
            self.prev: LRUCacheManual._Node | None = None
            self.next: LRUCacheManual._Node | None = None

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.cache: dict[int, LRUCacheManual._Node] = {}

        # Sentinel nodes simplify edge cases
        self.head = self._Node()
        self.tail = self._Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: _Node) -> None:
        """Remove a node from the linked list."""
        prev_node = node.prev
        next_node = node.next
        assert prev_node is not None and next_node is not None
        prev_node.next = next_node
        next_node.prev = prev_node

    def _add_to_end(self, node: _Node) -> None:
        """Add a node right before tail (most recently used position)."""
        prev_node = self.tail.prev
        assert prev_node is not None
        prev_node.next = node
        node.prev = prev_node
        node.next = self.tail
        self.tail.prev = node

    def get(self, key: int) -> int:
        """Return value for key and mark as recently used. -1 if not found."""
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)
        self._add_to_end(node)
        return node.val

    def put(self, key: int, value: int) -> None:
        """Insert or update key-value pair. Evict LRU if at capacity."""
        if key in self.cache:
            self._remove(self.cache[key])

        node = self._Node(key, value)
        self.cache[key] = node
        self._add_to_end(node)

        if len(self.cache) > self.capacity:
            # Evict the least recently used (right after head sentinel)
            lru = self.head.next
            assert lru is not None
            self._remove(lru)
            del self.cache[lru.key]


if __name__ == "__main__":
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    print(f"get(1) = {cache.get(1)}")  # 1
    cache.put(3, 3)  # evicts key 2
    print(f"get(2) = {cache.get(2)}")  # -1
    cache.put(4, 4)  # evicts key 1
    print(f"get(1) = {cache.get(1)}")  # -1
    print(f"get(3) = {cache.get(3)}")  # 3
    print(f"get(4) = {cache.get(4)}")  # 4
