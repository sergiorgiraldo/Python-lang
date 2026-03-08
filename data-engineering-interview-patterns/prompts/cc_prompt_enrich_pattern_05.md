# CC Prompt: Enrich Pattern 05 (Heap/Priority Queue) to Principal Level

## Context

Pattern 05 has 6 problems and 4 DE scenarios. Enrichment adds principal-level depth to .md files only.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- NO Oxford commas, NO em dashes, NO exclamation points
- Do NOT modify any .py files
- Only ADD content to .md files
- 3-8 sentences per "At Scale" section

---

## Task 1: Enrich README.md Trade-offs Section

In `patterns/05_heap_priority_queue/README.md`, find `## Trade-offs` and ADD:

```markdown
### Scale characteristics

A min-heap of k elements uses O(k) memory and O(log k) per insert/extract. For top-k problems, k is usually small (top 10, top 100), so heap operations are essentially O(1) in practice.

| Operation | Full sort | Heap (size k) | Savings at n=1B, k=100 |
|---|---|---|---|
| Top-k selection | O(n log n) | O(n log k) | ~3x faster (log 100 vs log 1B) |
| Memory | O(n) | O(k) | 10M x less memory |
| Streaming capable | No (need all data) | Yes (process one at a time) | Fundamental difference |

The streaming property is the heap's killer feature at scale. A heap of size k can process an infinite stream and always hold the current top-k. A sort requires all data in memory first.

**Distributed equivalent:** Top-k across distributed partitions: each partition maintains a local heap of size k, then merge the partition heaps (at most P*k elements, where P is partition count) with a final heap of size k. MapReduce top-k follows this pattern. In Spark: `df.orderBy(desc("count")).limit(k)` uses a heap internally per partition, then merges.

**Merge k sorted streams:** The heap enables efficient k-way merge in O(n log k) where n is total elements and k is the number of streams. This is the core of external merge sort: merge k sorted runs from disk by maintaining a heap of the smallest element from each run. It's also how Spark merges sorted partitions in a sort-merge join.

### SQL equivalent

`ORDER BY metric DESC LIMIT k` is the SQL top-k pattern. Internally, the query engine uses a heap to avoid fully sorting the data. Window functions like `RANK() OVER (ORDER BY metric DESC)` with a filter on rank <= k achieve the same result. The SQL section's window functions and aggregation subsections cover these patterns. APPROX_TOP_COUNT in BigQuery uses probabilistic structures (similar to Pattern 11) for approximate top-k on very large datasets.
```

## Task 2: Add "At Scale" Section to Each Problem .md

### 703_kth_largest_stream.md (or actual filename)
```markdown
## At Scale

A min-heap of size k processes an infinite stream using O(k) memory. For k=100, that's a few KB regardless of whether 1M or 1B elements flow through. This is the canonical streaming top-k structure. In production, this powers real-time leaderboards, "trending now" features and anomaly detection thresholds. Kafka Streams and Flink both use heap-based structures for their top-k operators. The key limitation: the heap gives you the kth largest, but not the exact rank of arbitrary elements. For that, you need an order-statistic tree or approximate rank structures.
```

### 1046_last_stone_weight.md
```markdown
## At Scale

The max-heap simulation runs O(n log n) in total: n elements, each extracted and potentially re-inserted at O(log n). For n=10M, this takes a few seconds. Memory is O(n) for the heap. The simulation doesn't parallelize well because each step depends on the previous result. At scale, the interesting question is whether you need the exact final value or can approximate. For resource allocation problems (where stones represent competing demands), a greedy approximation may suffice. The interviewer may use this as a warm-up before harder heap problems.
```

### 215_kth_largest.md
```markdown
## At Scale

Quickselect is O(n) average but O(n^2) worst case. The heap approach is O(n log k) with no worst case. For n=1B and k=100, quickselect does ~1B comparisons, the heap does ~1B * 7 = 7B comparisons. Quickselect is faster in practice but has unpredictable performance. In distributed settings, finding the kth largest across partitions uses a multi-round approach: each partition finds local candidates, then merge and refine. Spark's `percentile_approx` uses t-digest (a probabilistic structure) for approximate quantiles on distributed data. For exact results, you need a distributed selection algorithm that narrows the candidate range across rounds.
```

### 347_top_k_frequent.md
```markdown
## At Scale

Phase 1 (counting) stores one entry per unique value: O(d) where d is the number of distinct values. For 10M events with 100K unique values, that's ~20MB. For 1B events with 10M unique values, that's ~2GB. Phase 2 (top-k extraction) uses a heap of size k: negligible. The bottleneck at scale is the counting phase. In Spark, this is `groupBy("value").count().orderBy(desc("count")).limit(k)`. The shuffle for the groupBy is the expensive operation. If counting is approximate, Count-Min Sketch (Pattern 11) gives O(1) memory counting, and the heap still extracts top-k. This exact + approximate tradeoff is a principal-level discussion point.
```

### 023_merge_k_sorted.md
```markdown
## At Scale

The k-way merge with a heap is O(n log k) where n is total elements across all lists. This is the core algorithm for external merge sort and sort-merge joins in databases. Merging 1000 sorted files of 1GB each (1TB total) requires a heap of size 1000 and sequential reads from each file. Total comparisons: 1B * log(1000) ≈ 10B. The heap is tiny (1000 entries) but I/O is the bottleneck: reading 1TB sequentially. The practical optimization is to use large read buffers per file to minimize disk seeks. In Spark, sort-merge joins merge sorted partitions using exactly this algorithm. Understanding k-way merge is essential for debugging slow sort-merge operations.
```

### 295_find_median_stream.md
```markdown
## At Scale

Two heaps (max-heap for lower half, min-heap for upper half) give O(log n) insert and O(1) median. Memory is O(n) - every element is stored. For 1B elements, that's ~8GB. The streaming property is essential: you get the running median without sorting. At scale, exact median in a distributed setting is expensive: you need the element at position n/2 across all partitions, which requires a global sort or a multi-round selection algorithm. Approximate median is much cheaper: t-digest and GK-sketch provide epsilon-approximate quantiles in O(1/epsilon) memory. BigQuery's APPROX_QUANTILES and Spark's percentile_approx use these structures. In interviews, mentioning the exact vs approximate tradeoff for streaming median is a strong principal-level signal.
```

## Task 3: Enrich Interview Tips with Evaluator Framing

### 703 (Kth Largest Stream):
```markdown
**What the interviewer evaluates:** Understanding that a min-heap (not max-heap) of size k gives the kth largest is the core insight. Many candidates reach for a max-heap and process k elements, which is O(n log n). The min-heap approach is O(n log k). Explaining the streaming property (can handle infinite input in bounded memory) shows you think beyond batch processing.
```

### 1046 (Last Stone Weight):
```markdown
**What the interviewer evaluates:** This is a straightforward heap simulation. The interviewer expects quick, clean execution. The real test is whether you reach for a max-heap naturally (Python requires negation for max-heap behavior) and handle the re-insertion logic correctly. Finishing fast opens time for harder problems.
```

### 215 (Kth Largest):
```markdown
**What the interviewer evaluates:** This tests whether you know multiple selection algorithms. Quickselect (O(n) average) vs heap (O(n log k)) vs full sort (O(n log n)). Discussing the time-space-predictability tradeoff shows mature engineering judgment. The follow-up "what about distributed data?" tests system design thinking.
```

### 347 (Top K Frequent):
```markdown
**What the interviewer evaluates:** The two-phase approach (count then select) tests decomposition. Starting with the heap approach, then mentioning bucket sort as an O(n) alternative shows optimization awareness. Connecting to SQL's GROUP BY + ORDER BY + LIMIT shows you understand how query engines solve this same problem.
```

### 023 (Merge K Sorted):
```markdown
**What the interviewer evaluates:** k-way merge is a fundamental operation. The heap provides O(log k) per element extraction, making the total O(n log k). Understanding that this is the basis of external merge sort and sort-merge joins is the principal-level differentiator. The interviewer may ask "what if k is very large?" (answer: multi-level merge - merge groups of k' lists, then merge the results).
```

### 295 (Find Median Stream):
```markdown
**What the interviewer evaluates:** The two-heap data structure is non-obvious and tests design creativity. Maintaining the balance invariant (size difference <= 1) at each insert is where bugs occur. The follow-up "what about distributed streams?" is a principal-level question. Mentioning t-digest or APPROX_QUANTILES shows production awareness.
```

## Task 4: Glossary Updates

Add to WORKING_GLOSSARY.md:

- **k-way merge**: Merging k sorted sequences into one sorted output using a heap of size k. O(n log k) total where n is the combined element count. Core of external sort and sort-merge joins.
- **t-digest**: Probabilistic data structure for approximate quantile estimation. Provides bounded-error quantile queries with compact memory. Used in Spark, Elasticsearch and BigQuery.
- **order-statistic tree**: Augmented balanced BST that supports O(log n) rank queries (find kth element, find rank of element). Not available in Python's standard library.
- **fan-out (top-k)**: Distributed top-k strategy where each partition computes local top-k, then a coordinator merges and selects the global top-k from at most P*k candidates.

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== At Scale sections ==="
for f in patterns/05_heap_priority_queue/problems/*.md; do
    name=$(basename "$f")
    has_scale=$(grep -q "## At Scale" "$f" && echo "Y" || echo "N")
    echo "  $name: At Scale=$has_scale"
done

echo ""
echo "=== README enriched ==="
grep -q "Scale characteristics" patterns/05_heap_priority_queue/README.md && echo "✅" || echo "❌"

echo ""
echo "=== Evaluator framing ==="
for f in patterns/05_heap_priority_queue/problems/*.md; do
    has_eval=$(grep -q "interviewer evaluates" "$f" && echo "Y" || echo "N")
    echo "  $(basename $f): evaluator=$has_eval"
done

echo ""
echo "=== Style + tests ==="
grep -rn "—" patterns/05_heap_priority_queue/ --include="*.md" && echo "❌" || echo "✅ No em dashes"
uv run pytest patterns/05_heap_priority_queue/ --tb=short -q 2>&1 | tail -3
```
