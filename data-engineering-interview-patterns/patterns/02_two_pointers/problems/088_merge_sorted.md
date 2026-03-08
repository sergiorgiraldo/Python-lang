# Merge Sorted Array (LeetCode #88)

🔗 [LeetCode 88: Merge Sorted Array](https://leetcode.com/problems/merge-sorted-array/)

> **Difficulty:** Easy | **Interview Frequency:** Very Common

## Problem Statement

Given two sorted arrays `nums1` and `nums2`, merge `nums2` into `nums1` in place. `nums1` has enough space at the end (filled with zeros) to hold all elements.

**Example:**
```
Input: nums1 = [1,2,3,0,0,0], m = 3, nums2 = [2,5,6], n = 3
Output: [1,2,2,3,5,6]
```

**Constraints:**
- nums1.length == m + n
- nums2.length == n
- 0 <= m, n <= 200

---

## Thought Process

1. **Merging forward would overwrite elements** - If we start from the front of nums1 and place merged elements there, we'd overwrite elements we haven't processed yet.
2. **Merge from the back** - The empty space is at the end of nums1. Start there. Compare the largest unprocessed elements from both arrays and place the larger one at the end.
3. **When one array is exhausted** - If nums2 has remaining elements, copy them. If nums1 has remaining elements, they're already in the right place.

---

## Worked Example

When merging two sorted arrays, nums1 has extra space at the END. If we write from the front, we'd overwrite values we haven't processed. The fix: merge from the back. Start pointers at the end of each real section and a write pointer at the very end. Compare, write the larger value, move backward.

```
Input: nums1 = [1, 3, 5, 7, 0, 0, 0, 0], m=4
       nums2 = [2, 4, 6, 8],              n=4

  p1=3 (value 7), p2=3 (value 8), write=7

  7 vs 8: 8 wins → nums1[7]=8, p2=2, write=6.   [..., 0, 0, 0, 8]
  7 vs 6: 7 wins → nums1[6]=7, p1=2, write=5.   [..., 0, 0, 7, 8]
  5 vs 6: 6 wins → nums1[5]=6, p2=1, write=4.   [..., 0, 6, 7, 8]
  5 vs 4: 5 wins → nums1[4]=5, p1=1, write=3.   [..., 5, 6, 7, 8]
  3 vs 4: 4 wins → nums1[3]=4, p2=0, write=2.   [...4, 5, 6, 7, 8]
  3 vs 2: 3 wins → nums1[2]=3, p1=0, write=1.   [1, 3, 3, 4, 5, 6, 7, 8]
  1 vs 2: 2 wins → nums1[1]=2, p2=-1, write=0.  [1, 2, 3, 4, 5, 6, 7, 8]

  p2 exhausted. nums1[0]=1 already in place.
  Result: [1, 2, 3, 4, 5, 6, 7, 8]

The write pointer is always ahead of the read pointers, so we
never overwrite values we haven't processed.
```

---

## Approaches

### Approach 1: Merge from the Back (In Place)

<details>
<summary>💡 Hint</summary>

Where is the empty space in nums1? Can you fill from there to avoid overwriting?

</details>

<details>
<summary>📝 Explanation</summary>

Three pointers: `p1` at the last real element of nums1 (m-1), `p2` at the last of nums2 (n-1), `write` at the very end (m+n-1).

At each step, compare nums1[p1] and nums2[p2]. Write the larger value at nums1[write]. Decrement the pointer that was used and decrement write.

If p1 runs out first, copy remaining nums2 elements. If p2 runs out first, remaining nums1 elements are already in place.

**Time:** O(n + m) - each element processed exactly once.
**Space:** O(1) - merging into existing space in nums1.

Edge case: if p2 runs out but p1 hasn't, we're done. Those nums1 elements were already at the front and nothing shifted them.

</details>

<details>
<summary>💻 Code</summary>

```python
def merge_sorted_array(nums1: list[int], m: int, nums2: list[int], n: int) -> None:
    p1 = m - 1
    p2 = n - 1
    write = m + n - 1

    while p2 >= 0:
        if p1 >= 0 and nums1[p1] > nums2[p2]:
            nums1[write] = nums1[p1]
            p1 -= 1
        else:
            nums1[write] = nums2[p2]
            p2 -= 1
        write -= 1
```

</details>

---

## Edge Cases

| Case | nums1 (m) | nums2 (n) | Result | Why It Matters |
|------|-----------|-----------|--------|----------------|
| Interleaved | `[1,3,5,0,0,0]` (3) | `[2,4,6]` (3) | `[1,2,3,4,5,6]` | Alternating sources |
| nums2 all smaller | `[4,5,6,0,0,0]` (3) | `[1,2,3]` (3) | `[1,2,3,4,5,6]` | All of nums2 goes first |
| nums2 empty | `[1]` (1) | `[]` (0) | `[1]` | Nothing to merge |
| nums1 empty | `[0]` (0) | `[1]` (1) | `[1]` | Just copy nums2 |
| Duplicates | `[1,2,2,0,0]` (3) | `[2,3]` (2) | `[1,2,2,2,3]` | Stability matters |

---

## Common Pitfalls

1. **Merging from the front** - Overwrites unprocessed elements in nums1. Always merge from the back for in-place.
2. **Forgetting to copy remaining nums2 elements** - When p1 is exhausted but p2 still has elements, they need to be copied. (Remaining nums1 elements are already in place.)
3. **Off-by-one on the write pointer** - Initialize at `m + n - 1`, not `m + n`.

---

## Interview Tips

**What to say:**
> "Merging from the front would overwrite values I haven't processed. But nums1 has empty space at the end, so I can fill from the back - comparing the largest remaining elements and working backward."

**The "merge from the back" insight is the whole problem.** Once you see it, the implementation is mechanical. Mention this insight early to show you understand the key challenge.

**What the interviewer evaluates:** The backwards-merge insight tests spatial reasoning. Starting from the end avoids extra memory allocation. Mentioning sort-merge joins or external merge sort connects the algorithm to production systems - a strong principal-level signal.

---

## DE Application

Merging sorted sequences is fundamental to data engineering:
- External sort merge phase (merge sorted runs from disk)
- Combining sorted partition files into a single output
- Merge step in sort-merge joins
- Compaction in LSM-tree storage engines (RocksDB, LevelDB)

The two-array version is a building block. The K-sorted-streams version (using a heap) generalizes this to merge many sources. See [23. Merge K Sorted Lists](https://leetcode.com/problems/merge-k-sorted-lists/).

---

## At Scale

Merging two sorted arrays is the core operation in merge sort and sort-merge joins. The backwards merge (from end to start) avoids extra memory - critical when arrays are large. For two sorted files of 10GB each, you'd stream both files sequentially and write the merged output. This is exactly how external merge sort works: merge sorted runs from disk. In Spark, sort-merge join sorts both sides by key, then merges with a two-pointer scan. The O(1) extra memory property makes this the preferred join strategy for large datasets where neither side fits in memory for a hash join.

---

## Related Problems

- [21. Merge Two Sorted Lists](https://leetcode.com/problems/merge-two-sorted-lists/) - Linked list version
- [23. Merge K Sorted Lists](https://leetcode.com/problems/merge-k-sorted-lists/) - Generalization with heap
- [977. Squares of a Sorted Array](977_squares_sorted.md) - Opposite-ends merge variant
