# Time Based Key-Value Store (LeetCode #981)

🔗 [LeetCode 981: Time Based Key-Value Store](https://leetcode.com/problems/time-based-key-value-store/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

## Problem Statement

Design a time-based key-value data structure that stores multiple values for the same key at different timestamps and retrieves the value at a certain timestamp.

Implement:
- `set(key, value, timestamp)` - Store the key-value pair at the given timestamp.
- `get(key, timestamp)` - Return the value with the largest timestamp that is <= the given timestamp. Return empty string if no such value.

All `set` timestamps for a given key are strictly increasing.

**Example:**
```
set("foo", "bar", 1)
set("foo", "bar2", 4)
get("foo", 1)  → "bar"
get("foo", 3)  → "bar"    (latest value at or before time 3)
get("foo", 4)  → "bar2"
get("foo", 5)  → "bar2"
```

---

## Thought Process

1. **Storage:** Each key maps to a list of (timestamp, value) pairs. Since timestamps are strictly increasing, the list stays sorted without extra work.
2. **Set:** Just append to the list. O(1).
3. **Get:** Find the latest timestamp that's <= the query timestamp. That's a right-boundary binary search on the timestamps list.
4. **Two implementation options:** Use Python's `bisect` module (production-grade) or implement the binary search manually (demonstrates understanding).

---

## Worked Example

TimeMap stores key-value pairs with timestamps and retrieves the value at the largest timestamp <= the query timestamp. This is a boundary-finding binary search: for a given key, find the rightmost timestamp that doesn't exceed the query.

The data structure uses a dict mapping each key to a list of (timestamp, value) pairs. Since timestamps for the same key are set in increasing order (per the problem guarantee), the list is already sorted. Binary search finds the right entry without scanning the full history.

```
TimeMap()

set("weather", "sunny",  1)
set("weather", "cloudy", 4)
set("weather", "rainy",  7)
set("weather", "sunny",  12)

Internal state:
  data["weather"] = [(1, "sunny"), (4, "cloudy"), (7, "rainy"), (12, "sunny")]

get("weather", timestamp=5):
  Binary search for rightmost timestamp <= 5 in [1, 4, 7, 12]:
    left=0, right=3, mid=1 → timestamp 4 <= 5 → candidate. Go right: left=2.
    left=2, right=3, mid=2 → timestamp 7 > 5 → too late. right=1.
    left=2 > right=1 → done. Best candidate was index 1.
  Return "cloudy" (the value at timestamp 4, the latest timestamp <= 5).

get("weather", timestamp=7):
  Binary search for rightmost timestamp <= 7:
    left=0, right=3, mid=1 → 4 <= 7 → left=2.
    left=2, right=3, mid=2 → 7 <= 7 → exact match. left=3.
    left=3, right=3, mid=3 → 12 > 7 → right=2.
    left=3 > right=2. Best candidate was index 2.
  Return "rainy" (exact match at timestamp 7).

get("weather", timestamp=0):
  Binary search: all timestamps > 0. No valid candidate. Return "".

Each get is O(log m) where m is the number of entries for that key,
vs O(m) for a linear scan through the history.
```

---

## Approaches

### Approach 1: Using bisect (Production)

<details>
<summary>📝 Explanation</summary>

Store each key's history as a sorted list of (timestamp, value) pairs. For get operations, use `bisect_right` to find where the query timestamp would be inserted, then return the entry just before that insertion point (which is the latest timestamp <= query).

```python
import bisect
idx = bisect.bisect_right(timestamps, query_ts)
if idx == 0:
    return ""  # all timestamps are after the query
return values[idx - 1]
```

`bisect_right` returns the insertion point that keeps the list sorted. If it returns index `i`, all elements before `i` have timestamps <= query. So `i - 1` is the one we want.

**Time:** O(1) for set (append to list), O(log m) for get (binary search on m entries for that key).
**Space:** O(total entries across all keys).

This is the production approach. The bisect module is well-tested and handles edge cases correctly.

</details>

<details>
<summary>💻 Code</summary>

```python
import bisect
from collections import defaultdict

class TimeMap:
    def __init__(self):
        self.store = defaultdict(list)

    def set(self, key: str, value: str, timestamp: int) -> None:
        self.store[key].append((timestamp, value))

    def get(self, key: str, timestamp: int) -> str:
        entries = self.store[key]
        if not entries:
            return ""
        idx = bisect.bisect_right(entries, (timestamp, chr(127)))
        if idx == 0:
            return ""
        return entries[idx - 1][1]
```

</details>

### Approach 2: Manual Binary Search (Interview)

<details>
<summary>📝 Explanation</summary>

Same logic as above but implementing the binary search by hand. This is what interviewers typically want to see.

Maintain a dict of key → list of (timestamp, value). For get, binary search the list for the rightmost timestamp <= query:

1. `left = 0`, `right = len(entries) - 1`.
2. Track `result = ""` (best answer so far).
3. While `left <= right`:
   - If `entries[mid].timestamp <= query_ts`: this is a valid candidate. Update `result` and search right for a later valid timestamp: `left = mid + 1`.
   - If `entries[mid].timestamp > query_ts`: too late. Go left: `right = mid - 1`.
4. Return result.

The "track best so far" pattern is common in binary search boundary problems. We don't stop at the first valid answer - we keep searching for a better (later) one.

**Time:** O(1) for set, O(log m) for get.
**Space:** O(total entries).

</details>

<details>
<summary>💻 Code</summary>

```python
from collections import defaultdict

class TimeMapManual:
    def __init__(self):
        self.store = defaultdict(list)

    def set(self, key: str, value: str, timestamp: int) -> None:
        self.store[key].append((timestamp, value))

    def get(self, key: str, timestamp: int) -> str:
        entries = self.store[key]
        if not entries:
            return ""
        left, right = 0, len(entries) - 1
        result = ""
        while left <= right:
            mid = (left + right) // 2
            if entries[mid][0] <= timestamp:
                result = entries[mid][1]
                left = mid + 1
            else:
                right = mid - 1
        return result
```

</details>

---

## Edge Cases

| Case | Operation | Expected | Why It Matters |
|------|-----------|----------|----------------|
| Exact match | `get("foo", 1)` after set at 1 | `"bar"` | Direct hit |
| Between timestamps | `get("foo", 3)` with entries at 1,4 | `"bar"` | Latest before query |
| After all | `get("foo", 5)` with entries at 1,4 | `"bar2"` | Latest overall |
| Before all | `get("foo", 0)` with entry at 1 | `""` | Nothing valid |
| Missing key | `get("missing", 1)` | `""` | Key never set |
| Many entries | 100 entries, query in middle | Correct value | Performance at scale |

---

## Common Pitfalls

1. **Not handling the "before all timestamps" case** - When `bisect_right` returns 0 or the manual search finds no valid candidate, return empty string.
2. **Using bisect_left instead of bisect_right** - `bisect_left` finds the first entry >= timestamp. We want the last entry <= timestamp, so we need `bisect_right` and then go back one step.
3. **Assuming timestamps can repeat** - The problem says timestamps are strictly increasing per key, so appending maintains sort order. If they could repeat, you'd need to handle duplicates.

---

## Interview Tips

**What to say:**
> "Since timestamps are strictly increasing per key, I can store entries in a list and get O(1) appends. For get, I need the latest timestamp at or before the query, which is a binary search. I'll use bisect_right and go back one index."

**bisect vs manual:**
> "In production I'd use Python's bisect module - it's C-implemented and well-tested. For the interview, I can implement the binary search manually if you'd prefer to see the logic."

**Design follow-ups interviewers might ask:**
- "What if timestamps aren't strictly increasing?" - Need insertion into sorted position, not just append. Changes set to O(log n).
- "What about thread safety?" - Reads are safe for concurrent access on immutable data. Writes need locking or copy-on-write.
- "What about memory?" - If key has millions of entries, consider TTL-based cleanup or a more compact storage format.

**What the interviewer evaluates:** This is a design + algorithm hybrid. The data structure choice (dict of sorted lists) tests design sense. The binary search within each key's history tests implementation. The follow-up "what about concurrent writes?" or "what about TTL/expiration?" pivots to system design. Mentioning time-travel queries in Delta Lake or Iceberg connects to production systems.

---

## DE Application

This is one of the most directly applicable binary search problems for data engineering:
- **Point-in-time lookups** in SCD Type 2 tables: "What was this customer's address on this date?"
- **Temporal joins**: match fact table events to the correct dimension record version
- **Event sourcing**: find the state of an entity at a given time by searching its event history
- **Versioned config**: "What was the pipeline's config when this batch ran?"

Every time you write a query with `WHERE effective_date <= @query_date ORDER BY effective_date DESC LIMIT 1`, you're doing the same operation this data structure does.

See: [Time-Based Log Lookup (DE Scenario)](../de_scenarios/log_lookup.md)

---

## At Scale

A time-based key-value store is essentially a sorted map per key: given a key and a timestamp, find the most recent value at or before that timestamp. This is binary search on the timestamp list per key. At scale, this is how time-travel queries work in data lakehouses (Delta Lake, Iceberg): each key has a version history sorted by timestamp. A query at timestamp T binary-searches the version list to find the active version. For 1B versions across all keys, the per-key binary search is fast (log of versions per key, typically small), but the key lookup itself needs a hash map or index.

---

## Related Problems

- [35. Search Insert Position](035_search_insert.md) - Same boundary search concept
- [704. Binary Search](704_binary_search.md) - Foundation
- [146. LRU Cache](../../01_hash_map/problems/146_lru_cache.md) - Another design problem combining data structures
