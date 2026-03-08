# Insert Delete GetRandom O(1) (LeetCode #380)

🔗 [LeetCode 380: Insert Delete GetRandom O(1)](https://leetcode.com/problems/insert-delete-getrandom-o1/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

## Problem Statement

Implement a data structure that supports three operations, each in O(1) average time:
- `insert(val)` - Insert a value. Returns true if the item was not present.
- `remove(val)` - Remove a value. Returns true if the item was present.
- `getRandom()` - Return a random element with equal probability.

**Example:**
```
rs = RandomizedSet()
rs.insert(1)    // true
rs.insert(2)    // true
rs.insert(2)    // false (already present)
rs.getRandom()  // 1 or 2, each with 50% probability
rs.remove(1)    // true
rs.getRandom()  // 2 (only element)
```

**Constraints:**
- -2^31 <= val <= 2^31 - 1
- At most 2 * 10^5 calls total
- There will be at least one element when getRandom is called

---

## Thought Process

1. **O(1) insert and membership check** - Hash set handles this. But hash sets don't support random access by index.
2. **O(1) random element** - An array supports this (`random.choice`). But arrays have O(n) deletion from the middle.
3. **Combine both** - Use a list for random access and a hash map (value → index) for O(1) lookups. The trick is making deletion O(1).
4. **Deletion trick** - Swap the element to delete with the last element in the list, then pop from the end. Popping from the end of a Python list is O(1). Update the hash map to reflect the swap.

---

## Worked Example

This problem needs O(1) for three operations: insert, delete AND getRandom. No single data structure gives all three. A set gives O(1) insert and membership check, but picking a random element requires converting to a list first (O(n)). A list gives O(1) random access by index, but deleting from the middle shifts everything after it (O(n)).

The solution: use BOTH. A list stores values (for O(1) random access by index). A dict maps each value to its index in the list (for O(1) lookup). For deletion, we avoid the expensive middle-removal problem with a trick: swap the target with the last element, then pop from the end. Swapping is O(1) and popping from the end of a list is O(1).

The dict key is the value itself and the dict value is the index in the list where that value lives.

```
RandomizedSet()
  vals = [], idx_map = {}

insert(10) → True:
  10 not in idx_map. Append to vals, record its index.
  vals = [10], idx_map = {10: 0}

insert(30) → True:
  vals = [10, 30], idx_map = {10: 0, 30: 1}

insert(20) → True:
  vals = [10, 30, 20], idx_map = {10: 0, 30: 1, 20: 2}

insert(30) → False:
  30 already in idx_map. No change.

getRandom():
  random.choice(vals) picks index 0, 1 or 2 with equal probability.
  This works because vals is a contiguous list with no gaps.

remove(30) → True:
  30 is at index 1 (found via idx_map in O(1)).
  Last element is 20 at index 2.

  Step 1 - Swap 30 with the last element:
    vals[1] = 20, vals[2] = 30 → vals = [10, 20, 30]
    Update idx_map for 20: idx_map[20] = 1 (its new position)

  Step 2 - Pop the last element (which is now 30):
    vals.pop() → vals = [10, 20]
    Remove 30 from idx_map.
    Final: vals = [10, 20], idx_map = {10: 0, 20: 1}

  Why swap-and-pop? Removing from index 1 directly would require
  shifting 20 one position left - that's O(n) for a large list.
  Swapping with the last element and popping from the end is always O(1)
  regardless of which element we're removing or how big the list is.

insert(40) → True:
  vals = [10, 20, 40], idx_map = {10: 0, 20: 1, 40: 2}

getRandom():
  Still uniform: 1/3 chance for each value. The swap-and-pop
  preserved the contiguous structure of the list (no gaps).
```

---

## Approaches

### Approach: Hash Map + Array with Swap Deletion

<details>
<summary>💡 Hint</summary>

You can delete from the end of an array in O(1). Can you move the element you want to delete to the end first?

</details>

<details>
<summary>📝 Explanation</summary>

The challenge is that no single data structure gives O(1) for all three operations. A set gives O(1) insert and delete, but `getRandom` requires converting to a list first (O(n)). A list gives O(1) random access by index, but deleting from the middle is O(n) because all elements after the deleted one shift left.

The solution combines both:

**Array (`vals`):** Stores all current values in a contiguous list. `getRandom` calls `random.choice(vals)`, which picks a random index in O(1). This only works if the array has no gaps - every index from 0 to len-1 holds a valid value.

**Dict (`idx_map`):** Maps each value to its current index in the array. This gives O(1) lookup: "where in the array is value X?"

The critical trick is **swap-and-pop deletion**:

1. Look up the target value's index in the dict: `idx = idx_map[val]`.
2. Swap the target with the last element in the array. Update the dict entry for the element that was just moved.
3. Pop the last element from the array (O(1) - no shifting needed). Remove the target from the dict.

For example, removing value 30 from `vals = [10, 30, 20]`:
- 30 is at index 1. Last element is 20 at index 2.
- Swap: `vals = [10, 20, 30]`. Update dict: `idx_map[20] = 1`.
- Pop last: `vals = [10, 20]`. Remove 30 from dict.

The array stays contiguous (no gaps), so `getRandom` still works correctly.

**Time:** O(1) average for insert, remove and getRandom.
**Space:** O(n) - the array and dict each hold n entries.

This two-data-structure pattern (array for positional access + dict for value-based lookup) shows up whenever you need both random access and fast value-based operations.

</details>

<details>
<summary>💻 Code</summary>

```python
import random

class RandomizedSet:
    def __init__(self) -> None:
        self.val_to_index: dict[int, int] = {}
        self.values: list[int] = []

    def insert(self, val: int) -> bool:
        if val in self.val_to_index:
            return False
        self.val_to_index[val] = len(self.values)
        self.values.append(val)
        return True

    def remove(self, val: int) -> bool:
        if val not in self.val_to_index:
            return False
        idx = self.val_to_index[val]
        last_val = self.values[-1]
        self.values[idx] = last_val
        self.val_to_index[last_val] = idx
        self.values.pop()
        del self.val_to_index[val]
        return True

    def get_random(self) -> int:
        return random.choice(self.values)
```

</details>

---

## Edge Cases

| Case | Scenario | Why It Matters |
|------|----------|----------------|
| Insert duplicate | `insert(1)` twice | Must return False, not add again |
| Remove nonexistent | `remove(999)` | Must return False, not crash |
| Remove last element | Element to remove is already at end of list | Swap is a no-op, still need to pop and delete from map |
| Re-insert after remove | `insert(1)`, `remove(1)`, `insert(1)` | Should work normally |
| Single element | Insert one, getRandom | Must return that element |

---

## Common Pitfalls

1. **Not updating the swapped element's index** - After swapping, the element that moved must have its index updated in the map
2. **Removing the last element** - When the target is already the last element, the "swap" overwrites it with itself. The code still works but be aware of the edge case.
3. **Using a set instead of a list** - Sets don't support random indexing. `random.choice(set)` converts to a list internally, which is O(n).

---

## Interview Tips

**What to say:**
> "getRandom needs uniform probability, which means I need index-based access - so a list. But list deletion is O(n) from the middle. I can fix that by swapping with the last element and popping. A hash map tracks where each element is in the list."

**This problem tests your ability to combine data structures.** The insight isn't any single data structure - it's recognizing that combining a hash map with an array covers all three requirements.

**Follow-up: "What about duplicates?"**
→ For the follow-up problem (LeetCode 381), each value can appear multiple times. You'd need to map each value to a set of indices instead of a single index.

**What the interviewer evaluates at each stage:** Recognizing that no single data structure covers all three operations tests analytical thinking. The swap-and-pop deletion trick tests creative problem-solving. Understanding why the array must stay contiguous (for uniform random sampling) tests your grasp of the probability requirement. At principal level, connecting this to reservoir sampling and distributed random selection shows breadth.

---

## DE Application

This pattern appears in data engineering when:
- Building sampling systems that need to add/remove elements and randomly sample from the current set
- Reservoir sampling implementations where the reservoir needs efficient updates
- Load balancer implementations that randomly select from available workers while workers come and go

---

## At Scale

The array + hash map combination uses O(n) memory for n elements. The GetRandom operation is O(1) because arrays support random index access. At scale, uniform random sampling from a distributed dataset is harder than it sounds: you can't just pick a random index if the data is spread across 1000 partitions. Reservoir sampling handles this - maintain a sample of size k, and for each new element decide probabilistically whether to include it. Spark's `df.sample(fraction)` uses a similar approach. The insert/delete/getRandom combination appears in load balancers (random backend selection) and A/B test assignment.

---

## Related Problems

- [381. Insert Delete GetRandom O(1) - Duplicates Allowed](https://leetcode.com/problems/insert-delete-getrandom-o1-duplicates-allowed/) - Extension with duplicate handling
- [146. LRU Cache](146_lru_cache.md) - Another "design a data structure" problem combining hash map + linked list
