# CC Prompt: Rework Worked Examples - Pattern 02 Two Pointers (Problems 1-5)

## What This Prompt Does

Rewrites the `## Worked Example` section in problems 1-5. Run the README prompt first.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- Only modify `.md` files. REPLACE `## Worked Example` sections only.
- NO Oxford commas, NO em dashes, NO exclamation points

---

### 026_remove_duplicates.md

```markdown
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
```

### 088_merge_sorted.md

```markdown
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
```

### 283_move_zeroes.md

```markdown
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
```

### 167_two_sum_ii.md

```markdown
## Worked Example

With sorted input, start one pointer at the smallest value and one at the largest. Their sum tells us which pointer to move: too big means the right value is too large (move right left), too small means the left value is too small (move left right). Each step eliminates one position because sorted order guarantees the eliminated value can't be part of any valid pair.

```
Input: numbers = [2, 4, 5, 7, 9, 11, 14], target = 11

  left=0 (2), right=6 (14): 2+14=16 > 11
    Too big. Even the smallest left (2) makes 16 with 14.
    Every other left value would be bigger. Eliminate 14. Move right←.

  left=0 (2), right=5 (11): 2+11=13 > 11
    Still too big. Same logic. Eliminate 11. Move right←.

  left=0 (2), right=4 (9): 2+9=11 = target → found. Return [1, 5] (1-indexed).

  3 comparisons. Brute force: up to 21 pairs.
```
```

### 015_three_sum.md

```markdown
## Worked Example

Three Sum reduces to Two Sum. Sort the array, then for each element, use two pointers on the rest to find a pair summing to the negative of the fixed element. The sorting enables both the two-pointer search and duplicate skipping (identical values become adjacent).

```
Input: nums = [-3, -1, 0, 1, 2, -1, -4]
Sorted: [-4, -3, -1, -1, 0, 1, 2]

  i=0, fix=-4, need pair summing to 4:
    left=1(-3), right=6(2): -3+2=-1 < 4 → move left
    left=2(-1), right=6(2): -1+2=1 < 4 → move left
    ...eventually left >= right. No triplet with -4.

  i=1, fix=-3, need pair summing to 3:
    left=2(-1), right=6(2): -1+2=1 < 3 → move left
    left=3(-1), right=6(2): -1+2=1 < 3 → move left
    left=4(0), right=6(2):  0+2=2 < 3 → move left
    left=5(1), right=6(2):  1+2=3 = 3 → FOUND [-3, 1, 2]
      Skip duplicates. left=6 >= right → done with -3.

  i=2, fix=-1, need pair summing to 1:
    left=3(-1), right=6(2): -1+2=1 → FOUND [-1, -1, 2]
      Skip left to 4(0), right to 5(1).
    left=4(0), right=5(1): 0+1=1 → FOUND [-1, 0, 1]
      Done.

  i=3, fix=-1 = same as nums[2] → SKIP (duplicate)

  i=4, fix=0: left=5(1), right=6(2): 1+2=3 > 0 → no triplet.

  Result: [[-3, 1, 2], [-1, -1, 2], [-1, 0, 1]]

O(n²) total: sort O(n log n) + n outer iterations × O(n) inner scan.
```
```

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns
git diff --name-only | grep -v '.md$'
uv run pytest patterns/02_two_pointers/ -v --tb=short 2>&1 | tail -3

grep "Input:" patterns/02_two_pointers/problems/001_two_sum.md 2>/dev/null
grep "Input:" patterns/02_two_pointers/problems/167_two_sum_ii.md
```
