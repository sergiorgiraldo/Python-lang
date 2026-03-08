# CC Prompt: Rework README - Pattern 02 Two Pointers

## What This Prompt Does

Rewrites the README.md "What Is It?", "Visual Aid" and "Trade-offs" sections for pattern 02 with the same teaching depth as pattern 01's hash map README.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- Only modify `patterns/02_two_pointers/README.md`
- REPLACE the specified sections only. Leave all other sections untouched.
- NO Oxford commas, NO em dashes, NO exclamation points

---

## Replace `## What Is It?` (everything up to `## When to Use It`)

```markdown
## What Is It?

### The core idea

Two pointers is a technique where you use two variables (the "pointers") to track positions in an array or sequence. By moving these pointers strategically, you can solve problems in a single pass (O(n)) that would otherwise require comparing every possible pair of elements (O(n²)).

It's not a data structure like a hash map. It's a *movement strategy* - a way of organizing your scan through the data so you never waste work.

### The three patterns

Almost every two-pointer problem falls into one of three categories:

**1. Opposite ends (converging pointers)**

Start one pointer at the beginning, one at the end. Move them toward each other based on some condition. This works when the array is sorted and you're looking for a pair that satisfies some target.

```python
left, right = 0, len(arr) - 1
while left < right:
    # check arr[left] + arr[right] against target
    # move left forward OR right backward
```

Why it works: in a sorted array, moving the left pointer right increases the sum. Moving the right pointer left decreases it. You can steer toward the target without checking every pair.

**2. Same direction (fast/slow or read/write)**

Both pointers start at (or near) the beginning and move forward. One scans ahead (the "read" or "fast" pointer) while the other marks a position (the "write" or "slow" pointer). This is the pattern for in-place removal, deduplication and partitioning.

```python
write = 0
for read in range(len(arr)):
    if should_keep(arr[read]):
        arr[write] = arr[read]
        write += 1
```

Why it works: the read pointer looks at every element. The write pointer only advances when we find something worth keeping. Everything before `write` is the "cleaned" portion of the array.

**3. Two sequences (merge pointers)**

One pointer per sequence, both moving forward. At each step, compare the elements at both pointers, process the smaller (or appropriate) one and advance that pointer. This is the pattern for merging sorted data.

```python
i, j = 0, 0
while i < len(a) and j < len(b):
    if a[i] <= b[j]:
        process(a[i]); i += 1
    else:
        process(b[j]); j += 1
```

Why it works: both sequences are sorted. By always taking the smaller current element, you produce a sorted result in O(n + m) without re-sorting.

### How two pointers connects to data engineering

If you've worked with sorted data in production, you've used two-pointer logic even if you didn't call it that:

- **Merging sorted files or partitions** (same as merge sort's merge step)
- **Deduplicating sorted exports** (read/write pointer skipping duplicates)
- **Incremental sync between two sorted datasets** (one pointer per dataset, classifying inserts/updates/deletes)
- **Data compaction** (scanning sorted data, writing only what passes a filter)

The SQL equivalent is a merge join - the database walks two sorted tables in parallel, matching rows where keys align. Two pointers is the Python version of that operation.

### Two pointers vs hash map

Both techniques can solve "find a pair" problems. The trade-offs:

| | Two Pointers | Hash Map |
|---|---|---|
| Time | O(n) (or O(n log n) if sorting needed) | O(n) |
| Space | O(1) | O(n) |
| Requires sorted input? | Yes (for opposite-end pattern) | No |
| Best for | Sorted data, in-place operations, merging | Unsorted data, frequency counting |

If the input is already sorted, two pointers usually wins because it uses no extra memory. If the input is unsorted and you'd need to sort it first, the hash map might be simpler (O(n) time and O(n) space vs O(n log n) time and O(1) space).

### The key thing to understand about pointer movement

In every two-pointer solution, the critical question is: **which pointer do I move, and why?**

The answer is always based on eliminating possibilities. When you move a pointer, you're saying "every option I'm skipping over is guaranteed to be worse (or invalid) than what I'm moving toward." If you can't make that guarantee, two pointers won't work for the problem.

For example, in the container water problem (11): you always move the pointer at the shorter line. The water level is limited by the shorter line (it overflows over it). Making the container narrower while keeping the same bottleneck can only reduce the area. Moving the taller line's pointer would never help. Moving the shorter one might find something taller.

### What the problems in this section use

| Problem | Pattern | What the pointers track | Why two pointers helps |
|---|---|---|---|
| Remove Duplicates | Same direction | Write position + read scan | Skip duplicates in-place, O(1) space |
| Merge Sorted Array | Two sequences | Position in each array | Merge without extra allocation |
| Move Zeroes | Same direction | Write position + read scan | Partition non-zeros to front |
| Two Sum II | Opposite ends | Left and right candidates | Sorted input, steer toward target |
| Three Sum | Opposite ends (nested) | Fixed element + two-pointer search | Reduce O(n³) to O(n²) |
| Container Water | Opposite ends | Left and right walls | Maximize area by eliminating worse walls |
| Sort Colors | Three pointers | Low/mid/high boundaries | Three-way partition in one pass |
| Squares of Sorted Array | Opposite ends | Left and right (largest squares at ends) | Build result from largest to smallest |
| Trapping Rain Water | Opposite ends | Left and right with running maxes | Calculate water without precomputed arrays |
```

## Replace `## Visual Aid` (everything up to `## Template`)

```markdown
## Visual Aid

```
Pattern 1: Opposite ends (sorted pair sum)

Find two numbers that sum to 12 in [2, 4, 5, 7, 9, 11]

  left=0 (2), right=5 (11): 2+11=13 > 12
    13 is too big. Moving left up would make it bigger. Move right down.

  left=0 (2), right=4 (9):  2+9=11 < 12
    11 is too small. Moving right down would make it smaller. Move left up.

  left=1 (4), right=4 (9):  4+9=13 > 12
    Too big again. Move right down.

  left=1 (4), right=3 (7):  4+7=11 < 12
    Too small. Move left up.

  left=2 (5), right=3 (7):  5+7=12 ✓ Found it.

  5 comparisons instead of 15 pairs. Each step eliminates one position.

Pattern 2: Read/write (remove duplicates from sorted array)

  Input: [1, 1, 2, 2, 2, 3, 4, 4]
          W
          R

  R=0: val=1. First element always stays. write=1.
  R=1: val=1. Same as previous (1==1). Skip.
  R=2: val=2. New value (2!=1). Write to position 1. write=2.
  R=3: val=2. Same. Skip.
  R=4: val=2. Same. Skip.
  R=5: val=3. New value. Write to position 2. write=3.
  R=6: val=4. New value. Write to position 3. write=4.
  R=7: val=4. Same. Skip.

  Result: [1, 2, 3, 4, _, _, _, _]  unique count = 4
  One pass. O(1) extra space.

Pattern 3: Merging two sorted sequences

  A: [1, 4, 7]     B: [2, 3, 8]
      ^                 ^

  1 < 2 → output 1, advance pA.    Result: [1]
  4 > 2 → output 2, advance pB.    Result: [1, 2]
  4 > 3 → output 3, advance pB.    Result: [1, 2, 3]
  4 < 8 → output 4, advance pA.    Result: [1, 2, 3, 4]
  7 < 8 → output 7, advance pA.    Result: [1, 2, 3, 4, 7]
  A done → output rest of B: [8].  Result: [1, 2, 3, 4, 7, 8]

  Each element processed exactly once. O(n + m).
```
```

## Replace `## Trade-offs` (everything up to `## Problems in This Section`)

```markdown
## Trade-offs

**The core advantage of two pointers is O(1) space.** Unlike hash maps (which need O(n) extra memory), two pointers work with just a couple of index variables. This matters when the data is large or when the problem requires in-place modification.

**The main constraint is ordering.** Opposite-end and merge patterns require sorted input. If the data isn't sorted, you need to sort it first (O(n log n)), which may make a hash map approach simpler.

**When two pointers doesn't apply:**
- Unsorted data where sorting would cost more than a hash map
- Problems requiring random access to arbitrary elements (not sequential scanning)
- Problems where the relationship between elements isn't monotonic (moving a pointer doesn't consistently improve or worsen the result)
```

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

git diff --name-only | grep -v '.md$'  # Should be empty
uv run pytest patterns/02_two_pointers/ -v --tb=short 2>&1 | tail -5

echo "=== README subsections ==="
grep "^### " patterns/02_two_pointers/README.md

echo ""
echo "=== Key teaching sections present? ==="
for section in "The core idea" "three patterns" "Opposite ends" "Same direction" "Two sequences" "vs hash map" "pointer movement" "problems in this section"; do
    grep -qi "$section" patterns/02_two_pointers/README.md && echo "✅ $section" || echo "❌ $section"
done
```
