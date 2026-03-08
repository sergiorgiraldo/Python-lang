# Hash Map Pattern

## What Is It?

### The basics

In Python, a hash map is a **dictionary** (`dict`). You've used one every time you wrote `my_dict[key] = value`.

A dict stores pairs: a **key** and a **value** that goes with it. Think of it like a contacts list on your phone. You don't scroll through every contact to find someone - you type their name and jump straight to them. A dict works the same way. You give it a key, it gives you the value instantly.

```python
# storing and looking up values
prices = {"apple": 1.50, "banana": 0.75, "milk": 4.99}
prices["banana"]  # → 0.75, found instantly

# adding a new entry
prices["bread"] = 3.49
```

Each dict is completely independent. Two dicts can use the same key without interfering:

```python
fruits = {42: "banana"}
colors = {42: "red"}
fruits[42]  # → "banana"
colors[42]  # → "red"
# same key, different dicts, no conflict
```

### Why dicts are fast (and lists aren't)

Compare a dict to a list. A list is just values lined up in order with no keys - like a stack of papers with no labels. The only way to find something is to look through them one at a time:

```python
# list: no keys, have to search through it
my_list = [5, 8, 42, 3, 17]
# "is 42 in here?" → Python checks 5, then 8, then 42. Found it (3 checks).
# "is 99 in here?" → Python checks all 5 values. Not found (5 checks).
```

For a short list, that's fine. But if the list has a million items and the one you want is near the end, Python checks nearly every one.

A dict with a million items still finds any key instantly.

That speed difference is what **O(1) vs O(n)** means:
- **O(1)** means "takes the same time no matter how big the data is" (dict lookup)
- **O(n)** means "takes longer as the data gets bigger" (list scan)

When n is 10, you won't notice. When n is 10 million, it's the difference between a millisecond and seconds.

If you've worked with SQL, you've already seen this. Querying an indexed column is fast because the database jumps straight to the matching row - like a dict. Querying a column with no index forces a full table scan, checking every row - like searching a list.

### How hashing works under the hood

When you write `prices["banana"] = 0.75`, Python takes the key `"banana"` and runs it through a **hash function** - a formula that turns any value into a number. Think of it like a formula that converts a name into a locker number. `"banana"` might hash to locker 4,571. Python stores 0.75 in that locker.

Later, when you check `prices["banana"]`, Python runs `"banana"` through the same formula, gets 4,571 again, goes straight to that locker and finds 0.75. No searching.

Different keys hash to different lockers. `"apple"` might hash to locker 2,103. `"milk"` to locker 8,847. Each key gets its own spot.

Occasionally two different keys hash to the same locker number (called a **collision**). Python handles this automatically - you don't need to worry about it in practice. Lookups are still effectively instant.

The important thing to remember: the hash function only works on **exact matches**. It can tell you "is `banana` in here?" instantly. It cannot tell you "is there anything similar to `banana`?" or "what comes after `banana` alphabetically?" For those questions you need different data structures (like binary search, pattern 03).

### Dicts are not sorted

A dict does not sort its keys. If you store keys 42, 7, 100 and 3, they don't get rearranged into 3, 7, 42, 100. The dict doesn't know or care that 3 < 7 < 42 < 100. It just hashes each key to a memory slot and stores it there.

(Python 3.7+ dicts do remember **insertion order** - the order you added items. But that's not the same as sorted order. If you add 42 first and 3 second, iterating gives you 42 then 3.)

This means:
- A dict **can** answer "is X in here? what's the value for X?" instantly
- A dict **cannot** answer "what's the key closest to X?" or "give me all keys between A and B"

### What can be a key?

Not everything. Keys have to be **hashable**, which in practice means they can't change after creation (immutable). Strings, numbers and tuples are all fine. Lists and dicts can't be keys because they can change - if they changed after being stored, the hash would be wrong and Python couldn't find them in their locker anymore.

```python
# these work as keys
my_dict["hello"] = 1     # string key
my_dict[42] = 2          # int key
my_dict[(1, 2, 3)] = 3   # tuple key

# these DO NOT work as keys
my_dict[[1, 2, 3]] = 4   # TypeError! lists are mutable
my_dict[{"a": 1}] = 5    # TypeError! dicts are mutable
```

This comes up in the problems. In Group Anagrams (problem 49), we sort the letters of a word and use the result as a key. But `sorted("eat")` returns a list `['a', 'e', 't']`, which can't be a key. So we convert it to a tuple or join it into a string `"aet"` first. That's not a random implementation detail - it's because of how hashing works.

### Dict vs set

A **set** is a dict without values. Under the hood it uses the same hashing for O(1) lookup. Use a set when you only care about "is this thing in here?" Use a dict when you also need to store data alongside each key.

```python
# set: just tracking membership ("have I seen this?")
seen = set()
seen.add(42)
42 in seen  # True

# dict: tracking membership + associated data ("where did I see this?")
seen = {}
seen[42] = 0  # storing the index where we saw 42
42 in seen   # True
seen[42]     # 0 (the associated data)
```

Several problems in this pattern (Contains Duplicate, Longest Consecutive) use sets because they only need the "is it in here?" check. Others (Two Sum, Subarray Sum) use dicts because they need associated data like indices or counts.

### What happens when a key doesn't exist?

Looking up a missing key crashes with a `KeyError`. That's why our code always checks membership first, or uses safe alternatives:

```python
prices = {"apple": 1.50}

# this crashes
prices["banana"]              # KeyError!

# these are safe
"banana" in prices            # False (check first, then access)
prices.get("banana", 0)       # 0 (returns a default instead of crashing)

# for counting patterns, defaultdict creates missing keys automatically
from collections import defaultdict
counts = defaultdict(int)     # missing keys default to 0
counts["banana"] += 1         # no KeyError, creates the key with 0 then adds 1
```

### How much memory does a dict use?

A dict holding n keys uses roughly O(n) memory. Each entry stores the key, the value and some overhead. For interview purposes the answer is "proportional to how many items you put in it."

The trade-off across all hash map problems is the same: we're **spending extra memory** (the dict) **to save time** (O(1) lookups instead of O(n) scans). This is almost always worth it.

### What the problems in this section are really asking

Every hash map problem uses a dict (or set), but what you use as the **key** changes based on what you're trying to look up:

| Problem | Key | Value | What we're asking the dict |
|---|---|---|---|
| Two Sum | the number itself | its index | "Have I already seen a number that completes my pair?" |
| Contains Duplicate | the number itself | (none, just a set) | "Have I seen this exact number before?" |
| Valid Anagram | each character | its count | "Do both strings have the same character counts?" |
| Group Anagrams | sorted letters of a word | list of original words | "Which words are rearrangements of each other?" |
| Top K Frequent | each number | its count | "How many times has each number appeared?" |
| Longest Consecutive | the number itself | (none, just a set) | "Is a number's neighbor in the set?" |
| Subarray Sum = K | a running total (prefix sum) | how many times we've seen that total | "Has this running total appeared before?" |
| LRU Cache | the cache key | cached value + position in usage order | "What's stored here and when was it last used?" |
| Insert Delete GetRandom | the value itself | its position in an array | "Where in the array is this value?" |
| Design Twitter | user ID | list of tweets / set of followers | "What has this user posted? Who do they follow?" |

The first few are intuitive - the key is a number or character directly from the input. Subarray Sum is the trickiest because the key is a *computed value* (the running total so far), not something you can see directly in the input.

## When to Use It

**Recognition signals in interviews:**
- "Find a pair that..."
- "Check if we've seen..."
- "Count occurrences of..."
- "Group by..."
- Any time you're doing repeated lookups in a loop - that nested O(n) search is a sign you need a hash map

## Visual Aid

```
Problem: Find two numbers that sum to 14

Array: [8, 3, 11, 5, 9, 2, 7]  Target: 14

Without hash map (brute force - check every pair):
  8+3=11  8+11=19  8+5=13  8+9=17  8+2=10  8+7=15
  3+11=14 ✓  Found it after 7 comparisons. But we got lucky.
  Worst case: check all 21 pairs. For n=10,000: ~50 million pairs.

With hash map (single pass):
  num=8   need 14-8=6   seen={}                         6 not there → store {8: 0}
  num=3   need 14-3=11  seen={8:0}                      11 not there → store {8:0, 3:1}
  num=11  need 14-11=3  seen={8:0, 3:1}                 3 IS there at index 1 → return [1, 2]

  Found it in 3 steps. For n=10,000: at most 10,000 steps (not 50 million).

The dict turned "scan the whole array for the complement" into "check one slot."
That's the pattern: use a dict to remember what you've seen so you don't re-scan.
```

## Template

```python
from collections import defaultdict

def hash_map_pattern(items):
    seen = {}  # or defaultdict, Counter, set

    for i, item in enumerate(items):
        # Check if what we need already exists
        if condition_met(item, seen):
            return result

        # Store current item for future iterations
        seen[item] = i  # or += 1, or .add()

    return default_result
```

## Time/Space Complexity

| Operation | Average | Worst Case |
|-----------|---------|------------|
| Lookup    | O(1)    | O(n)       |
| Insert    | O(1)    | O(n)       |
| Delete    | O(1)    | O(n)       |
| Space     | O(n)    | O(n)       |

Worst case happens with hash collisions. For interviews, assume O(1) unless asked.

### A Note on O(1) "Average Case"

Hash map operations are O(1) on average but O(n) in the worst case. In practice, worst-case behavior is rare, but understanding when it can happen matters for interviews:

- **Hash collisions** - Multiple keys hash to the same bucket. Python's dict handles this well with open addressing and perturbation, but a pathological set of keys can still cause clustering. In CPython, the hash of small integers is the integer itself, so inserting keys 0, 8, 16, 24... (multiples of the table size) would all collide.
- **Adversarial input** - In competitive programming or security-sensitive contexts, an attacker who knows your hash function can craft inputs that force O(n) per operation. Python mitigates this with hash randomization (since Python 3.3).
- **Resize storms** - When a hash map exceeds its load factor, it resizes (typically doubles). This single resize is O(n), but it happens infrequently enough that the amortized cost per operation stays O(1).

**For interviews:** assume O(1) unless asked. If the interviewer pushes on worst case, mention hash collisions and amortized resizing. If they ask how to guarantee O(1), mention consistent hashing or perfect hashing for static key sets.

**For production:** Python's built-in dict is well-optimized. You'd need millions of operations on a poorly distributed key space to notice worst-case behavior. If you're concerned, profile before optimizing.

### Connection to data engineering

If you work with data, you use hash maps constantly:

- **Deduplication:** Track which IDs you've already seen. `if record_id in seen: skip` is O(1).
- **Aggregation:** Group-by operations accumulate values by key. `totals[category] += amount` is a hash map.
- **Lookup tables:** Enrich streaming records by joining against a dict of reference data. This is a hash join.
- **Frequency counting:** Count occurrences of values in a column. `Counter(column_values)` builds a frequency dict in O(n).
- **Caching:** Memoize expensive computations. `if key in cache: return cache[key]` avoids recomputation.

The SQL equivalents: GROUP BY uses hash aggregation internally. JOIN often uses a hash join. DISTINCT uses a hash set. COUNT(*) GROUP BY builds a frequency map. Understanding hash maps helps you reason about why these SQL operations have the performance characteristics they do.

## Trade-offs

**The core trade-off in every hash map problem is memory for speed.** You're spending O(n) extra memory (the dict) to avoid O(n) repeated scans. This brings the total time from O(n^2) down to O(n). Almost always worth it.

**When hash maps don't help:**
- If you need data in sorted order, a dict can't help (it doesn't sort). Use sorting or binary search (pattern 03).
- If you need the "closest" or "nearest" value rather than an exact match, a dict can't help. Again, binary search.
- If memory is extremely constrained and the data is sorted, two pointers (pattern 02) solves some of the same problems in O(1) space.

**A note on worst case:** the complexity table shows O(n) worst case for lookups. This happens if many keys hash to the same slot (lots of collisions). In practice with Python's dict implementation, this almost never happens. For interview purposes, treat dict operations as O(1).

### Scale characteristics

A Python dict storing n integer keys uses roughly 80-120 bytes per entry (key object + hash + pointer overhead). For reference:

| n | Approximate memory | Fits in a single machine? |
|---|---|---|
| 100K | ~10 MB | Easily |
| 10M | ~1 GB | Yes |
| 100M | ~10 GB | Tight (typical worker has 8-16 GB) |
| 1B | ~100 GB | No - need distributed approach |

**Distributed equivalent:** Hash maps become hash-partitioned joins in Spark/Flink. The key is hashed to determine which partition (worker) owns it. This is a shuffle operation - expensive because it moves data across the network. Broadcast joins avoid the shuffle by sending the smaller table to every worker, but only work when one side fits in memory.

**Key skew:** If one key appears far more often than others (e.g., user_id = "anonymous" accounts for 30% of events), the partition handling that key gets 30% of the work while others sit idle. Solutions: salting the key (appending a random suffix, joining on both original and salted key), pre-aggregating the hot key separately or using a broadcast join for the skewed portion.

### SQL equivalent

The hash map pattern maps directly to hash joins in SQL engines. When you write `SELECT * FROM orders JOIN customers ON orders.customer_id = customers.id`, the engine builds a hash table from the smaller table and probes it with the larger table. The SQL section's joins subsection covers join strategies including when engines choose hash joins vs sort-merge joins.

## Problems

| # | Problem | Difficulty | Key Concept |
|---|---------|------------|-------------|
| [1](https://leetcode.com/problems/two-sum/) | [Two Sum](problems/001_two_sum.md) | Easy | Complement lookup |
| [217](https://leetcode.com/problems/contains-duplicate/) | [Contains Duplicate](problems/217_contains_duplicate.md) | Easy | Existence check with set |
| [242](https://leetcode.com/problems/valid-anagram/) | [Valid Anagram](problems/242_valid_anagram.md) | Easy | Frequency counting |
| [49](https://leetcode.com/problems/group-anagrams/) | [Group Anagrams](problems/049_group_anagrams.md) | Medium | Grouping by computed key |
| [347](https://leetcode.com/problems/top-k-frequent-elements/) | [Top K Frequent Elements](problems/347_top_k_frequent.md) | Medium | Counting + selection |
| [128](https://leetcode.com/problems/longest-consecutive-sequence/) | [Longest Consecutive Sequence](problems/128_longest_consecutive.md) | Medium | Set for O(1) neighbor check |
| [560](https://leetcode.com/problems/subarray-sum-equals-k/) | [Subarray Sum Equals K](problems/560_subarray_sum_k.md) | Medium | Prefix sum + hash map |
| [146](https://leetcode.com/problems/lru-cache/) | [LRU Cache](problems/146_lru_cache.md) | Medium | Hash map + doubly linked list |
| [380](https://leetcode.com/problems/insert-delete-getrandom-o1/) | [Insert Delete GetRandom O(1)](problems/380_insert_delete_random.md) | Medium | Hash map + array |
| [355](https://leetcode.com/problems/design-twitter/) | [Design Twitter](problems/355_design_twitter.md) | Medium | Multiple hash maps + merge |

**Suggested order:** 1, 217 → 242 → 49 → 347, 128 → 560 → 146, 380 → 355

Start with the easy problems to build intuition, then work through the mediums. LRU Cache and Design Twitter are more complex design problems that combine hash maps with other structures.

## DE Scenarios

| Scenario | What It Demonstrates |
|----------|---------------------|
| [Build Lookup Table](de_scenarios/build_lookup_table.md) | Enriching events with reference data |
| [Deduplication in Streaming](de_scenarios/deduplication_streaming.md) | Tracking seen records by key |
| [Single-Pass Aggregation](de_scenarios/single_pass_aggregation.md) | Implementing GROUP BY in Python |
| [Incremental Diff Detection](de_scenarios/incremental_diff_detection.md) | Finding new, changed and deleted records |

## Interview Tips

**What to say when you recognize this pattern:**
> "I see we're doing repeated lookups. A hash map would let me do each lookup in O(1), bringing the overall complexity from O(n²) down to O(n)."

**Common follow-ups:**
- "What if there are hash collisions?" → Rare in practice. Worst case is O(n) per operation, but Python's dict handles this well.
- "What if you can't use extra space?" → Usually means two pointers (if sorted) or you accept O(n²).
- "Hash map vs hash set?" → A set stores only keys. A map stores key-value pairs. Use a set when you only need membership checks.

## Related Patterns

- **[Two Pointers](../02_two_pointers/)** - When input is sorted, two pointers can replace hash map lookups with O(1) space. See [Two Sum](problems/001_two_sum.md) (hash map) vs [Two Sum II](../02_two_pointers/problems/167_two_sum_ii.md) (two pointers) for a direct comparison.
- **[Sliding Window](../04_sliding_window/)** - Often combined with a hash map for "window contains" problems.
- **Heap** (patterns/05_heap_priority_queue/) - When you need top-K after counting with a hash map.

## What's Next

**Next pattern:** [Two Pointers](../02_two_pointers/) - the natural complement to hash maps. When input is sorted, two pointers often achieve the same result with O(1) space instead of O(n).

**See also:**
- [Hash Map vs Nested Loop Benchmark](../../benchmarks/hash_map_vs_nested_loop.py) - watch O(n) vs O(n²) play out at scale (5,000x difference at 50K elements)
- [Pattern Recognition Cheat Sheet](../../docs/PATTERN_RECOGNITION.md) - quick reference for identifying which pattern fits
- [Time Complexity Reference](../../docs/TIME_COMPLEXITY_CHEATSHEET.md) - Big-O comparison card
