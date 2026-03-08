# CC Prompt: Enrich Pattern 02 (Two Pointers) to Principal Level

## Context

Pattern 02 has 9 problems and 4 DE scenarios. This enrichment adds principal-level depth to .md files only. No code changes.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- NO Oxford commas, NO em dashes, NO exclamation points
- Do NOT modify any .py files
- Do NOT remove existing content - only ADD sections
- 3-8 sentences per "At Scale" section
- Use specific numbers

---

## Task 1: Enrich README.md Trade-offs Section

In `patterns/02_two_pointers/README.md`, find `## Trade-offs` and ADD to the end:

```markdown
### Scale characteristics

Two pointers operates in O(1) extra memory regardless of input size. This is its superpower at scale. The constraint: the data must be sorted (or have some ordering property). Sorting costs O(n log n) time and O(n) space for a copy, or O(1) extra space if you sort in-place (modifying the input).

| n | Sort time (approx) | Two-pointer scan | Total |
|---|---|---|---|
| 10M | ~2 seconds | ~0.1 seconds | ~2 seconds |
| 1B | ~5 minutes | ~10 seconds | ~5 minutes |
| 100B | Doesn't fit in memory | N/A | Need external sort |

**Distributed equivalent:** Two pointers on sorted data maps to merge-based operations in distributed systems. Spark's sort-merge join sorts both sides by join key, then uses a two-pointer-like scan to find matches. External merge sort handles data that doesn't fit in memory: sort chunks that fit in RAM, write to disk, merge sorted chunks. This is how every database engine handles large sorts.

**When to prefer two pointers over hash maps:** When memory is constrained and the data is already sorted (or sorting is acceptable). A hash map approach to Two Sum uses O(n) memory. The sort + two-pointer approach uses O(1) extra memory after the sort. At 1B elements, that's the difference between needing 80GB of RAM and needing 8GB.

### SQL equivalent

Two-pointer algorithms correspond to sort-merge operations in SQL. When you write an ORDER BY or a merge join, the engine is effectively using the sorted-data + pointer-scan approach. Window functions with ORDER BY (like LAG/LEAD for comparing adjacent rows) are the SQL equivalent of the two-pointer "compare neighbors" pattern. The SQL section's window functions and joins subsections cover these patterns.
```

## Task 2: Add "At Scale" Section to Each Problem .md

Add `## At Scale` after `## DE Application` in each problem file:

### 026_remove_duplicates.md (or whatever the actual filename is)
```markdown
## At Scale

In-place dedup with two pointers uses O(1) extra memory - the only approach that works when the array is too large to copy. For 10M elements, the scan takes ~50ms. For data that doesn't fit in memory, you need external sort followed by a streaming dedup pass: read sorted chunks sequentially, output only when the value changes. In SQL, this is `SELECT DISTINCT` on a sorted column or `ROW_NUMBER() PARTITION BY value ORDER BY value` to pick one representative per group. The two-pointer approach here is exactly what the database engine does internally during a streaming distinct operation.
```

### 088_merge_sorted_array.md
```markdown
## At Scale

Merging two sorted arrays is the core operation in merge sort and sort-merge joins. The backwards merge (from end to start) avoids extra memory - critical when arrays are large. For two sorted files of 10GB each, you'd stream both files sequentially and write the merged output. This is exactly how external merge sort works: merge sorted runs from disk. In Spark, sort-merge join sorts both sides by key, then merges with a two-pointer scan. The O(1) extra memory property makes this the preferred join strategy for large datasets where neither side fits in memory for a hash join.
```

### 283_move_zeroes.md
```markdown
## At Scale

In-place partitioning uses O(1) memory. The two-pointer approach makes a single pass, so it's I/O-optimal: each element is read once and written at most once. At 1B elements, the bottleneck is memory bandwidth, not computation. The partition operation is the building block of quicksort and quickselect. In data pipelines, this pattern appears as "filter and compact": remove null/invalid records from a dataset while preserving order of valid records. Spark's `df.filter(col("value") != 0)` does this logically but materializes a new DataFrame rather than modifying in-place.
```

### 167_two_sum_sorted.md
```markdown
## At Scale

Two pointers on sorted data uses O(1) memory vs O(n) for the hash map approach. For 1B sorted integers, the scan takes ~10 seconds and requires zero extra memory beyond the input. The sorted precondition is the key constraint: if the data arrives unsorted, you pay O(n log n) to sort it first. In a database context, if the column has an index (B-tree), the data is already sorted and the two-pointer scan is free. This is why indexed columns enable efficient range queries and pair-finding. An interviewer asking "what if the array is already sorted?" is testing whether you recognize that sorted data unlocks better algorithms.
```

### 015_3sum.md
```markdown
## At Scale

Sort + two pointers gives O(n^2) time with O(1) extra memory. For n=10K, that's 100M operations (~0.1 seconds). For n=100K, that's 10B operations (~10 seconds). For n=1M+, O(n^2) is too slow regardless of approach. The hash set alternative trades memory for slightly simpler code but is still O(n^2) time. At scale, 3Sum-type problems (find matching triplets across datasets) become join problems: a three-way join with a filter condition. In SQL: `SELECT a.val, b.val, c.val FROM t a JOIN t b JOIN t c WHERE a.val + b.val + c.val = 0`. The optimizer decides whether to use hash joins or sort-merge joins based on data size.
```

### 011_container_with_most_water.md
```markdown
## At Scale

Two pointers scans n elements once: O(n) time, O(1) memory. Even at 1B elements, this completes in seconds and uses no extra memory. The greedy insight (move the shorter pointer inward) is provably optimal. This problem doesn't have a meaningful distributed equivalent because the two pointers must see the full array to make correct decisions. However, the "greedy narrowing" pattern appears in database query optimization: range scans that progressively narrow the search space based on constraints. At scale, the primary concern is data locality: sequential access through a sorted array is cache-friendly and I/O-efficient.
```

### 075_sort_colors.md
```markdown
## At Scale

Dutch National Flag uses O(1) memory and a single pass. It's a three-way partition: elements less than pivot, equal to pivot, greater than pivot. For 1B elements, this takes ~10 seconds. The partition operation is the core of quicksort and appears in distributed systems as the shuffle phase: partition data into buckets by key range. In Spark, `repartitionByRange` does a multi-way partition. The three-way variant is important when many elements equal the pivot (common with low-cardinality columns like status codes or country codes). Without three-way partitioning, quicksort degrades to O(n^2) on inputs with many duplicates.
```

### 977_squares_of_sorted_array.md
```markdown
## At Scale

Two pointers from both ends produces a sorted result in O(n) time and O(n) space (for the output array). The key insight - largest squares are at the extremes of a sorted array with negatives - avoids an O(n log n) sort of the squared values. At 1B elements, saving the log n factor means ~30x faster. In data pipelines, the "merge two sorted sequences" pattern appears whenever you combine pre-sorted partitions. A sorted output from two sorted inputs is the merge step of merge sort, sort-merge joins and external sorting.
```

### 042_trapping_rain_water.md
```markdown
## At Scale

The two-pointer approach uses O(1) memory and a single pass. The prefix max approach uses O(n) memory for the left_max and right_max arrays. At 10M elements, that's ~80MB of extra memory vs zero. At 1B elements, the O(n) approach needs 8GB of extra arrays - the two-pointer approach needs nothing. The monotonic stack approach (Pattern 08) also uses O(n) memory in the worst case. For time-series analysis at scale (finding periods where a metric dips below surrounding peaks), the two-pointer O(1)-memory approach is the only viable option for streaming data where you can't store the full history.
```

## Task 3: Enrich Interview Tips with Evaluator Framing

Add to the `## Interview Tips` section of each problem:

**026 (Remove Duplicates):**
```markdown
**What the interviewer evaluates:** The in-place constraint tests whether you can work within memory limits. Proposing a new array first (then optimizing) shows good problem-solving process. Mentioning that this is how streaming DISTINCT works in databases shows engineering maturity.
```

**088 (Merge Sorted):**
```markdown
**What the interviewer evaluates:** The backwards-merge insight tests spatial reasoning. Starting from the end avoids extra memory allocation. Mentioning sort-merge joins or external merge sort connects the algorithm to production systems - a strong principal-level signal.
```

**283 (Move Zeroes):**
```markdown
**What the interviewer evaluates:** This tests in-place array manipulation with stability (preserving relative order). The two-pointer swap approach is clean but easy to get wrong with off-by-one errors. Walking through an example carefully before coding shows discipline.
```

**167 (Two Sum Sorted):**
```markdown
**What the interviewer evaluates:** Can you exploit the sorted precondition? Reaching for a hash map on sorted data is a yellow flag - it means you're applying patterns mechanically rather than analyzing the input. The follow-up "what if it's not sorted?" tests whether you understand the tradeoff: sort first + O(1) memory vs hash map + O(n) memory.
```

**015 (3Sum):**
```markdown
**What the interviewer evaluates:** Reducing 3Sum to Two Sum (fix one element, two-pointer the rest) tests decomposition skill. Duplicate handling tests attention to detail. The O(n^2) lower bound discussion tests theoretical understanding - you can't do better for the general case.
```

**011 (Container With Most Water):**
```markdown
**What the interviewer evaluates:** The greedy proof is what separates strong candidates. Saying "move the shorter pointer because..." tests whether you can reason about algorithm correctness, not just implement a pattern. An interviewer may ask you to prove why this works.
```

**075 (Sort Colors):**
```markdown
**What the interviewer evaluates:** Single-pass with three pointers tests your ability to manage complex state. The partition invariant (everything left of low is 0, everything right of high is 2) must be maintained at every step. Mentioning quicksort's partition step connects this to a foundational algorithm.
```

**977 (Squares of Sorted Array):**
```markdown
**What the interviewer evaluates:** Recognizing that the largest squares come from the extremes tests insight over brute force. The "two sorted halves" observation is the key. This is a warm-up problem - the interviewer expects a clean O(n) solution quickly and will move to harder follow-ups.
```

**042 (Trapping Rain Water):**
```markdown
**What the interviewer evaluates:** This is a hard problem used to test senior+ candidates. Multiple valid approaches (prefix arrays, two pointers, monotonic stack) exist. Starting with the prefix approach (correct but O(n) space), then optimizing to two pointers (O(1) space) shows the optimization process interviewers want to see. Explaining WHY the two-pointer invariant works is the principal-level differentiator.
```

## Task 4: No New Glossary Terms

Pattern 01 already added the key distributed terms (broadcast join, hash-partitioned join, key skew, salting, external hashing). Pattern 02 introduces:

- **external merge sort**: Sorting data too large for memory by sorting in-memory chunks, writing to disk, then merging sorted runs. O(n log n) time with O(M) memory where M is the available RAM.
- **sort-merge join**: Distributed join that sorts both sides by join key, then merges with a sequential scan. Preferred over hash joins when both sides are large. More expensive than hash join (due to sort) but handles arbitrarily large datasets.
- **streaming distinct**: Deduplication of a sorted stream by comparing each element to the previous. O(1) memory, requires sorted input.

Add these to the WORKING_GLOSSARY.md file.

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== At Scale sections ==="
for f in patterns/02_two_pointers/problems/*.md; do
    name=$(basename "$f")
    has_scale=$(grep -q "## At Scale" "$f" && echo "Y" || echo "N")
    echo "  $name: At Scale=$has_scale"
done

echo ""
echo "=== README enriched ==="
grep -q "Scale characteristics" patterns/02_two_pointers/README.md && echo "✅" || echo "❌"
grep -q "SQL equivalent" patterns/02_two_pointers/README.md && echo "✅" || echo "❌"

echo ""
echo "=== Evaluator framing ==="
for f in patterns/02_two_pointers/problems/*.md; do
    name=$(basename "$f")
    has_eval=$(grep -q "interviewer evaluates" "$f" && echo "Y" || echo "N")
    echo "  $name: evaluator=$has_eval"
done

echo ""
echo "=== Style check ==="
grep -rn "—" patterns/02_two_pointers/ --include="*.md" && echo "❌ Em dashes" || echo "✅ No em dashes"

echo ""
echo "=== Tests unaffected ==="
uv run pytest patterns/02_two_pointers/ --tb=short -q 2>&1 | tail -3
```
