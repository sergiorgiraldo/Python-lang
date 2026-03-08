# Remove Duplicates from Sorted Array (LeetCode #26)

🔗 [LeetCode 26: Remove Duplicates from Sorted Array](https://leetcode.com/problems/remove-duplicates-from-sorted-array/)

> **Difficulty:** Easy | **Interview Frequency:** Occasional

## Problem Statement

Given a sorted array, remove duplicates **in place** so each element appears only once. Return the number of unique elements.

The first `k` elements of the array should contain the unique values. Elements beyond `k` don't matter.

**Example:**
```
Input: nums = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]
Output: 5, nums = [0, 1, 2, 3, 4, ...]
```

**Constraints:**
- 1 <= nums.length <= 3 * 10^4
- -100 <= nums[i] <= 100
- nums is sorted in non-decreasing order

---

## Thought Process

1. **In-place means O(1) extra space** - Can't create a new array.
2. **Sorted means duplicates are adjacent** - Don't need a hash set.
3. **Two pointers: read and write** - Read scans every element. Write tracks where the next unique value should go.
4. **When read finds something new, copy it to write position and advance write.**

---

## Worked Example

In a sorted array, all duplicates are adjacent. The read/write pointer technique exploits this: the "read" pointer scans forward through every element, the "write" pointer marks where the next unique value should go. When read finds a value different from what's at the write position, it copies it forward and write advances. Everything before write is the deduplicated result.

```
Input: nums = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]

  write=1 (index 0 always stays - first element is always unique)

  read=1: nums[1]=0, compare to nums[0]=0 → same value, skip
  read=2: nums[2]=1, compare to nums[0]=0 → different
           Copy: nums[1] = 1. write=2.   Array: [0, 1, 1, 1, 1, 2, 2, 3, 3, 4]
  read=3: nums[3]=1, compare to nums[1]=1 → same, skip
  read=4: nums[4]=1, compare to nums[1]=1 → same, skip
  read=5: nums[5]=2, compare to nums[1]=1 → different
           Copy: nums[2] = 2. write=3.
  read=6: same, skip
  read=7: nums[7]=3, compare to nums[2]=2 → different
           Copy: nums[3] = 3. write=4.
  read=8: same, skip
  read=9: nums[9]=4, compare to nums[3]=3 → different
           Copy: nums[4] = 4. write=5.

  Return write=5. First 5 elements: [0, 1, 2, 3, 4].

Read advanced 10 times. Write advanced 5 times. One pass, O(1) space.
```

---

## Approaches

### Approach 1: Read/Write Pointers

<details>
<summary>💡 Hint</summary>

You need two positions: one scanning ahead (read) and one tracking where to place the next unique value (write). When do you advance the write pointer?

</details>

<details>
<summary>📝 Explanation</summary>

Both pointers start near the beginning. Write begins at index 1 (index 0 is always kept). Read scans from index 1 forward.

At each step, compare what read sees to the last value written (at `write - 1`). If different, copy to write position and advance write. If same, skip.

Because the array is sorted, all copies of the same value are adjacent. Once read passes the last copy, write has already recorded one and we'll never see that value again.

**Time:** O(n) - read visits every element once.
**Space:** O(1) - two index variables. Modified in place.

This is the foundational "read/write pointer" pattern. Same structure appears in Move Zeroes, data compaction and any "remove X from sorted array in place" problem.

</details>

<details>
<summary>💻 Code</summary>

```python
def remove_duplicates(nums: list[int]) -> int:
    if not nums:
        return 0
    write = 1
    for read in range(1, len(nums)):
        if nums[read] != nums[write - 1]:
            nums[write] = nums[read]
            write += 1
    return write
```

</details>

---

## Edge Cases

| Case | Input | Expected | Why It Matters |
|------|-------|----------|----------------|
| Basic | `[1,1,2]` | `2` | Minimum duplicate case |
| Empty | `[]` | `0` | Boundary |
| Single | `[1]` | `1` | No comparisons needed |
| No duplicates | `[1,2,3,4,5]` | `5` | Write advances every step |
| All same | `[7,7,7,7]` | `1` | Write never moves past index 0 |
| Negatives | `[-3,-1,-1,0,0,2]` | `4` | Sign doesn't affect logic |

---

## Common Pitfalls

1. **Starting read at 0 instead of 1** - Index 0 is always kept; comparing `nums[0]` with `nums[-1]` is wrong
2. **Comparing against the previous read position instead of the last written value** - Compare `nums[read]` against `nums[write - 1]` (the last unique value written), not `nums[read - 1]`. For sorted input both produce the same result, but `write - 1` is the correct general pattern
3. **Returning write instead of the array** - The problem asks for the count, not the array

---

## Interview Tips

**What to say:**
> "Since the array is sorted, duplicates are always adjacent. I'll use two pointers - a read pointer scanning forward and a write pointer tracking where to place the next unique value."

**This is the simplest two-pointer problem.** If you're asked a two-pointer question and aren't sure where to start, this pattern (read/write for in-place modification) is a good mental model to fall back on.

**What the interviewer evaluates:** The in-place constraint tests whether you can work within memory limits. Proposing a new array first (then optimizing) shows good problem-solving process. Mentioning that this is how streaming DISTINCT works in databases shows engineering maturity.

---

## DE Application

In-place deduplication of sorted data is common when:
- Processing sorted log files and removing duplicate entries
- Compacting sorted partitions after a merge operation
- Cleaning sorted export files before loading into a warehouse

The sorted invariant is key. If data isn't sorted, you'd use a hash set instead (see [217. Contains Duplicate](../../01_hash_map/problems/217_contains_duplicate.md)).

---

## At Scale

In-place dedup with two pointers uses O(1) extra memory - the only approach that works when the array is too large to copy. For 10M elements, the scan takes ~50ms. For data that doesn't fit in memory, you need external sort followed by a streaming dedup pass: read sorted chunks sequentially, output only when the value changes. In SQL, this is `SELECT DISTINCT` on a sorted column or `ROW_NUMBER() PARTITION BY value ORDER BY value` to pick one representative per group. The two-pointer approach here is exactly what the database engine does internally during a streaming distinct operation.

---

## Related Problems

- [80. Remove Duplicates from Sorted Array II](https://leetcode.com/problems/remove-duplicates-from-sorted-array-ii/) - Allow up to 2 duplicates
- [283. Move Zeroes](283_move_zeroes.md) - Same read/write pattern, different criteria
- [27. Remove Element](https://leetcode.com/problems/remove-element/) - Remove specific value instead of duplicates
