# Binary Search Pattern

## What Is It?

### The basics

Binary search is a way to find something in sorted data by cutting the search space in half with every step. Instead of checking every element from the start (O(n)), binary search checks the middle element, decides which half the answer must be in, throws away the other half and repeats. Each step halves the remaining data, so finding a value in a million-element array takes at most 20 checks (log₂ of 1,000,000 ≈ 20).

You already use binary search intuitively. When looking up a word in a physical dictionary, you don't start at page 1. You flip to roughly the middle, see if your word comes before or after the current page, then flip to the middle of the remaining section. Each flip eliminates half the dictionary.

### How it works step by step

```python
def binary_search(arr, target):
    left = 0
    right = len(arr) - 1

    while left <= right:
        mid = (left + right) // 2

        if arr[mid] == target:
            return mid          # found it
        elif arr[mid] < target:
            left = mid + 1      # target is in the right half
        else:
            right = mid - 1     # target is in the left half

    return -1  # not found
```

Three variables: `left` (start of search range), `right` (end of search range), `mid` (middle of current range). At each step:

1. Compute `mid = (left + right) // 2`
2. Compare `arr[mid]` to the target
3. If equal, done. If target is larger, search the right half (`left = mid + 1`). If smaller, search the left half (`right = mid - 1`).
4. Repeat until `left > right` (search space is empty, target not found).

Each step throws away half the remaining elements. That's what gives binary search its O(log n) time.

### What O(log n) means in practice

O(log n) grows incredibly slowly. Here's the comparison with O(n):

| Array size | O(n) steps | O(log n) steps |
|---|---|---|
| 100 | 100 | 7 |
| 10,000 | 10,000 | 14 |
| 1,000,000 | 1,000,000 | 20 |
| 1,000,000,000 | 1 billion | 30 |

A billion elements in 30 steps. That's the power of halving.

If you've used SQL, `O(log n)` is what happens when you query an indexed column. The B-tree index (despite its name, it's a different structure than binary search) uses a similar divide-and-conquer principle to find rows without scanning the full table.

### The one requirement: sorted data

Binary search only works when the data is sorted (or has some monotonic property where you can consistently decide "go left" or "go right"). If the data isn't sorted, binary search can't know which half to eliminate.

This means the first question to ask yourself is: "Is this data sorted, or can I sort it without breaking the problem?" If yes, binary search might apply. If no, you need a different approach (hash map, two pointers, etc.).

### The three types of binary search problems

**1. Exact match** - Find a specific value in a sorted array.
This is the classic case. "Is 42 in this array? If so, where?"
Problems: Binary Search (704), Search in Rotated Sorted Array (33).

**2. Boundary finding** - Find where a condition changes from false to true (or vice versa).
Instead of looking for an exact value, you're looking for a boundary. "What's the first element >= 5?" or "What's the leftmost position where this predicate becomes true?"
Problems: Search Insert Position (35), Find Minimum in Rotated Sorted Array (153), Find Peak Element (162).

**3. Binary search on the answer** - The answer itself is a number in some range, and you binary search for it.
Instead of searching an array, you're searching a range of possible answers. For each candidate answer, you check if it works (usually with a helper function). "What's the minimum speed to finish in time?" or "What's the maximum value that satisfies this constraint?"
Problems: Koko Eating Bananas (875).

Type 3 is the trickiest to recognize because there's no explicit sorted array. The "sorted" property is implicit: if speed X works, then any speed > X also works. That monotonic property is what makes binary search applicable.

### Common bugs

Binary search is conceptually simple but notoriously tricky to implement correctly. The most common bugs:

**Off-by-one in loop condition:** `while left <= right` vs `while left < right`. The first includes the case where left == right (one element to check). The second stops before checking the last element. Use `<=` for exact match, `<` for boundary finding (where left converges to the answer).

**Off-by-one in mid updates:** `left = mid + 1` and `right = mid - 1` for exact match. For boundary finding, one side uses `mid` (not `mid ± 1`) to keep the boundary candidate in the range. Getting this wrong causes infinite loops.

**Integer overflow in mid calculation:** `(left + right) // 2` can overflow in languages with fixed-size integers (not a problem in Python, but important in Java/C++). The safe version is `left + (right - left) // 2`.

### Python's bisect module

Python provides the `bisect` module for binary search:

```python
import bisect

arr = [1, 3, 5, 7, 9, 11]
bisect.bisect_left(arr, 5)   # → 2 (leftmost position where 5 could be inserted)
bisect.bisect_right(arr, 5)  # → 3 (rightmost position where 5 could be inserted)
bisect.insort(arr, 6)        # inserts 6 in sorted position → [1, 3, 5, 6, 7, 9, 11]
```

`bisect_left` and `bisect_right` are boundary-finding binary searches. They return insertion points, not just "found/not found." This is useful for finding ranges, counting elements and answering "where does this value fit?"

In an interview, it's fine to mention bisect and use it in production code. But be prepared to implement binary search from scratch - interviewers usually want to see that you understand the mechanics.

### Connection to data engineering

Binary search patterns appear in DE work:
- **Partition boundary detection** - finding where to split sorted data into date/value ranges
- **Log lookup by timestamp** - finding the first log entry after a specific time in a sorted log file
- **Search on answer** - "what's the minimum number of partitions to keep each under 1GB?" or "what's the optimal batch size?"
- **Change point detection** - finding where a metric shifted using bisection on sorted time-series data

## When to Use It

**Recognition signals:**
- "Find X in sorted data"
- "Find the minimum/maximum that satisfies a condition"
- "Find where a property changes"
- "Search in a rotated sorted array"
- "Minimize the maximum" or "maximize the minimum" (binary search on answer)
- Input is sorted or has a monotonic property

**Not just sorted arrays.** Binary search works on any space where you can determine which half to eliminate. This includes:
- Sorted arrays (classic)
- Rotated sorted arrays (modified comparison)
- Answer spaces ("what's the minimum speed to finish in time?")
- 2D matrices (treat as flattened sorted array)
- Time-based data (find when something changed)

## Visual Aid

```
Target: 34 in sorted array [1, 2, 3, 4, ..., 1000]

Step 1: Search range [1 - 1000], mid index 500 → value 500
        500 > 34, too high → eliminate upper half [501-1000]

Step 2: Search range [1 - 499], mid index 250 → value 250
        250 > 34 → eliminate [251-499]

Step 3: Search range [1 - 249], mid index 125 → value 125
        125 > 34 → eliminate [126-249]

Step 4: Search range [1 - 124], mid index 62 → value 62
        62 > 34 → eliminate [63-124]

Step 5: Search range [1 - 61], mid index 31 → value 31
        31 < 34 → eliminate [1-31]

Step 6: Search range [32 - 61], mid index 46 → value 46
        46 > 34 → eliminate [47-61]

Step 7: Search range [32 - 45], mid index 38 → value 38
        38 > 34 → eliminate [39-45]

Step 8: Search range [32 - 37], mid index 34 → value 34
        34 == 34 → FOUND at index 33 (0-indexed)

Found the target in 8 steps out of 1000 elements.
log₂(1000) ≈ 10, so 8 steps is right in the expected range.
Linear search would have taken 34 steps to reach this element.
```

## Three Variants You Need to Know

Binary search has three core variants. Every binary search problem is one of these or a combination:

### 1. Exact Match
Find the index of a specific target. Return -1 if not found.
```python
while left <= right:
    mid = (left + right) // 2
    if arr[mid] == target: return mid
    elif arr[mid] < target: left = mid + 1
    else: right = mid - 1
```

### 2. Left Boundary (Lower Bound)
Find the first position where `arr[i] >= target`. Used for "find the leftmost" or "find insertion point."
```python
while left < right:
    mid = (left + right) // 2
    if arr[mid] < target: left = mid + 1
    else: right = mid
# left == right == insertion point
```

### 3. Binary Search on Answer
The search space isn't an array - it's a range of possible answers. For each candidate answer, check if it's feasible. Find the minimum (or maximum) feasible answer.
```python
while left < right:
    mid = (left + right) // 2
    if is_feasible(mid): right = mid      # mid works, try smaller
    else: left = mid + 1                   # mid doesn't work, need bigger
```

## The Off-by-One Problem

Binary search bugs almost always come from boundary conditions. The three variants above use different loop conditions and update rules for a reason:

| Variant | Loop condition | When target found | Left update | Right update |
|---------|---------------|-------------------|-------------|--------------|
| Exact match | `left <= right` | Return immediately | `mid + 1` | `mid - 1` |
| Left boundary | `left < right` | Don't return, narrow right | `mid + 1` | `mid` |
| Search on answer | `left < right` | Don't return, narrow right | `mid + 1` | `mid` |

**The rule:** If you're looking for an exact value and returning immediately, use `<=` and move both bounds past mid. If you're looking for a boundary and converging, use `<` and set one bound to mid (not mid ± 1).

Getting this wrong is the most common binary search bug. When in doubt, trace through a 2-element array to verify your bounds converge correctly.

## Time/Space Complexity

| Operation | Time | Space |
|-----------|------|-------|
| Standard binary search | O(log n) | O(1) |
| Binary search on 2D matrix | O(log(m*n)) | O(1) |
| Binary search on answer | O(log(range) * check_cost) | O(1) |
| Exponential search (unknown bounds) | O(log n) | O(1) |

For context: log₂(1,000,000) ≈ 20. Binary search on a million elements takes about 20 comparisons.

## Trade-offs

**The core trade-off: O(log n) time but requires sorted/monotonic data.** If the data isn't sorted, you either sort it first (O(n log n) upfront cost) or use a different approach entirely.

**Binary search vs hash map:**
- Hash map: O(1) lookup but O(n) space and only does exact match
- Binary search: O(log n) lookup, O(1) extra space, and can find boundaries/ranges

**Binary search vs linear scan:**
- For a single search in sorted data: binary search (O(log n)) always wins
- For multiple searches in unsorted data: sort once (O(n log n)) then binary search each query (O(log n) each) vs. building a hash map once (O(n)) then O(1) each query. The hash map wins if you're only doing exact matches.

**When binary search is the only option:**
- "Binary search on the answer" problems have no array to hash. The search space is a conceptual range (e.g., speeds from 1 to max). Binary search is the natural fit.
- Finding boundaries or insertion points. Hash maps don't support "find the first element >= X."

### Scale characteristics

Binary search eliminates half the data with each comparison. The number of comparisons is log2(n):

| n | Comparisons | Time at 100ns/comparison |
|---|---|---|
| 1K | 10 | 1 microsecond |
| 1M | [20](https://leetcode.com/problems/valid-parentheses/) | 2 microseconds |
| 1B | 30 | 3 microseconds |
| 1T | 40 | 4 microseconds |

This is why binary search is the foundation of database indexing. A B-tree index on 1 trillion rows requires ~40 comparisons per lookup. The practical bottleneck at scale isn't the comparisons - it's disk I/O. Each comparison may require reading a disk page. B-trees optimize for this by having high fan-out (hundreds of keys per node), reducing tree depth to 3-4 levels even for billions of rows.

**Distributed equivalent:** Binary search on partitioned data requires knowing which partition contains the target range. Range-partitioned tables (common in BigQuery, Snowflake, Cassandra) store partition boundaries as metadata. A query first binary-searches the partition metadata to identify the relevant partition, then binary-searches within it. This is a two-level search: O(log P + log N/P) where P is partitions.

**"Binary search the answer" at scale:** Problems like Koko Eating Bananas binary-search over the solution space rather than the data. This pattern appears in distributed systems as capacity planning: "what's the minimum number of workers to process this data in under 1 hour?" Binary search the worker count, simulate the workload for each candidate count.

### SQL equivalent

Binary search maps to index lookups in SQL. A `WHERE id = 42` on an indexed column triggers a B-tree traversal (binary search variant). Range queries like `WHERE created_at BETWEEN '2024-01-01' AND '2024-01-31'` use the index to find the start point, then scan sequentially. Understanding when the optimizer chooses an index scan vs a full table scan is essential for query performance. The SQL section's optimization subsection covers index selection and query plans.

## Problems

| # | Problem | Difficulty | Key Concept |
|---|---------|------------|-------------|
| [704](https://leetcode.com/problems/binary-search/) | [Binary Search](problems/704_binary_search.md) | Easy | Exact match (foundation) |
| [35](https://leetcode.com/problems/search-insert-position/) | [Search Insert Position](problems/035_search_insert.md) | Easy | Left boundary / insertion point |
| [74](https://leetcode.com/problems/search-a-2d-matrix/) | [Search a 2D Matrix](problems/074_search_2d_matrix.md) | Medium | Treat 2D as sorted 1D |
| [153](https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/) | [Find Min in Rotated Sorted Array](problems/153_find_min_rotated.md) | Medium | Modified binary search |
| [33](https://leetcode.com/problems/search-in-rotated-sorted-array/) | [Search in Rotated Sorted Array](problems/033_search_rotated.md) | Medium | Determine sorted half |
| [162](https://leetcode.com/problems/find-peak-element/) | [Find Peak Element](problems/162_find_peak.md) | Medium | Binary search on unsorted data |
| [875](https://leetcode.com/problems/koko-eating-bananas/) | [Koko Eating Bananas](problems/875_koko_bananas.md) | Medium | Binary search on answer |
| [981](https://leetcode.com/problems/time-based-key-value-store/) | [Time Based Key-Value Store](problems/981_time_map.md) | Medium | Binary search in design |

**Suggested order:** 704, 35 → 74 → 153, 33 → 162 → 875 → 981

## DE Scenarios

| Scenario | Description | Connection |
|----------|-------------|------------|
| [Finding Partition Boundaries](de_scenarios/partition_boundaries.md) | Determine split points for backfill ranges | Left boundary variant |
| [Time-Based Log Lookup](de_scenarios/log_lookup.md) | Find events at or near a timestamp in sorted logs | Left boundary + bisect |
| [Binary Search on Answer](de_scenarios/search_on_answer.md) | Resource allocation (find min workers/partitions) | Search on answer variant |
| [Metric Change Detection](de_scenarios/metric_change_detection.md) | Find when a metric crossed a threshold | Left boundary variant |

## Interview Tips

**What to say when you see sorted data:**
> "The input is sorted, so I can use binary search to bring this from O(n) down to O(log n)."

**When you're not sure which variant:**
> "Let me think about whether I need the exact position or just a boundary. If I need the first element that satisfies a condition, I'll use the left-boundary variant."

**On the off-by-one problem:**
> "Binary search boundary conditions are tricky, so let me trace through a small example to verify my bounds converge."

Most interviewers respect you acknowledging that binary search edge cases are subtle. Tracing through a 2-3 element example to verify your loop is correct shows discipline, not weakness.

## Related Patterns

- **[Two Pointers](../02_two_pointers/)** - Both work on sorted data. Two pointers scan for pairs in O(n); binary search finds single elements in O(log n). Compare [Two Sum II](../02_two_pointers/problems/167_two_sum_ii.md) (two pointers) with binary search for complement (O(n log n) - usually worse).
- **[Hash Map](../01_hash_map/)** - For unsorted data, hash maps give O(1) lookup. For sorted data, binary search gives O(log n) lookup with O(1) space instead of O(n) space.
- **Heap** (patterns/05_heap_priority_queue/) - Heaps maintain partial order. Binary search needs full order but is faster for single lookups.

## What's Next

**Next pattern:** [Sliding Window](../04_sliding_window/) - another pattern for sequential data, focused on subarrays and substrings rather than search.

**See also:**
- [Binary Search vs Linear Scan Benchmark](../../benchmarks/binary_search_vs_linear.py) - watch O(log n) vs O(n) at scale
- [Pattern Recognition Cheat Sheet](../../docs/PATTERN_RECOGNITION.md) - quick reference for identifying which pattern fits
- [Time Complexity Reference](../../docs/TIME_COMPLEXITY_CHEATSHEET.md) - Big-O comparison card
