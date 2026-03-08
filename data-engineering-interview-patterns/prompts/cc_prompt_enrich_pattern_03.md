# CC Prompt: Enrich Pattern 03 (Binary Search) to Principal Level

## Context

Pattern 03 has 8 problems and 4 DE scenarios. This enrichment adds principal-level depth to .md files only.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- NO Oxford commas, NO em dashes, NO exclamation points
- Do NOT modify any .py files
- Only ADD content to .md files
- 3-8 sentences per "At Scale" section

---

## Task 1: Enrich README.md Trade-offs Section

In `patterns/03_binary_search/README.md`, find `## Trade-offs` and ADD:

```markdown
### Scale characteristics

Binary search eliminates half the data with each comparison. The number of comparisons is log2(n):

| n | Comparisons | Time at 100ns/comparison |
|---|---|---|
| 1K | 10 | 1 microsecond |
| 1M | 20 | 2 microseconds |
| 1B | 30 | 3 microseconds |
| 1T | 40 | 4 microseconds |

This is why binary search is the foundation of database indexing. A B-tree index on 1 trillion rows requires ~40 comparisons per lookup. The practical bottleneck at scale isn't the comparisons - it's disk I/O. Each comparison may require reading a disk page. B-trees optimize for this by having high fan-out (hundreds of keys per node), reducing tree depth to 3-4 levels even for billions of rows.

**Distributed equivalent:** Binary search on partitioned data requires knowing which partition contains the target range. Range-partitioned tables (common in BigQuery, Snowflake, Cassandra) store partition boundaries as metadata. A query first binary-searches the partition metadata to identify the relevant partition, then binary-searches within it. This is a two-level search: O(log P + log N/P) where P is partitions.

**"Binary search the answer" at scale:** Problems like Koko Eating Bananas binary-search over the solution space rather than the data. This pattern appears in distributed systems as capacity planning: "what's the minimum number of workers to process this data in under 1 hour?" Binary search the worker count, simulate the workload for each candidate count.

### SQL equivalent

Binary search maps to index lookups in SQL. A `WHERE id = 42` on an indexed column triggers a B-tree traversal (binary search variant). Range queries like `WHERE created_at BETWEEN '2024-01-01' AND '2024-01-31'` use the index to find the start point, then scan sequentially. Understanding when the optimizer chooses an index scan vs a full table scan is essential for query performance. The SQL section's optimization subsection covers index selection and query plans.
```

## Task 2: Add "At Scale" Section to Each Problem .md

### 704_binary_search.md
```markdown
## At Scale

Binary search on 1B sorted elements takes 30 comparisons. This is negligible. The real cost at scale is getting the data sorted in the first place (O(n log n)) and keeping it sorted as new data arrives (B-tree insert is O(log n) per element). In a database, the sorted data IS the index. Every primary key lookup, every range scan and every merge join relies on binary search internally. At 1T rows with a B-tree index of depth 4, a point lookup touches 4 disk pages. With 4KB pages cached in memory, this takes microseconds.
```

### 035_search_insert.md
```markdown
## At Scale

Finding the insertion position is how B-tree inserts work internally: binary search to the leaf node, insert there. For 1B elements, this takes 30 comparisons. The cost of actually inserting (shifting elements in an array) is O(n), which is why production systems use trees (O(log n) insert) instead of sorted arrays. In data pipelines, "find where this row belongs in the sorted output" is the partitioning step of a sort-merge operation. Range-partitioned tables use this to route rows to the correct partition.
```

### 074_search_2d_matrix.md
```markdown
## At Scale

Treating the 2D matrix as a flat sorted array (row * cols + col) is a conceptual tool. In practice, data stored in row-major order in columnar formats (Parquet, ORC) has different access patterns. Columnar storage is optimized for scanning entire columns, not random row access. Binary search on columnar data is inefficient because each comparison reads from a different row group. This is why columnar databases use min/max statistics per row group (zone maps) for pruning rather than binary search: "this row group's values range from 50-100, so skip it if looking for 42."
```

### 153_find_min_rotated.md
```markdown
## At Scale

Finding the rotation point in a rotated sorted array is a single O(log n) operation. The practical application at scale: finding the partition boundary in range-partitioned data that has been rotated (e.g., time-partitioned data where partitions wrap around). More commonly, the "binary search on a nearly-sorted structure" pattern applies to searching log files that are sorted within segments but segments may be out of order. At 1B elements, the 30-comparison cost is dominated by the cost of loading the relevant cache lines or disk pages.
```

### 033_search_rotated.md
```markdown
## At Scale

Binary search in a rotated sorted array is O(log n) - same as standard binary search. The extra comparison per step (checking which half is sorted) doesn't change the asymptotic complexity. At scale, the important lesson is that binary search works on ANY structure with a monotonic property, not just perfectly sorted arrays. Database indexes handle this with B-tree variants that maintain balance through rotations. Log-structured merge trees (LSM trees, used in Cassandra and RocksDB) maintain multiple sorted runs and binary-search each one separately.
```

### 162_find_peak.md
```markdown
## At Scale

Peak finding in O(log n) works because the problem has a "binary search the answer" structure: the gradient tells you which direction to move. At scale, this pattern appears in optimization and tuning: "find the configuration (batch size, partition count, parallelism) that maximizes throughput." If the performance curve is unimodal (one peak), binary search the parameter space. Ternary search generalizes this to any unimodal function. Distributed hyperparameter tuning (like Spark's ML tuning) uses similar search strategies over the parameter space.
```

### 875_koko_eating_bananas.md
```markdown
## At Scale

"Binary search the answer" is the key pattern here: instead of searching the data, search the solution space. The solution space has a monotonic property (if speed k works, k+1 also works), enabling binary search. At scale, this pattern is everywhere: "what's the minimum number of Spark executors to finish this job in under 1 hour?" Binary search executor count, simulate the workload at each candidate. "What's the minimum batch size for this API that keeps latency under 100ms?" Same structure. The simulation step (checking if a candidate works) is the bottleneck, not the binary search itself.
```

### 981_time_based_kv.md (if it exists)
```markdown
## At Scale

A time-based key-value store is essentially a sorted map per key: given a key and a timestamp, find the most recent value at or before that timestamp. This is binary search on the timestamp list per key. At scale, this is how time-travel queries work in data lakehouses (Delta Lake, Iceberg): each key has a version history sorted by timestamp. A query at timestamp T binary-searches the version list to find the active version. For 1B versions across all keys, the per-key binary search is fast (log of versions per key, typically small), but the key lookup itself needs a hash map or index.
```

## Task 3: Enrich Interview Tips with Evaluator Framing

### 704 (Binary Search):
```markdown
**What the interviewer evaluates:** Clean implementation of binary search (correct boundary handling, no off-by-one errors) is the baseline. The real test is whether you can extend the pattern: "now what if the array is rotated?" or "what if you're searching a function instead of an array?" Your comfort with the basic template determines how quickly you can handle variants.
```

### 035 (Search Insert):
```markdown
**What the interviewer evaluates:** Understanding what the left pointer represents after binary search terminates (the insertion point) shows you understand the algorithm, not just the template. This is often a warm-up - the interviewer expects fast, clean execution and will escalate.
```

### 074 (Search 2D Matrix):
```markdown
**What the interviewer evaluates:** Can you see the flat sorted array within the 2D structure? The index math (row = mid // cols, col = mid % cols) tests whether you think in abstractions. Mentioning row group statistics and zone maps as the production equivalent shows systems awareness.
```

### 153 (Find Min Rotated):
```markdown
**What the interviewer evaluates:** The rotation adds ambiguity to each comparison. You must reason about which half is sorted to decide which way to go. Walking through examples with the interviewer (showing how the comparison determines the search direction) demonstrates careful analysis.
```

### 033 (Search Rotated):
```markdown
**What the interviewer evaluates:** This combines the rotation handling from 153 with the target search from 704. Getting both right under pressure tests composure and systematic thinking. Off-by-one errors are common - using `<=` vs `<` in the boundary check is where most bugs hide.
```

### 162 (Find Peak):
```markdown
**What the interviewer evaluates:** The gradient-based binary search tests whether you can generalize binary search beyond sorted arrays. If you only know the "sorted array" version, you'll struggle here. The interviewer wants to see you reason about the binary search invariant: "why can I discard this half?"
```

### 875 (Koko Eating Bananas):
```markdown
**What the interviewer evaluates:** "Binary search the answer" is a more advanced pattern than "binary search the array." Recognizing the monotonic property in the solution space (not the data) is the insight. The feasibility check function is where most implementation bugs occur. At principal level, connecting this to capacity planning and resource estimation is a differentiator.
```

### 981 (Time Based KV):
```markdown
**What the interviewer evaluates:** This is a design + algorithm hybrid. The data structure choice (dict of sorted lists) tests design sense. The binary search within each key's history tests implementation. The follow-up "what about concurrent writes?" or "what about TTL/expiration?" pivots to system design. Mentioning time-travel queries in Delta Lake or Iceberg connects to production systems.
```

## Task 4: Glossary Updates

Add to WORKING_GLOSSARY.md:

- **B-tree**: Self-balancing tree with high fan-out, used for database indexes. Each node holds many keys, minimizing disk reads. Lookup, insert, delete are all O(log n).
- **zone maps / min-max statistics**: Metadata stored per data file or row group recording the minimum and maximum values. Enables query engines to skip files that can't contain matching rows without reading them.
- **LSM tree**: Log-structured merge tree. Write-optimized data structure that batches writes into sorted runs and periodically merges them. Used in Cassandra, RocksDB, LevelDB.
- **range partitioning**: Distributing data across partitions by value range (e.g., dates, ID ranges). Enables partition pruning on range queries.
- **binary search the answer**: Technique where binary search is applied to the solution space rather than the data. Requires a monotonic feasibility function.

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== At Scale sections ==="
for f in patterns/03_binary_search/problems/*.md; do
    name=$(basename "$f")
    has_scale=$(grep -q "## At Scale" "$f" && echo "Y" || echo "N")
    echo "  $name: At Scale=$has_scale"
done

echo ""
echo "=== README enriched ==="
grep -q "Scale characteristics" patterns/03_binary_search/README.md && echo "✅" || echo "❌"
grep -q "SQL equivalent" patterns/03_binary_search/README.md && echo "✅" || echo "❌"

echo ""
echo "=== Evaluator framing ==="
for f in patterns/03_binary_search/problems/*.md; do
    has_eval=$(grep -q "interviewer evaluates" "$f" && echo "Y" || echo "N")
    echo "  $(basename $f): evaluator=$has_eval"
done

echo ""
echo "=== Style + tests ==="
grep -rn "—" patterns/03_binary_search/ --include="*.md" && echo "❌ Em dashes" || echo "✅ No em dashes"
uv run pytest patterns/03_binary_search/ --tb=short -q 2>&1 | tail -3
```
