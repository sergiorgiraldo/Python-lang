# LRU Cache (LeetCode #146)

🔗 [LeetCode 146: LRU Cache](https://leetcode.com/problems/lru-cache/)

> **Difficulty:** Medium | **Interview Frequency:** Very Common

## Problem Statement

Design a data structure that follows the Least Recently Used (LRU) eviction policy. Implement `get` and `put` operations, both in O(1) time.

- `get(key)` - Return the value if the key exists, otherwise return -1. Mark as recently used.
- `put(key, value)` - Insert or update the key-value pair. If at capacity, evict the least recently used key first.

**Example:**
```
LRUCache cache = new LRUCache(2)
cache.put(1, 1)
cache.put(2, 2)
cache.get(1)       // returns 1
cache.put(3, 3)    // evicts key 2
cache.get(2)       // returns -1 (not found)
```

**Constraints:**
- 1 <= capacity <= 3000
- 0 <= key <= 10^4
- 0 <= value <= 10^5
- At most 2 * 10^5 calls to get and put

---

## Thought Process

1. **What operations need to be O(1)?** Both get and put, including eviction.
2. **Hash map gives O(1) lookup** - but doesn't track access order.
3. **Linked list gives O(1) insert/delete** - but doesn't give O(1) lookup by key.
4. **Combine both** - Hash map for lookup, doubly linked list for ordering. The map values point to list nodes.
5. **Python shortcut** - `OrderedDict` does exactly this internally. Use it in practice, but know how to build it from scratch.

---

## Worked Example

An LRU (Least Recently Used) cache evicts the item that hasn't been accessed for the longest time when the cache is full. It needs two things to be fast: O(1) lookup by key (a dict) and O(1) tracking of usage order (a doubly linked list).

The dict's key is the cache key and the value is a reference to a node in the linked list. The linked list keeps items in order from least recently used (front) to most recently used (back). Every time we access or add an item, it moves to the back. When we need to evict, we remove from the front.

A dict alone can't track order. A list alone can't do O(1) lookup by key. Together they cover each other's weakness. This combination is common enough that Python provides `OrderedDict` which wraps both into one structure.

```
LRUCache(capacity=3)

put(1, "A"):
  Dict: {1 → "A"}, order: [1]
  (1 is both least and most recent, cache has room)

put(2, "B"):
  Dict: {1 → "A", 2 → "B"}, order: [1, 2]

put(3, "C"):
  Dict: {1, 2, 3}, order: [1, 2, 3]
  Cache is now full (3 out of 3 slots used).

get(1) → returns "A":
  Found in dict (O(1) lookup). Move node 1 to the back of the list.
  Order: [2, 3, 1]   (key 2 is now the least recently used)

put(4, "D"):
  Cache is full. Must evict the least recently used = front of list = key 2.
  Remove key 2 from dict and from front of list.
  Add key 4 at the back.
  Dict: {1 → "A", 3 → "C", 4 → "D"}, order: [3, 1, 4]

get(2) → returns -1:
  Key 2 was evicted. Not in dict. Return -1.

get(3) → returns "C":
  Found. Move 3 to back. Order: [1, 4, 3]

put(5, "E"):
  Cache full. Evict front = key 1 ("A").
  Dict: {3 → "C", 4 → "D", 5 → "E"}, order: [4, 3, 5]

get(1) → returns -1:
  Key 1 was evicted. Not in dict.

Notice that key 1 survived the first eviction (key 2 was evicted instead)
because the get(1) call moved it to the back of the usage order. But after
being untouched while keys 3, 4 and 5 were accessed, it drifted to the
front and eventually got evicted. The linked list captures this usage
history naturally - the front is always the stalest item.
```

---

## Approaches

### Approach 1: OrderedDict (Pythonic)

<details>
<summary>📝 Explanation</summary>

Python's `OrderedDict` from the `collections` module is a dict that remembers insertion order AND provides O(1) methods to rearrange that order. It's a perfect fit for LRU because it gives us:

- `move_to_end(key)` - moves a key to the most-recent position in O(1)
- `popitem(last=False)` - removes and returns the least-recent (front) item in O(1)
- Regular dict `__getitem__` and `__setitem__` for O(1) lookup and insertion

The implementation:
- **get(key):** If the key exists, call `move_to_end(key)` to mark it as most recently used, then return the value. If not, return -1.
- **put(key, value):** If the key already exists, update its value and `move_to_end(key)`. If it's new and the cache is at capacity, call `popitem(last=False)` to evict the least recently used item. Then insert the new key-value pair.

**Time:** O(1) for both get and put. All operations (dict lookup, move_to_end, popitem) are O(1).
**Space:** O(capacity) - the OrderedDict holds at most `capacity` entries.

This is the cleanest approach for production Python code. In an interview, some interviewers want to see the manual implementation below to prove you understand the underlying data structures. Ask which they prefer.

</details>

<details>
<summary>💻 Code</summary>

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.cache: OrderedDict[int, int] = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
```

</details>

---

### Approach 2: Hash Map + Doubly Linked List (From Scratch)

<details>
<summary>💡 Hint</summary>

You need O(1) lookup (hash map) and O(1) reordering (linked list). Combine them: the map stores references to list nodes.

</details>

<details>
<summary>📝 Explanation</summary>

Building it from scratch to understand what `OrderedDict` does under the hood. We need two data structures working together:

**Hash map (dict):** Maps each cache key to its corresponding node in the linked list. This gives us O(1) lookup by key.

**Doubly linked list:** Maintains the usage order from least recently used (head) to most recently used (tail). A doubly linked list lets us remove any node from the middle in O(1) (given a reference to the node) and insert at the tail in O(1). A singly linked list can't do O(1) removal from the middle because you'd need to find the previous node first.

The implementation uses **sentinel nodes** (dummy head and tail) to avoid null checks. The real items live between the sentinels.

- **get(key):** Look up the key in the dict → get the node. Remove the node from its current position in the linked list (O(1) pointer updates), insert it at the tail (most recent). Return the value.
- **put(key, value):** If the key exists, update the node's value and move it to the tail. If it's new and we're at capacity, remove the node right after the head sentinel (least recent), delete its key from the dict. Create a new node, insert it at the tail, add the key to the dict.

Each operation involves: one dict lookup + a constant number of pointer reassignments = O(1).

**Time:** O(1) for both operations.
**Space:** O(capacity) - one dict entry and one list node per cached item, plus two sentinel nodes.

The sentinel trick is worth knowing: head.next is always the least recently used item, tail.prev is always the most recently used. No special cases for empty lists or single-element lists.

</details>

<details>
<summary>💻 Code</summary>

```python
class LRUCacheManual:
    class _Node:
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
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)
        self._add_to_end(node)
        return node.val

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self._remove(self.cache[key])

        node = self._Node(key, value)
        self.cache[key] = node
        self._add_to_end(node)

        if len(self.cache) > self.capacity:
            lru = self.head.next
            assert lru is not None
            self._remove(lru)
            del self.cache[lru.key]
```

</details>

---

## Edge Cases

| Case | Scenario | Why It Matters |
|------|----------|----------------|
| Capacity 1 | Every new put evicts the previous entry | Minimum capacity boundary |
| Update existing key | `put(key, new_value)` should update, not add a duplicate | Recency must update too |
| Get updates recency | `get(key)` should move it to most recent | Prevents premature eviction |
| Sequential eviction | Fill to capacity, then add N more | Eviction order is correct |

---

## Common Pitfalls

1. **Not updating recency on put for existing keys** - If key already exists, it must move to most recent
2. **Not updating recency on get** - A get counts as "using" the key
3. **Forgetting sentinel nodes in manual implementation** - Without sentinels, you need null checks everywhere
4. **Memory leak in manual implementation** - When evicting, remove from both the map and the list

---

## Interview Tips

**What to say:**
> "I need O(1) for both lookup and order maintenance. A hash map gives O(1) lookup but no ordering. A linked list gives O(1) insert/delete but no random access. Combining them - hash map pointing to linked list nodes - gives both."

**Interviewers will usually ask for the manual implementation.** The OrderedDict approach is worth mentioning (shows you know the standard library) but be ready to build the doubly linked list version.

**Follow-up: "What about thread safety?"**
> You'd need locking around the get/put operations. In production, consider `functools.lru_cache` for simple cases or Redis for distributed caching.

**What the interviewer evaluates at each stage:** The OrderedDict approach tests standard library knowledge. The manual implementation tests data structure design - can you combine two structures (hash map + doubly linked list) to cover each other's weaknesses? The sentinel node technique tests implementation craft. At principal level, discussing distributed caching (consistent hashing, cache invalidation, eviction policies) shows you think beyond single-machine solutions.

---

## DE Application

LRU caching appears everywhere in data engineering:
- Caching dimension table lookups to avoid repeated database queries
- Connection pool management (evict least recently used connections)
- Query result caching in data serving layers
- Buffer pool management in database internals

Understanding LRU at this level helps when debugging cache hit rates, sizing cache capacity or choosing eviction policies (LRU vs LFU vs TTL).

---

## At Scale

The LRU cache stores at most `capacity` entries. This is bounded by design - the whole point is fixed memory. At scale, the question shifts from implementation to architecture: a single-machine LRU cache handles ~1M entries comfortably. For distributed caching, you shard by key across machines (consistent hashing for rebalancing) and accept that cross-shard operations like "evict globally least-recent" are expensive. Redis and Memcached implement this pattern at production scale. An interviewer asking about LRU at scale wants to hear about cache invalidation, consistency and eviction policies - not the linked-list implementation.

---

## Related Problems

- [460. LFU Cache](https://leetcode.com/problems/lfu-cache/) - Evicts least frequently (not recently) used
- [380. Insert Delete GetRandom O(1)](380_insert_delete_random.md) - Another "design a data structure" problem combining hash map with something else
