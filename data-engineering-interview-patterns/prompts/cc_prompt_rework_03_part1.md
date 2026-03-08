# CC Prompt: Full Rework - Pattern 03 Binary Search (Part 1 of 2)

## What This Prompt Does

Rewrites the README "What Is It?", "Visual Aid" and "Trade-offs" sections, plus all `## Worked Example` sections and `📝 Explanation` blocks for the first 4 problems.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- Only modify `.md` files. Do NOT touch `.py` or `_test.py` files.
- REPLACE the specified sections only. Do not modify other sections.
- NO Oxford commas, NO em dashes, NO exclamation points
- Avoid: "straightforward", "robust", "leverage", "utilize", "comprehensive", "powerful", "fascinating", "game-changer"

---

## Task 1: Rewrite README Sections

### Replace `## What Is It?` (everything up to `## When to Use It`)

```markdown
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

### What O(log n) actually means

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
```

### Replace `## Visual Aid` (up to `## Template`)

Keep the existing Visual Aid if it already shows the 1-1000 search trace approved. If it uses a smaller example, replace with:

```markdown
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
```

### Replace `## Trade-offs` (up to `## Problems in This Section`)

```markdown
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
```

---

## Task 2: Worked Examples + Approach Explanations for Problems 1-4

### 704_binary_search.md

**Worked Example:**

```markdown
## Worked Example

The classic case: find an exact value in a sorted array. We maintain a search range [left, right] and check the middle element. If it matches, we're done. If the target is larger, the answer must be in the right half (everything to the left of mid is smaller, so we can discard it). If smaller, the answer is in the left half. Each step cuts the range in half.

```
Input: nums = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91], target = 23

  left=0, right=9, mid=4 → nums[4] = 16
  16 < 23 → target is in right half. left = 5.
  Eliminated: [2, 5, 8, 12, 16]

  left=5, right=9, mid=7 → nums[7] = 56
  56 > 23 → target is in left half. right = 6.
  Eliminated: [56, 72, 91]

  left=5, right=6, mid=5 → nums[5] = 23
  23 == 23 → found it. Return index 5.

3 steps to find the value in a 10-element array. Linear search would
have taken 6 steps (checking indices 0 through 5).

Not-found case: target = 20
  left=0, right=9, mid=4 → 16 < 20 → left=5
  left=5, right=9, mid=7 → 56 > 20 → right=6
  left=5, right=6, mid=5 → 23 > 20 → right=4
  left=5 > right=4 → search space empty. Return -1.
```
```

**Approach: Exact Match Binary Search - replace explanation:**

```
Maintain a search range defined by `left` and `right` pointers. At each step, compute `mid = (left + right) // 2` and compare `nums[mid]` to the target:

- If `nums[mid] == target`: return mid.
- If `nums[mid] < target`: the answer must be to the right (all elements before mid are even smaller). Set `left = mid + 1`.
- If `nums[mid] > target`: the answer must be to the left. Set `right = mid - 1`.

Continue until `left > right`, which means the search range is empty and the target doesn't exist. Return -1.

The `+1` and `-1` are critical. We've already checked `mid` and it's not the target, so we exclude it from the next range. Without the adjustment, the range wouldn't shrink and the loop would run forever.

**Time:** O(log n) - each step halves the search range. After k steps, the range is n / 2^k. When n / 2^k < 1, the search ends. Solving for k: k = log₂(n).
**Space:** O(1) - just three variables (left, right, mid).

This is the most fundamental algorithm in the pattern. Every other binary search variant builds on this structure.
```

### 035_search_insert.md

**Worked Example:**

```markdown
## Worked Example

This is a boundary-finding problem. Instead of "is this value here?", we're asking "where should this value go?" If the target exists, return its index. If it doesn't, return the index where it would be inserted to keep the array sorted. This is exactly what Python's `bisect_left` does.

The key difference from exact-match binary search: when the search ends without finding the target, `left` naturally points to the correct insertion position. Elements before `left` are all smaller than the target, and elements from `left` onward are all larger or equal.

```
Input: nums = [1, 3, 5, 7, 9, 11], target = 6

  left=0, right=5, mid=2 → nums[2] = 5
  5 < 6 → left = 3

  left=3, right=5, mid=4 → nums[4] = 9
  9 > 6 → right = 3

  left=3, right=3, mid=3 → nums[3] = 7
  7 > 6 → right = 2

  left=3 > right=2 → not found.
  Return left = 3. Insert 6 at index 3: [1, 3, 5, 6, 7, 9, 11].

Target exists case: target = 7
  left=0, right=5, mid=2 → 5 < 7 → left=3
  left=3, right=5, mid=4 → 9 > 7 → right=3
  left=3, right=3, mid=3 → 7 == 7 → return 3.

Target at edges: target = 0
  left=0, right=5, mid=2 → 5 > 0 → right=1
  left=0, right=1, mid=0 → 1 > 0 → right=-1
  left=0 > right=-1 → return 0 (insert at the beginning).
```
```

**Approach: Left-Boundary Binary Search - replace explanation:**

```
This is a standard binary search where the "not found" behavior returns the insertion point instead of -1. The algorithm is identical to exact match binary search, and the insertion point falls out naturally from the final value of `left`.

Here's why `left` is the correct insertion point: during the search, `left` moves right past elements that are too small, and `right` moves left past elements that are too big. When the loop ends (`left > right`), `left` points to the first element that is greater than or equal to the target. That's exactly where the target should be inserted.

This is equivalent to Python's `bisect.bisect_left(nums, target)`.

**Time:** O(log n) - same as exact match binary search.
**Space:** O(1).

This is the foundation for many boundary-finding problems. Once you understand that `left` converges to the first position where `nums[left] >= target`, you can adapt this template to find any kind of boundary.
```

### 074_search_2d_matrix.md

**Worked Example:**

```markdown
## Worked Example

The matrix is sorted row by row, and each row starts with a value larger than the previous row's last value. This means if you read the matrix left-to-right, top-to-bottom, it's one continuous sorted sequence. We can treat the 2D matrix as a 1D sorted array and do a single binary search.

The trick: convert between a 1D index and 2D (row, col) coordinates. For a matrix with `m` rows and `n` columns: `row = index // n`, `col = index % n`. For example, in a 3×4 matrix, 1D index 7 maps to row 1, col 3 (7 // 4 = 1, 7 % 4 = 3).

```
Input: matrix = [[1,  3,  5,  7],
                 [10, 11, 16, 20],
                 [23, 30, 34, 50]]
       target = 16

  m=3 rows, n=4 cols. Total elements = 12.
  Treat as 1D: [1, 3, 5, 7, 10, 11, 16, 20, 23, 30, 34, 50]

  left=0, right=11, mid=5 → row=5//4=1, col=5%4=1 → matrix[1][1] = 11
  11 < 16 → left = 6

  left=6, right=11, mid=8 → row=8//4=2, col=8%4=0 → matrix[2][0] = 23
  23 > 16 → right = 7

  left=6, right=7, mid=6 → row=6//4=1, col=6%4=2 → matrix[1][2] = 16
  16 == 16 → found it at row 1, col 2.

3 steps for a 3×4 matrix (12 elements). log₂(12) ≈ 4, so that's expected.
```
```

**Approach 1: Flatten to 1D - replace explanation:**

```
Since the matrix rows are sorted and each row starts larger than the previous row ends, the entire matrix is one sorted sequence read left-to-right, top-to-bottom. Apply standard binary search on the conceptual 1D array.

The only trick is index conversion. For a matrix with `n` columns:
- 1D index → 2D: `row = idx // n`, `col = idx % n`
- 2D → 1D: `idx = row * n + col`

Search range is `left = 0` to `right = m * n - 1`. At each step, convert `mid` to (row, col) to look up the value in the matrix.

**Time:** O(log(m × n)) - binary search over all elements.
**Space:** O(1) - no actual flattening, just index math.

This is the cleanest approach and what most interviewers expect. The index conversion is the only thing you need beyond standard binary search.
```

**Approach 2: Binary Search Row Then Column - replace explanation:**

```
Alternatively, find the correct row first, then search within that row. Two binary searches instead of one.

Step 1: Binary search on the first column to find which row the target belongs in. The target is in row `r` if `matrix[r][0] <= target <= matrix[r][n-1]`.

Step 2: Binary search within row `r` for the target.

**Time:** O(log m + log n) = O(log(m × n)) - same as the flatten approach.
**Space:** O(1).

Mathematically identical complexity, but conceptually simpler for some people since each binary search is standard. The flatten approach does it in one search instead of two.
```

### 153_find_min_rotated.md

**Worked Example:**

```markdown
## Worked Example

A rotated sorted array was originally sorted, then some number of elements were moved from the front to the back. For example, [1,2,3,4,5,6,7] rotated by 3 becomes [4,5,6,7,1,2,3]. The minimum element is at the "rotation point" where the sequence breaks.

The key insight for binary search: compare the middle element to the rightmost element. If `nums[mid] > nums[right]`, the rotation point (and therefore the minimum) is somewhere in the right half. If `nums[mid] <= nums[right]`, mid is already in the right (sorted) section, so the minimum is at mid or to the left.

This works because one half of the array is always in sorted order, and the minimum is always in the unsorted half (or at the boundary).

```
Input: nums = [6, 7, 9, 11, 15, 2, 3, 5]  (originally [2,3,5,6,7,9,11,15], rotated by 5)

  left=0, right=7
  mid=3 → nums[3]=11, nums[right]=nums[7]=5
  11 > 5 → minimum is in the right half. left = 4.
  Eliminated: [6, 7, 9, 11] (all larger than 5, can't contain the min)

  left=4, right=7
  mid=5 → nums[5]=2, nums[right]=5
  2 <= 5 → minimum is at mid or to the left. right = 5.
  Eliminated: [3, 5]

  left=4, right=5
  mid=4 → nums[4]=15, nums[right]=nums[5]=2
  15 > 2 → left = 5

  left=5, right=5 → left == right. Minimum is nums[5] = 2.

4 steps for 8 elements. The minimum is 2, which is at the rotation point
where 15 drops to 2 (the original beginning of the sorted array).

No-rotation case: nums = [1, 2, 3, 4, 5]
  mid=2 → nums[2]=3 <= nums[4]=5 → right=2
  mid=1 → nums[1]=2 <= nums[2]=3 → right=1
  mid=0 → nums[0]=1 <= nums[1]=2 → right=0
  left==right==0 → minimum is nums[0] = 1. Correctly identifies the
  first element as the minimum (no rotation happened).
```
```

**Approach: Modified Binary Search - replace explanation:**

```
Standard binary search compares mid to the target. Here, we compare mid to the rightmost element to determine which half contains the minimum.

The logic:
- If `nums[mid] > nums[right]`: the rotation point is between mid+1 and right. The left half (including mid) is part of the "rotated up" section and can't contain the minimum. Set `left = mid + 1`.
- If `nums[mid] <= nums[right]`: mid through right is sorted normally. The minimum could be at mid, but not after it. Set `right = mid` (not `mid - 1`, because mid itself might be the answer).

Note the asymmetry: `left = mid + 1` (excluding mid) vs `right = mid` (including mid). This is because:
- When we go right, mid is too large to be the minimum, so we exclude it.
- When we go left, mid might be the minimum, so we keep it.

The loop condition is `while left < right` (not `<=`). When left == right, we've converged to the minimum. Return `nums[left]`.

Why compare to the right end instead of the left? Comparing to the right consistently tells us which half has the rotation break. Comparing to the left creates ambiguous cases when the array isn't rotated.

**Time:** O(log n) - halving the range each step.
**Space:** O(1).

This problem assumes no duplicates. With duplicates (LeetCode 154), the worst case degrades to O(n) because you can't always determine which half to eliminate.
```

---

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

git diff --name-only | grep -v '.md$'
uv run pytest patterns/03_binary_search/ -v --tb=short 2>&1 | tail -5

# Spot-check README has teaching sections
for section in "The basics" "How it works step by step" "What O(log n)" "The one requirement" "The three types" "Common bugs" "bisect module"; do
    grep -q "$section" patterns/03_binary_search/README.md && echo "✅ $section" || echo "❌ MISSING: $section"
done

# Spot-check rotated array worked example
grep "Input: nums" patterns/03_binary_search/problems/153_find_min_rotated.md
```

Show spot-checks. Then run Part 2.
