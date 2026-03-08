# CC Prompt: Rework Worked Examples - Pattern 02 Two Pointers (Problems 6-9 + DE Scenarios)

## What This Prompt Does

Rewrites `## Worked Example` in problems 6-9 and all 4 DE scenarios. Run after the problems 1-5 prompt.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- Only modify `.md` files. REPLACE `## Worked Example` sections only.
- NO Oxford commas, NO em dashes, NO exclamation points

---

### 011_container_water.md

```markdown
## Worked Example

Two lines form a container. Water held = shorter line's height × distance between them. Start at both ends (max width). Move the shorter pointer inward each step because: the water level is limited by the shorter wall, and making the container narrower with the same bottleneck can only reduce the area. Moving the shorter wall *might* find a taller wall that compensates for the lost width.

```
Input: height = [3, 1, 6, 4, 5, 2, 8, 3, 7]
                 0  1  2  3  4  5  6  7  8

  left=0(3), right=8(7): area = min(3,7)×8 = 24. max=24. Left shorter → move left.
  left=1(1), right=8(7): area = min(1,7)×7 = 7.  max=24. Left shorter → move left.
  left=2(6), right=8(7): area = min(6,7)×6 = 36. max=36. Left shorter → move left.
  left=3(4), right=8(7): area = min(4,7)×5 = 20. max=36. Left shorter → move left.
  left=4(5), right=8(7): area = min(5,7)×4 = 20. max=36. Left shorter → move left.
  left=5(2), right=8(7): area = min(2,7)×3 = 6.  max=36. Left shorter → move left.
  left=6(8), right=8(7): area = min(8,7)×2 = 14. max=36. Right shorter → move right.
  left=6(8), right=7(3): area = min(8,3)×1 = 3.  max=36. Done.

  Answer: 36 (between index 2, height 6 and index 8, height 7).
  8 comparisons for 9 elements instead of 36 pairs.
```
```

### 075_sort_colors.md

```markdown
## Worked Example

Dutch National Flag: three pointers partition the array into [0s | 1s | unprocessed | 2s]. `low` marks where the next 0 goes, `high` marks where the next 2 goes, `mid` scans the unprocessed region. When mid sees 0, swap with low. When mid sees 2, swap with high (but DON'T advance mid because the swapped-in value hasn't been inspected). When mid sees 1, just advance.

```
Input: nums = [2, 0, 1, 2, 1, 0, 2, 0]
  low=0, mid=0, high=7

  mid=0: val=2 → swap(0,7): [0,0,1,2,1,0,2,2]. high=6. Don't advance mid.
  mid=0: val=0 → swap(0,0): no change. low=1, mid=1.
  mid=1: val=0 → swap(1,1): no change. low=2, mid=2.
  mid=2: val=1 → already correct. mid=3.
  mid=3: val=2 → swap(3,6): [0,0,1,2,1,0,2,2]. high=5. Don't advance mid.
  mid=3: val=2 → swap(3,5): [0,0,1,0,1,2,2,2]. high=4. Don't advance mid.
  mid=3: val=0 → swap(2,3): [0,0,0,1,1,2,2,2]. low=3, mid=4.
  mid=4: val=1 → correct. mid=5.
  mid=5 > high=4 → done.

  Result: [0, 0, 0, 1, 1, 2, 2, 2]. One pass, O(1) space.
```
```

### 977_squares_sorted.md

```markdown
## Worked Example

In a sorted array with negatives, the largest squared values are at the ends (large negatives become large positives). Two pointers from both ends build the result from largest to smallest, filling from the back.

```
Input: nums = [-7, -3, -1, 2, 4, 6]

  left=0 (49), right=5 (36), write=5

  49 > 36 → result[5]=49. left=1.     result = [_, _, _, _, _, 49]
  9 < 36  → result[4]=36. right=4.    result = [_, _, _, _, 36, 49]
  9 < 16  → result[3]=16. right=3.    result = [_, _, _, 16, 36, 49]
  9 > 4   → result[2]=9. left=2.      result = [_, _, 9, 16, 36, 49]
  1 < 4   → result[1]=4. right=2.     result = [_, 4, 9, 16, 36, 49]
  left=right=2: result[0]=1.          result = [1, 4, 9, 16, 36, 49]

One pass, O(n). The naive approach (square everything, then sort) is O(n log n).
```
```

### 042_trapping_rain_water.md

```markdown
## Worked Example

Water at position i = min(tallest wall to its left, tallest wall to its right) - height[i]. The two-pointer approach tracks running maximums from each side. If left_max < right_max, the water at the left pointer is determined by left_max (right side is at least as tall). Process whichever side has the smaller running max.

```
Input: height = [0, 2, 0, 3, 0, 1, 4, 0, 2, 0, 3]
  left=0, right=10, left_max=0, right_max=0, water=0

  left_max(0) ≤ right_max(0): process left
    left_max = max(0, h[0]=0) = 0. water += 0. left=1.
  left_max(0) ≤ right_max(0): process left
    left_max = max(0, h[1]=2) = 2. water += 0. left=2.
  left_max(2) > right_max(0): process right
    right_max = max(0, h[10]=3) = 3. water += 0. right=9.
  left_max(2) ≤ right_max(3): process left
    left_max stays 2. water += 2-0 = 2. left=3. (total: 2)
  left_max(2) ≤ right_max(3): process left
    left_max = max(2, h[3]=3) = 3. water += 0. left=4.
  left_max(3) ≤ right_max(3): process left
    water += 3-0 = 3. left=5. (total: 5)
  left_max(3) ≤ right_max(3): process left
    water += 3-1 = 2. left=6. (total: 7)
  left_max(3) ≤ right_max(3): process left
    left_max = max(3, h[6]=4) = 4. water += 0. left=7.
  left_max(4) > right_max(3): process right
    water += 3-0 = 3. right=8. (total: 10)
  left_max(4) > right_max(3): process right
    water += 3-2 = 1. right=7. (total: 11)
  left_max(4) > right_max(3): process right
    water += 3-0 = 3. right=6. (total: 14)
  left > right → done.

  Total water: 14. One pass, O(1) space.
```
```

---

## DE Scenarios

### de_scenarios/merging_sorted_files.md

```markdown
## Worked Example

Merging two sorted files is the fundamental two-pointer operation in data engineering. One pointer per file, always output the smaller current value. Each file read exactly once.

```
File A (sorted timestamps): [08:01, 08:15, 08:42, 09:10, 09:30]
File B (sorted timestamps): [08:05, 08:20, 08:55, 09:25]

  pA→08:01 < pB→08:05 → output 08:01. Advance pA.
  pA→08:15 > pB→08:05 → output 08:05. Advance pB.
  pA→08:15 < pB→08:20 → output 08:15. Advance pA.
  pA→08:42 > pB→08:20 → output 08:20. Advance pB.
  pA→08:42 < pB→08:55 → output 08:42. Advance pA.
  pA→09:10 > pB→08:55 → output 08:55. Advance pB.
  pA→09:10 < pB→09:25 → output 09:10. Advance pA.
  pA→09:30 > pB→09:25 → output 09:25. Advance pB.
  B exhausted → output 09:30.

9 elements, 8 comparisons. Merging two 100M-row sorted files: 200M
steps. Concatenating and re-sorting: ~5 billion comparisons.
```
```

### de_scenarios/incremental_sync.md

```markdown
## Worked Example

Two pointers classify every record between two sorted datasets in a single pass: matches (unchanged/updated), source-only (inserts), target-only (deletes). This is database MERGE/CDC logic.

```
Source (sorted by ID): [101, 103, 105, 107, 109, 111]
Target (sorted by ID): [101, 102, 105, 107, 108, 111]

  src→101, tgt→101: match → compare content → UNCHANGED. Both advance.
  src→103, tgt→102: 102 < 103 → target-only → DELETE 102. Advance tgt.
  src→103, tgt→105: 103 < 105 → source-only → INSERT 103. Advance src.
  src→105, tgt→105: match → UNCHANGED. Both advance.
  src→107, tgt→107: match → content differs → UPDATE. Both advance.
  src→109, tgt→108: 108 < 109 → DELETE 108. Advance tgt.
  src→109, tgt→111: 109 < 111 → INSERT 109. Advance src.
  src→111, tgt→111: match → UNCHANGED. Both advance.

  inserts: [103, 109], updates: [107], deletes: [102, 108], unchanged: [101, 105, 111]
  Single pass, no hash maps. O(n + m).
```
```

### de_scenarios/data_compaction.md

```markdown
## Worked Example

Data compaction removes unwanted records in-place. Same read/write pattern as Remove Duplicates and Move Zeroes applied to production data.

```
Records (some flagged for deletion):
  [(ts=1, "valid", A), (ts=2, "expired", B), (ts=3, "valid", C),
   (ts=4, "expired", D), (ts=5, "expired", E), (ts=6, "valid", F),
   (ts=7, "valid", G), (ts=8, "expired", H)]

  write=0
  read=0: "valid"   → write[0]=A. write=1.
  read=1: "expired" → skip.
  read=2: "valid"   → write[1]=C. write=2.
  read=3: "expired" → skip.
  read=4: "expired" → skip.
  read=5: "valid"   → write[2]=F. write=3.
  read=6: "valid"   → write[3]=G. write=4.
  read=7: "expired" → skip.

  Compacted: [A, C, F, G]. Truncate at write=4.
  Single pass, O(n), no extra memory.
```
```

### de_scenarios/partitioning_data.md

```markdown
## Worked Example

Partitioning sorted data into segments by detecting boundary changes. Because data is sorted by the partition key, all records in each partition are contiguous.

```
Records sorted by date:
  [("2024-01-15", evt_1), ("2024-01-15", evt_2), ("2024-01-15", evt_3),
   ("2024-01-16", evt_4), ("2024-01-16", evt_5),
   ("2024-01-17", evt_6), ("2024-01-17", evt_7), ("2024-01-17", evt_8)]

  read=0: date=01-15. New partition → start writing to 2024-01-15/
  read=1-2: same date. Continue.
  read=3: date=01-16. BOUNDARY. Close 01-15 (3 records). Start 01-16.
  read=4: same. Continue.
  read=5: date=01-17. BOUNDARY. Close 01-16 (2 records). Start 01-17.
  read=6-7: same. Continue.
  End. Close 01-17 (3 records).

  Result: 3 partitions from one scan. Same logic as writing
  partitioned Parquet files from sorted data.
```
```

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns
git diff --name-only | grep -v '.md$'
uv run pytest patterns/02_two_pointers/ -v --tb=short 2>&1 | tail -3

echo "=== Worked Example count ==="
grep -rl "## Worked Example" patterns/02_two_pointers/ | wc -l
echo "(should be 13: 9 problems + 4 DE scenarios)"
```
