# CC Prompt: Enrich Pattern 01 (Hash Map) to Principal Level

## Context

Pattern 01 is complete with 10 problems, 4 DE scenarios and 1142 tests passing. This enrichment adds principal-level depth without changing any existing code or tests. We're adding content to .md files only.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- NO Oxford commas, NO em dashes, NO exclamation points
- Do NOT modify any .py files or test files
- Do NOT remove any existing content - only ADD sections
- Keep additions concise. 3-8 sentences per "At Scale" section. Not essays.
- Use specific numbers (bytes, rows, seconds) not vague language

---

## Task 1: Enrich README.md Trade-offs Section

In `patterns/01_hash_map/README.md`, find the `## Trade-offs` section. ADD the following content to the end of that section (after whatever currently exists):

```markdown
### Scale characteristics

A Python dict storing n integer keys uses roughly 80-120 bytes per entry (key object + hash + pointer overhead). For reference:

| n | Approximate memory | Fits in a single machine? |
|---|---|---|
| 100K | ~10 MB | Easily |
| 10M | ~1 GB | Yes |
| 100M | ~10 GB | Tight (typical worker has 8-16 GB) |
| 1B | ~100 GB | No - need distributed approach |

**Distributed equivalent:** Hash maps become hash-partitioned joins in Spark/Flink. The key is hashed to determine which partition (worker) owns it. This is a shuffle operation - expensive because it moves data across the network. Broadcast joins avoid the shuffle by sending the smaller table to every worker, but only work when one side fits in memory.

**Key skew:** If one key appears far more often than others (e.g., user_id = "anonymous" accounts for 30% of events), the partition handling that key gets 30% of the work while others sit idle. Solutions: salting the key (appending a random suffix, joining on both original and salted key), pre-aggregating the hot key separately, or using a broadcast join for the skewed portion.

### SQL equivalent

The hash map pattern maps directly to hash joins in SQL engines. When you write `SELECT * FROM orders JOIN customers ON orders.customer_id = customers.id`, the engine builds a hash table from the smaller table and probes it with the larger table. The SQL section's joins subsection covers join strategies including when engines choose hash joins vs sort-merge joins.
```

## Task 2: Add "At Scale" Section to Each Problem .md

For each problem .md file in `patterns/01_hash_map/problems/`, add an `## At Scale` section AFTER the existing `## DE Application` section (and before `## Related Problems` if it exists). If a problem doesn't have `## DE Application`, add it before `## Related Problems`.

The content must be specific to each problem. Here's what to add:

### 001_two_sum.md
```markdown
## At Scale

The hash map approach uses O(n) memory. For 10M integer pairs, that's roughly 800MB - fits on one machine. For 1B pairs, it's ~80GB and you need a distributed approach: hash-partition both the array and the target complements by key, then each partition independently finds local pairs. In Spark, this is a self-join with a hash partitioner. Watch for skew: if many elements share the same complement, one partition does disproportionate work. An interviewer asking "what if the array doesn't fit in memory?" wants to hear you say "external hashing" or "partition and distribute."
```

### 217_contains_duplicate.md
```markdown
## At Scale

The hash set approach stores every unique element. For 10M integers, that's ~400MB. For data with high cardinality (many unique values), memory grows linearly. If you only need to know WHETHER duplicates exist (not WHICH ones), a Bloom filter (Pattern 11) gives a probabilistic answer in fixed memory. For exact dedup at scale, sort the data externally and check adjacent elements - O(n log n) time but O(1) memory beyond the sort buffer. In production pipelines, dedup is often done with a GROUP BY in SQL rather than in-memory sets.
```

### 242_valid_anagram.md
```markdown
## At Scale

Character frequency counting uses O(1) space (26 letters for lowercase English, 128 for ASCII, ~150K for full Unicode). This is one of the rare problems where the hash map doesn't grow with input size. At 1B-character strings, the bottleneck is I/O (reading the string) not memory. The sorted approach creates a copy of each string - for very long strings, that's double the memory. In a distributed setting, frequency counting is embarrassingly parallel: each worker counts locally, then merge the frequency maps (which are tiny).
```

### 049_group_anagrams.md
```markdown
## At Scale

The hash map stores every string, so memory scales with total input size. For 10M strings averaging 10 characters, that's roughly 200MB for the strings plus 400MB for the dict structure. The sorted-key approach creates a sorted copy of each string - for n strings of average length k, that's O(n * k * log k) time. At scale, this is a GROUP BY in Spark/SQL: `GROUP BY sorted_characters`. The shuffle groups strings with the same sorted key onto the same partition. Skew risk: if one anagram group is much larger than others (common in natural language - "aet" covers "eat", "tea", "ate"), that partition gets disproportionate work.
```

### 347_top_k_frequent.md
```markdown
## At Scale

The Counter stores one entry per unique element. For high-cardinality data (10M unique values), that's ~1GB. The heap holds only k elements - negligible. For very large datasets, this decomposes naturally: count frequencies per partition (map phase), merge frequency maps, then extract top-k (reduce phase). This is essentially what `GROUP BY value ORDER BY count DESC LIMIT k` does in SQL. Approximate alternatives: Count-Min Sketch (Pattern 11) for frequency estimation in fixed memory, or sampling. In Spark: `df.groupBy("value").count().orderBy(desc("count")).limit(k)`.
```

### 128_longest_consecutive_sequence.md
```markdown
## At Scale

The hash set stores all n elements. For 10M integers, that's ~400MB. The algorithm itself is O(n) with excellent cache behavior (hash lookups are random access, but each element is processed at most twice). At 1B elements, the set doesn't fit in memory. Distributed approach: range-partition the data so consecutive numbers land on the same partition. Each partition finds local consecutive sequences, then merge sequences that span partition boundaries. This is trickier than it sounds - the boundary merging requires a second pass. In practice, sort-based approaches are often preferred at scale because they're easier to distribute and sort is a well-optimized primitive in every distributed framework.
```

### 560_subarray_sum.md
```markdown
## At Scale

The prefix sum hash map stores at most n entries (one per prefix sum). For 10M elements, that's ~800MB. This problem is inherently sequential - each prefix sum depends on all previous elements - so it doesn't parallelize trivially. For very large arrays, you can split into chunks: compute prefix sums within each chunk, then adjust cross-chunk sums at boundaries. In a streaming context, the hash map grows unboundedly (every new prefix sum is stored). If you only need recent subarrays, combine with a sliding window to bound memory.
```

### 146_lru_cache.md
```markdown
## At Scale

The LRU cache stores at most `capacity` entries. This is bounded by design - the whole point is fixed memory. At scale, the question shifts from implementation to architecture: a single-machine LRU cache handles ~1M entries comfortably. For distributed caching, you shard by key across machines (consistent hashing for rebalancing) and accept that cross-shard operations like "evict globally least-recent" are expensive. Redis and Memcached implement this pattern at production scale. An interviewer asking about LRU at scale wants to hear about cache invalidation, consistency and eviction policies - not the linked-list implementation.
```

### 380_insert_delete_getrandom.md
```markdown
## At Scale

The array + hash map combination uses O(n) memory for n elements. The GetRandom operation is O(1) because arrays support random index access. At scale, uniform random sampling from a distributed dataset is harder than it sounds: you can't just pick a random index if the data is spread across 1000 partitions. Reservoir sampling handles this - maintain a sample of size k, and for each new element decide probabilistically whether to include it. Spark's `df.sample(fraction)` uses a similar approach. The insert/delete/getRandom combination appears in load balancers (random backend selection) and A/B test assignment.
```

### 355_design_twitter.md
```markdown
## At Scale

This is a system design problem disguised as a data structures problem. The in-memory approach works for the LeetCode constraints but breaks immediately at Twitter's actual scale (500M tweets/day). The real trade-off is fan-out-on-write (precompute each user's feed when a tweet is posted, like we do here with the merge) vs fan-out-on-read (compute the feed on demand). Fan-out-on-write uses more storage and write amplification but faster reads. Fan-out-on-read saves storage but every feed request is expensive. Hybrid approaches handle both: fan-out-on-write for normal users, fan-out-on-read for celebrities (whose tweets would fan out to millions). An interviewer using this problem at principal level will pivot to the system design trade-offs.
```

## Task 3: Enrich Interview Tips with Evaluator Framing

For each problem .md, find the `## Interview Tips` section. ADD a paragraph after the existing content (keep the existing quote and tips):

Add this to ALL 10 problem files, customized per problem:

**Pattern for the addition (adapt the specifics per problem):**
```markdown
**What the interviewer evaluates at each stage:** The brute force tests basic problem-solving ability. The hash map optimization tests pattern recognition - can you identify that O(n) lookup eliminates the inner loop? Follow-up questions about memory, scale or streaming test whether you think like an engineer or a puzzle solver. At principal level, volunteering the scale discussion before being asked is a strong signal.
```

Customize the "what the interviewer evaluates" paragraph for each problem based on what its specific approaches teach. For example:
- Two Sum: pattern recognition (hash map eliminates nested loop)
- LRU Cache: data structure design (combining two structures)
- Design Twitter: system design awareness (fan-out trade-offs)
- Contains Duplicate: knowing when a simpler tool suffices (set vs map)

## Task 4: Glossary Updates

Read the current glossary at `/mnt/project/WORKING_GLOSSARY.md`. Create an UPDATED version at `~/dev/projects/data-engineering-interview-patterns/WORKING_GLOSSARY.md` that adds these terms if they don't already exist:

- **broadcast join**: Distributed join strategy where the smaller table is copied to every worker, avoiding a shuffle. Works when one side fits in worker memory.
- **hash-partitioned join**: Distributed join where both tables are shuffled by join key so matching keys land on the same worker.
- **key skew**: Uneven distribution of values in a join or group-by key, causing one partition to process disproportionately more data.
- **salting**: Technique to handle key skew by appending random values to hot keys, spreading their data across multiple partitions.
- **fan-out-on-write**: Precomputing derived data (like feeds) at write time. Higher write cost, lower read cost.
- **fan-out-on-read**: Computing derived data at read time. Lower write cost, higher read cost.
- **external hashing**: Hash-based processing for datasets that don't fit in memory. Partition data to disk by hash, then process each partition in memory.
- **reservoir sampling**: Algorithm for uniform random sampling from a stream of unknown size in O(k) memory.

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== At Scale sections added ==="
for f in patterns/01_hash_map/problems/*.md; do
    name=$(basename "$f")
    has_scale=$(grep -q "## At Scale" "$f" && echo "Y" || echo "N")
    echo "  $name: At Scale=$has_scale"
done

echo ""
echo "=== README trade-offs enriched ==="
grep -q "Scale characteristics" patterns/01_hash_map/README.md && echo "✅ Scale characteristics added" || echo "❌ Missing"
grep -q "SQL equivalent" patterns/01_hash_map/README.md && echo "✅ SQL equivalent added" || echo "❌ Missing"

echo ""
echo "=== Interview evaluator framing ==="
for f in patterns/01_hash_map/problems/*.md; do
    name=$(basename "$f")
    has_eval=$(grep -q "interviewer evaluates" "$f" && echo "Y" || echo "N")
    echo "  $name: evaluator framing=$has_eval"
done

echo ""
echo "=== Style check ==="
grep -rn "—" patterns/01_hash_map/ --include="*.md" && echo "❌ Em dashes" || echo "✅ No em dashes"

echo ""
echo "=== Tests still pass ==="
uv run pytest patterns/01_hash_map/ --tb=short -q 2>&1 | tail -3

echo ""
echo "=== Glossary updated ==="
for term in "broadcast join" "key skew" "salting" "fan-out-on-write" "reservoir sampling"; do
    grep -qi "$term" WORKING_GLOSSARY.md && echo "✅ $term" || echo "❌ $term missing"
done
```
