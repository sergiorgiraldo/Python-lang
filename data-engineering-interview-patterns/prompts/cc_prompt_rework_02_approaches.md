# CC Prompt: Rework Approach Explanations - Pattern 02 Two Pointers

## What This Prompt Does

Rewrites every `📝 Explanation` block in all 9 problem `.md` files. Run after the README and worked example prompts.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- Only modify content inside `<details>` blocks containing `📝 Explanation`.
- Leave `💡 Hint` and `💻 Code` blocks untouched.
- NO Oxford commas, NO em dashes, NO exclamation points

---

### 026_remove_duplicates.md - Approach 1 (Read/Write Pointers)

```
Both pointers start near the beginning. Write begins at index 1 (index 0 is always kept). Read scans from index 1 forward.

At each step, compare what read sees to the last value written (at `write - 1`). If different, copy to write position and advance write. If same, skip.

Because the array is sorted, all copies of the same value are adjacent. Once read passes the last copy, write has already recorded one and we'll never see that value again.

**Time:** O(n) - read visits every element once.
**Space:** O(1) - two index variables. Modified in place.

This is the foundational "read/write pointer" pattern. Same structure appears in Move Zeroes, data compaction and any "remove X from sorted array in place" problem.
```

### 088_merge_sorted.md - Approach 1 (Merge from the Back)

```
Three pointers: `p1` at the last real element of nums1 (m-1), `p2` at the last of nums2 (n-1), `write` at the very end (m+n-1).

At each step, compare nums1[p1] and nums2[p2]. Write the larger value at nums1[write]. Decrement the pointer that was used and decrement write.

If p1 runs out first, copy remaining nums2 elements. If p2 runs out first, remaining nums1 elements are already in place.

**Time:** O(n + m) - each element processed exactly once.
**Space:** O(1) - merging into existing space in nums1.

Edge case: if p2 runs out but p1 hasn't, we're done. Those nums1 elements were already at the front and nothing shifted them.
```

### 283_move_zeroes.md - Approach 1 (Copy Then Zero-Fill)

```
Two passes. First pass: read scans everything, write tracks where the next non-zero goes. When read finds a non-zero, copy it to write position and advance write. Zeros are skipped.

After the first pass, positions 0 to write-1 contain non-zeros in original order. Second pass fills positions write through n-1 with zeros.

**Time:** O(n) - two passes, each element touched at most twice.
**Space:** O(1) - in place.

Simpler logic than the swap approach. The "copy good stuff forward, clean up after" pattern.
```

### 283_move_zeroes.md - Approach 2 (Swap-Based)

```
Instead of a separate zero-fill pass, swap each non-zero directly with the write position. When read finds a non-zero, swap nums[read] with nums[write] and advance both.

The swap naturally moves zeros backward. Safe because everything at or after write is either a zero or a value read will reach later.

**Time:** O(n) - single pass.
**Space:** O(1) - in place.

Common interview follow-up: "can you do it in one pass?" Both approaches are O(n). The difference is stylistic.
```

### 167_two_sum_ii.md - Approach 1 (Hash Map)

```
Same approach as LeetCode 1 (Two Sum). Build a dict mapping numbers to indices. For each number, check if `target - number` exists.

**Time:** O(n). **Space:** O(n).

Works but ignores the sorted property. Like doing a full table scan when you have an index. Mention it in an interview, then optimize with two pointers.
```

### 167_two_sum_ii.md - Approach 2 (Opposite-End Pointers)

```
Start at both ends of the sorted array. Compute the sum:
- Equals target → return indices.
- Too large → right value is too big. Move right left.
- Too small → left value is too small. Move left right.

Why moving works: if `left + right > target`, then pairing right with ANY value ≥ left produces an even bigger sum. So right can't be part of any valid pair. Eliminate it. Same logic for the "too small" case.

Each step eliminates one value. At most n steps until pointers meet.

**Time:** O(n) - one pass.
**Space:** O(1) - two index variables.

Same time as hash map but O(1) space. Optimal when input is sorted.
```

### 015_three_sum.md - Approach (Sort + Two Pointers)

```
Sort the array. For each element at index i (the "fixed" element), use opposite-end two pointers (left=i+1, right=n-1) to find a pair summing to `-nums[i]`.

Skip duplicates at three levels:
- Skip fixed element if `nums[i] == nums[i-1]`
- After finding a triplet, advance left past duplicate values
- After finding a triplet, retreat right past duplicate values

Early exit: if `nums[i] > 0`, stop. Three positive numbers can't sum to zero.

**Time:** O(n²) - sort is O(n log n), outer loop × inner two-pointer = O(n²).
**Space:** O(1) extra (or O(n) for the sort).

Reduces O(n³) brute force to O(n²) by replacing the inner two loops with a single two-pointer scan.
```

### 011_container_water.md - Approach 1 (Brute Force)

```
Check every pair of lines. Area = min(height[i], height[j]) × (j - i). Track the maximum.

**Time:** O(n²) - all pairs. **Space:** O(1).

Valid starting point. State it, note O(n²), then explain the greedy O(n) approach.
```

### 011_container_water.md - Approach 2 (Opposite-End Greedy)

```
Start at both ends (maximum width). At each step, move the pointer at the shorter line.

Why: area = min(left_h, right_h) × width. The shorter line is the bottleneck. If we move the taller line inward, width decreases and the bottleneck stays the same (or gets worse). Area can only shrink. Moving the shorter line might find something taller that overcomes the lost width.

Every step eliminates a provably useless configuration. n-1 steps total.

**Time:** O(n) - one pass.
**Space:** O(1).
```

### 075_sort_colors.md - Approach 1 (Counting Sort)

```
Two passes. First: count 0s, 1s and 2s. Second: overwrite the array using the counts.

**Time:** O(n) - two passes. **Space:** O(1) - three counters.

Simple and correct. Overwrites every element even if most are already placed. The Dutch National Flag approach does it in one pass.
```

### 075_sort_colors.md - Approach 2 (Dutch National Flag)

```
Three pointers: `low` (boundary of 0s), `mid` (scanner), `high` (boundary of 2s).

- `nums[mid] == 0`: swap with low, advance both low and mid. The swapped-in value from low is always 1 (already processed region), so it's safe to advance mid.
- `nums[mid] == 1`: correct region. Advance mid only.
- `nums[mid] == 2`: swap with high, decrement high. Do NOT advance mid because the swapped-in value hasn't been inspected.

Stop when mid > high.

**Time:** O(n) - each element inspected at most twice.
**Space:** O(1) - three pointers.

The "don't advance mid after high swap" is the most common bug and the most common interview follow-up.
```

### 977_squares_sorted.md - Approach 1 (Square and Sort)

```
Square every element, then sort. One line: `sorted(x*x for x in nums)`.

**Time:** O(n log n) - sort dominates. **Space:** O(n).

Ignores the sorted structure of the input. We can do O(n).
```

### 977_squares_sorted.md - Approach 2 (Opposite-End Pointers)

```
Largest squared values are at the extremes (large negatives become large positives). Two pointers from both ends, compare absolute values, write the larger to the back of the result array.

1. Create result array of size n.
2. left=0, right=n-1, write=n-1.
3. Compare abs(nums[left]) vs abs(nums[right]). Write the larger squared value at result[write]. Move that pointer inward. Decrement write.

**Time:** O(n) - each element squared and placed once.
**Space:** O(n) - result array (can't do in-place since we write from the back).

Same "fill from the back" idea as Merge Sorted Array (problem 88).
```

### 042_trapping_rain_water.md - Approach 1 (Prefix/Suffix Max Arrays)

```
Water at position i = min(left_max[i], right_max[i]) - height[i].

Precompute two arrays:
- `left_max[i]` = max height from 0 through i (left to right scan)
- `right_max[i]` = max height from i through n-1 (right to left scan)

Third pass: for each position, compute the water using both arrays.

**Time:** O(n) - three passes.
**Space:** O(n) - two extra arrays.

Easier to understand than two pointers. Solid first answer.
```

### 042_trapping_rain_water.md - Approach 2 (Two Pointers)

```
Track running left_max and right_max as we go. If left_max ≤ right_max, the left side is the bottleneck. Process left and advance. Otherwise process right and retreat.

Why: when left_max ≤ right_max, we know the water at the left pointer is bounded by left_max regardless of what's further right (the right side is at least as tall). So we don't need the full right_max array.

**Time:** O(n) - single pass.
**Space:** O(1) - four variables.

Harder to reason about but optimal. The key proof: when processing the left side, left_max can only increase as left moves right, so the water calculation is correct even though we haven't seen the rest of the right side.
```

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns
git diff --name-only | grep -v '.md$'
uv run pytest patterns/02_two_pointers/ -v --tb=short 2>&1 | tail -3

echo "=== Explanation quality check ==="
for f in patterns/02_two_pointers/problems/*.md; do
    name=$(basename "$f")
    awk '/📝 Explanation/{found=1; lines=0; next} found && /<\/details>/{if(lines<4) printf "❌ %s: %d lines\n", "'"$name"'", lines; found=0} found && /\S/{lines++}' "$f"
done
echo "(no output = all substantial)"
```
