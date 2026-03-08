# CC Prompt: Enrich Pattern 07 (Intervals) to Principal Level

## Context

Pattern 07 has 6 problems and 4 DE scenarios. Enrichment adds principal-level depth to .md files only.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- NO Oxford commas, NO em dashes, NO exclamation points
- Do NOT modify any .py files. Only ADD content to .md files.
- 3-8 sentences per "At Scale" section

---

## Task 1: Enrich README.md Trade-offs Section

In `patterns/07_intervals/README.md`, find `## Trade-offs` and ADD:

```markdown
### Scale characteristics

Interval problems almost always sort first: O(n log n). The merge/scan pass is O(n). Memory depends on the specific problem but is typically O(n) for the output.

| n (intervals) | Sort time | Merge time | Total |
|---|---|---|---|
| 100K | ~20ms | ~5ms | ~25ms |
| 10M | ~3 seconds | ~500ms | ~3.5 seconds |
| 1B | ~5 minutes | ~1 minute | ~6 minutes |

**Distributed equivalent:** Sorting intervals by start time, then merging is a natural fit for distributed sort-merge. Spark handles this as: repartition by start time range, sort within each partition, merge locally, then handle cross-partition boundary intervals. The boundary case is the tricky part: an interval that starts in partition k might overlap with intervals in partition k+1. A second pass to merge boundary intervals is needed.

**Time-series join (interval overlap):** Finding overlapping time ranges across two datasets is an interval intersection problem. In SQL, this is often written as `WHERE a.start < b.end AND a.end > b.start` - a range join. Without optimization, this is O(n*m). Databases use interval trees, sort-merge approaches or bin-based partitioning to speed this up. BigQuery and Spark don't natively optimize range joins, so they often devolve to cross joins with filters. Knowing this limitation (and workarounds like binning by time period) is a principal-level skill.

### SQL equivalent

Interval operations in SQL use window functions and self-joins. Merging overlapping intervals: `LAG(end) OVER (ORDER BY start)` to detect overlaps, then group contiguous overlapping intervals. Meeting rooms (counting concurrent intervals): convert to events (start/end), sort, use a running count. The SQL section's window functions and joins subsections cover these patterns. Range joins (finding overlapping intervals across two tables) are particularly important for DE and are covered in the optimization subsection.
```

## Task 2: Add "At Scale" Section to Each Problem .md

### 252_meeting_rooms.md
```markdown
## At Scale

Sort + linear scan: O(n log n) time, O(1) extra memory (if sorting in-place). For 10M meetings, sorting takes ~3 seconds. The scan to check for overlaps takes ~50ms. At scale, "do any intervals overlap?" is a data quality check for scheduling data, SLA windows and maintenance periods. In a pipeline, this validates that time-based partitions don't overlap. In SQL: sort by start time, then use LAG to check if the previous end exceeds the current start. If any row satisfies that condition, overlaps exist.
```

### 253_meeting_rooms_ii.md
```markdown
## At Scale

The min-heap approach uses O(n) memory in the worst case (all meetings overlap). For 10M meetings, that's ~160MB for the heap. The sweep line alternative (sort start/end events, scan) uses O(n) memory for the events array but processes in a single pass. At scale, "maximum concurrent connections/sessions/jobs" is a key capacity planning metric. In production, this is often computed in SQL: `SELECT MAX(concurrent) FROM (SELECT timestamp, SUM(delta) OVER (ORDER BY timestamp) as concurrent FROM events)`. Cloud billing (concurrent slot usage in BigQuery) uses exactly this calculation. Knowing the algorithmic version helps you understand and optimize the SQL version.
```

### 056_merge_intervals.md
```markdown
## At Scale

Sort + merge: O(n log n) time, O(n) space for the output. For 10M intervals, this takes ~3 seconds. The merge pass is cache-friendly (sequential access). At scale, merging intervals is a common ETL operation: "consolidate overlapping time ranges for the same user." In SQL, this is surprisingly hard to do efficiently - it typically requires recursive CTEs or window functions with careful gap detection. Spark handles it as: sort by key + start time within each partition, then merge sequentially. Cross-partition intervals (spanning partition boundaries) require a second pass. In practice, partitioning by the entity key (user_id, device_id) ensures that all intervals for one entity land on the same partition, eliminating the boundary problem.
```

### 057_insert_interval.md
```markdown
## At Scale

Single-pass merge is O(n) for a sorted list. Binary search to find the insertion point makes it O(log n + merge cost). At scale, the real question is the data structure: a sorted list with O(n) insert/merge is fine for small interval sets but slow for large ones. An interval tree provides O(log n + k) query and O(log n) insert, where k is the number of overlapping intervals. Databases use B-tree indexes on interval endpoints to efficiently find overlapping ranges. In a streaming context, inserting intervals into a maintained sorted structure is the core of real-time session tracking and time-based windowing.
```

### 435_non_overlapping_intervals.md
```markdown
## At Scale

Sort by end time + greedy selection: O(n log n). Memory is O(1) extra (sort in-place, count removals). For 10M intervals, this takes ~3 seconds. The greedy approach (keep the interval that ends earliest) is provably optimal. At scale, "find the maximum non-overlapping set" is a resource scheduling problem: maximize utilization without conflicts. In job scheduling, this determines the maximum number of non-conflicting tasks. In data pipelines, this resolves write conflicts when multiple processes target the same time range. The greedy algorithm's simplicity makes it easy to implement in SQL using window functions: sort by end time, then filter rows where start >= previous selected end.
```

### 986_interval_list_intersections.md
```markdown
## At Scale

Two-pointer merge of two sorted interval lists: O(n + m) time, O(1) extra memory. For two lists of 10M intervals each, this takes ~1 second. The output can be as large as n + m. At scale, interval intersection is the algorithmic basis of time-range joins: "for each user session, find all events that occurred during that session." This is an O(n + m) merge join on sorted intervals, but SQL engines often can't optimize it this way (they use nested loops or hash joins with range conditions). Implementing the two-pointer merge in a UDF or in application code can be orders of magnitude faster than the SQL equivalent for large datasets.
```

## Task 3: Enrich Interview Tips with Evaluator Framing

### 252 (Meeting Rooms):
```markdown
**What the interviewer evaluates:** This is a warm-up. Clean sort + scan is expected quickly. The key insight is sorting by start time and checking adjacent pairs. An interviewer may ask this as a lead-in to Meeting Rooms II.
```

### 253 (Meeting Rooms II):
```markdown
**What the interviewer evaluates:** The heap approach tests data structure selection. The sweep line approach tests event-based thinking. Both are valid. Mentioning that this is how concurrent usage is measured in production (BigQuery slot monitoring, database connection pooling) shows systems awareness. The follow-up "what if meetings can be updated?" tests whether you can handle dynamic intervals.
```

### 056 (Merge Intervals):
```markdown
**What the interviewer evaluates:** Sort + merge is the expected approach. Edge cases (touching intervals [1,2] and [2,3] - do they merge?) test attention to detail. The real differentiator is discussing why this is hard in SQL and how partitioning by entity key avoids cross-partition issues.
```

### 057 (Insert Interval):
```markdown
**What the interviewer evaluates:** The three-phase approach (before, overlap, after) tests clear decomposition. Getting the merge condition right (start <= existing_end AND end >= existing_start) is where bugs occur. Mentioning interval trees for the general case shows algorithmic breadth.
```

### 435 (Non-overlapping Intervals):
```markdown
**What the interviewer evaluates:** The greedy choice (sort by end time, keep earliest-ending interval) must be explained and justified. "Why end time, not start time?" tests proof intuition. The connection to activity selection and job scheduling shows you recognize the broader problem class.
```

### 986 (Interval Intersections):
```markdown
**What the interviewer evaluates:** The two-pointer approach on two sorted lists tests merge logic. Deciding which pointer to advance (the one with the earlier end time) is the key insight. Clean implementation without edge case bugs shows precision. Mentioning time-range joins as the production equivalent connects this to real work.
```

## Task 4: Glossary Updates

Add to WORKING_GLOSSARY.md:

- **sweep line**: Algorithm technique that processes events (interval starts/ends) in sorted order, maintaining a running state. Converts 2D interval problems into 1D event processing.
- **interval tree**: Tree data structure for storing intervals with O(log n + k) query for finding all intervals overlapping a point or range. Used in databases for range index operations.
- **range join**: Join between two tables based on overlapping ranges (e.g., WHERE a.start < b.end AND a.end > b.start). Poorly optimized by most SQL engines without explicit indexing or binning.
- **activity selection**: Classic greedy algorithm for selecting the maximum number of non-overlapping activities. Sort by end time, greedily select.

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== At Scale sections ==="
for f in patterns/07_intervals/problems/*.md; do
    name=$(basename "$f")
    has_scale=$(grep -q "## At Scale" "$f" && echo "Y" || echo "N")
    echo "  $name: At Scale=$has_scale"
done

echo ""
echo "=== README enriched ==="
grep -q "Scale characteristics" patterns/07_intervals/README.md && echo "✅" || echo "❌"

echo ""
echo "=== Evaluator framing ==="
for f in patterns/07_intervals/problems/*.md; do
    has_eval=$(grep -q "interviewer evaluates" "$f" && echo "Y" || echo "N")
    echo "  $(basename $f): evaluator=$has_eval"
done

echo ""
echo "=== Style + tests ==="
grep -rn "—" patterns/07_intervals/ --include="*.md" && echo "❌" || echo "✅ No em dashes"
uv run pytest patterns/07_intervals/ --tb=short -q 2>&1 | tail -3
```
