# Move Zeroes (LeetCode #283)

🔗 [LeetCode 283: Move Zeroes](https://leetcode.com/problems/move-zeroes/)

> **Difficulty:** Easy | **Interview Frequency:** Occasional

## Problem Statement

Given an array, move all zeroes to the end while maintaining the relative order of non-zero elements. Do this in place.

**Example:**
```
Input: [0, 1, 0, 3, 12]
Output: [1, 3, 12, 0, 0]
```

**Constraints:**
- 1 <= nums.length <= 10^4
- -2^31 <= nums[i] <= 2^31 - 1

---

## Thought Process

1. **In-place, maintain order** - Can't just swap zeros to the end (would break order). Need a read/write approach.
2. **Same pattern as Remove Duplicates** - Write pointer tracks the next position for a non-zero. Read pointer scans everything.
3. **Two-phase approach** - First, move all non-zeroes to the front. Then fill the rest with zeros.
4. **Or swap approach** - Swap non-zero elements forward, which naturally pushes zeros toward the end.

---

## Worked Example

Same read/write pointer as Remove Duplicates, but skipping zeros instead of duplicates. Read scans everything. When it finds a non-zero, it writes it forward. After the scan, fill remaining positions with zeros.

```
Input: nums = [0, 3, 0, 1, 0, 5, 2, 0]

  write=0

  read=0: 0 → skip
  read=1: 3 → non-zero. nums[0]=3, write=1.   [3, 3, 0, 1, 0, 5, 2, 0]
  read=2: 0 → skip
  read=3: 1 → non-zero. nums[1]=1, write=2.   [3, 1, 0, 1, 0, 5, 2, 0]
  read=4: 0 → skip
  read=5: 5 → non-zero. nums[2]=5, write=3.   [3, 1, 5, 1, 0, 5, 2, 0]
  read=6: 2 → non-zero. nums[3]=2, write=4.   [3, 1, 5, 2, 0, 5, 2, 0]
  read=7: 0 → skip

  Fill: nums[4]=0, nums[5]=0, nums[6]=0, nums[7]=0
  Result: [3, 1, 5, 2, 0, 0, 0, 0]

Non-zero order preserved: 3, 1, 5, 2 appear in original relative order.
```

---

## Approaches

### Approach 1: Copy Then Zero-Fill

<details>
<summary>📝 Explanation</summary>

Two passes. First pass: read scans everything, write tracks where the next non-zero goes. When read finds a non-zero, copy it to write position and advance write. Zeros are skipped.

After the first pass, positions 0 to write-1 contain non-zeros in original order. Second pass fills positions write through n-1 with zeros.

**Time:** O(n) - two passes, each element touched at most twice.
**Space:** O(1) - in place.

Simpler logic than the swap approach. The "copy good stuff forward, clean up after" pattern.

</details>

<details>
<summary>💻 Code</summary>

```python
def move_zeroes(nums: list[int]) -> None:
    write = 0
    for read in range(len(nums)):
        if nums[read] != 0:
            nums[write] = nums[read]
            write += 1
    while write < len(nums):
        nums[write] = 0
        write += 1
```

</details>

---

### Approach 2: Swap-Based

<details>
<summary>📝 Explanation</summary>

Instead of a separate zero-fill pass, swap each non-zero directly with the write position. When read finds a non-zero, swap nums[read] with nums[write] and advance both.

The swap naturally moves zeros backward. Safe because everything at or after write is either a zero or a value read will reach later.

**Time:** O(n) - single pass.
**Space:** O(1) - in place.

Common interview follow-up: "can you do it in one pass?" Both approaches are O(n). The difference is stylistic.

</details>

<details>
<summary>💻 Code</summary>

```python
def move_zeroes_swap(nums: list[int]) -> None:
    write = 0
    for read in range(len(nums)):
        if nums[read] != 0:
            nums[write], nums[read] = nums[read], nums[write]
            write += 1
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Basic | `[0,1,0,3,12]` | `[1,3,12,0,0]` | Standard case |
| No zeroes | `[1,2,3]` | `[1,2,3]` | Nothing to move |
| All zeroes | `[0,0,0]` | `[0,0,0]` | Write never advances |
| Already correct | `[1,2,0,0]` | `[1,2,0,0]` | No work needed |
| Single element | `[0]` / `[1]` | `[0]` / `[1]` | Boundary |

---

## Common Pitfalls

1. **Breaking relative order** - If you swap zeros directly to the end without maintaining order, you'll scramble the non-zero elements
2. **Off-by-one in zero filling** - The zero-fill phase starts at the write pointer's final position, not at the end

---

## Interview Tips

**What to say:**
> "This is the same read/write pointer pattern as Remove Duplicates. The write pointer marks where the next non-zero goes. After moving all non-zeroes forward, I fill the rest with zeros."

This problem is often a warm-up. Solve it quickly and cleanly to build momentum for harder follow-ups.

**What the interviewer evaluates:** This tests in-place array manipulation with stability (preserving relative order). The two-pointer swap approach is clean but easy to get wrong with off-by-one errors. Walking through an example carefully before coding shows discipline.

---

## DE Application

This is a data compaction pattern. In data engineering:
- Removing null rows from a dataset before processing
- Compacting sparse arrays (moving valid data to the front)
- Filtering out sentinel values from data streams
- Partition compaction in storage engines (removing tombstoned records)

---

## At Scale

In-place partitioning uses O(1) memory. The two-pointer approach makes a single pass, so it's I/O-optimal: each element is read once and written at most once. At 1B elements, the bottleneck is memory bandwidth, not computation. The partition operation is the building block of quicksort and quickselect. In data pipelines, this pattern appears as "filter and compact": remove null/invalid records from a dataset while preserving order of valid records. Spark's `df.filter(col("value") != 0)` does this logically but materializes a new DataFrame rather than modifying in-place.

---

## Related Problems

- [26. Remove Duplicates](026_remove_duplicates.md) - Same read/write pointer pattern
- [27. Remove Element](https://leetcode.com/problems/remove-element/) - Remove specific value (generalization)
- [75. Sort Colors](075_sort_colors.md) - Three-way partition (harder version of this concept)
