# CC Prompt: Enrich Pattern 11 (Probabilistic Structures) to Principal Level

## Context

Pattern 11 has 3 implementations (Bloom Filter, HyperLogLog, Count-Min Sketch) and 4 DE scenarios. This pattern already has strong scale content (memory budget analysis scenario). The enrichment adds interviewer framing, forward references and fills any gaps.

Work in `~/dev/projects/data-engineering-interview-patterns/`.

## Rules

- NO Oxford commas, NO em dashes, NO exclamation points
- Do NOT modify any .py files. Only ADD content to .md files.
- 3-8 sentences per "At Scale" section

---

## Task 1: Enrich README.md Trade-offs Section

In `patterns/11_probabilistic_structures/README.md`, find `## Trade-offs` and ADD (if not already covered - check first and skip any content that duplicates what's there):

```markdown
### Production deployment context

These structures aren't just interview topics. They run in production at every major tech company:

| Structure | Production system | What it does |
|---|---|---|
| Bloom filter | Cassandra, HBase, LevelDB | Avoids disk reads for keys that don't exist |
| HyperLogLog | Redis (PFCOUNT), BigQuery (APPROX_COUNT_DISTINCT), Snowflake | Approximate cardinality in seconds vs minutes |
| Count-Min Sketch | Spark, network monitoring tools | Frequency estimation for hot-key detection |

**When the interviewer asks about these:** At principal level, you won't be asked to implement these from scratch. You'll be asked: "Your pipeline processes 10B events/day. How would you count unique users?" The expected answer isn't "build a hash set" (that's 80GB). It's "use HyperLogLog with 16KB giving ~0.8% error, which is fine for a dashboard." Knowing WHEN to use approximate structures and what error rate is acceptable for the use case is the principal-level skill.

**The exact-vs-approximate decision framework:**
- Dashboard metrics and monitoring: approximate is fine (HLL, CMS)
- Financial reporting and billing: exact required (hash set, GROUP BY)
- Data quality checks (duplicate detection): Bloom filter for fast pre-screening, exact verification for positives
- Real-time alerting thresholds: approximate is fine if you build in margin

### SQL equivalent

BigQuery's APPROX_COUNT_DISTINCT uses HyperLogLog internally. Snowflake's APPROXIMATE_COUNT_DISTINCT does the same. These are 10-100x faster than exact COUNT(DISTINCT) on large tables because they avoid the full sort or hash aggregation. Spark's approxQuantile uses Count-Min Sketch variants. The SQL section's optimization subsection covers when to use approximate functions and how to reason about acceptable error rates.
```

## Task 2: Add "At Scale" Section to Each Problem/Implementation .md

Find the .md files for the three implementations. They may be in problems/ or at the top level of the pattern directory. Add the "At Scale" section to whichever .md files exist.

### bloom_filter.md (or whatever the actual filename is)
```markdown
## At Scale

A Bloom filter for 1B elements at 1% false positive rate uses ~1.2GB. For 0.1% false positive rate, ~1.8GB. This is fixed regardless of element size - a Bloom filter for 1B URLs (averaging 100 bytes each) uses the same 1.2GB as for 1B integers. The hash computations are the bottleneck: for k=7 hash functions and 1B lookups, that's 7B hash operations (~10 seconds). In production, Bloom filters are used as gatekeepers: Cassandra checks a Bloom filter before reading from disk. If the filter says "not present," the disk read is skipped entirely. This saves ~90% of disk reads for non-existent keys. The false positive rate means ~1% of "not found" queries still hit disk unnecessarily - an acceptable tradeoff. For distributed systems, each partition maintains its own Bloom filter. Merging Bloom filters across partitions is possible (bitwise OR) but increases the false positive rate.
```

### hyperloglog.md
```markdown
## At Scale

HyperLogLog with 2^14 registers (16KB) estimates cardinality of billions of elements with ~0.8% standard error. The estimation is independent of the actual cardinality - counting 1M unique users and 1B unique users uses the same 16KB. This is why every major analytics database uses HLL for COUNT(DISTINCT). The practical consideration at scale: HLL registers are mergeable. You can compute per-partition HLL sketches in parallel and merge them for a global estimate. This is how distributed COUNT(DISTINCT) works in BigQuery, Snowflake and Presto. The merge operation is simple (take the max register value per position) and the merged result has the same error bound as if computed centrally. For time-series cardinality (unique users per day over 365 days), store one HLL sketch per day. Any time range query merges the relevant daily sketches.
```

### count_min_sketch.md
```markdown
## At Scale

A Count-Min Sketch with width 2000 and depth 5 uses ~40KB and estimates frequencies with error proportional to total count / width. For 1B events, the maximum overestimate per element is ~500K (0.05% of total). This is compact enough to maintain per-partition in a streaming system. In production, CMS is used for finding heavy hitters (elements exceeding a frequency threshold) without storing all frequencies. Network monitoring uses CMS to detect high-traffic IP addresses. In data pipelines, CMS detects hot keys before a shuffle: if one key accounts for 10% of traffic, the pipeline can salt that key to avoid partition skew. The "count then check" pattern (CMS for fast frequency approximation, exact counting only for elements above the threshold) reduces memory from O(unique elements) to O(sketch size).
```

## Task 3: Enrich Interview Tips with Evaluator Framing

### Bloom Filter:
```markdown
**What the interviewer evaluates:** Understanding false positives (possible) vs false negatives (impossible) is the baseline. Explaining the math (optimal k, bit array sizing for target FPR) shows depth. The real principal-level signal: knowing where Bloom filters are used in production (Cassandra, HBase, LSM tree compaction) and being able to calculate the memory/error tradeoff for a given use case. "For 100M keys at 1% FPR, I need ~120MB" is the kind of back-of-envelope calculation interviewers want to hear.
```

### HyperLogLog:
```markdown
**What the interviewer evaluates:** You don't need to derive the math. You need to know: fixed memory (~16KB), ~0.8% error, mergeable across partitions. The killer answer in an interview: "I'd use APPROX_COUNT_DISTINCT in BigQuery, which uses HLL internally. For a dashboard showing daily unique users, 0.8% error is invisible. For billing where we charge per unique user, I'd use exact COUNT(DISTINCT) and accept the higher cost." This exact-vs-approximate decision framework is what the interviewer is really testing.
```

### Count-Min Sketch:
```markdown
**What the interviewer evaluates:** CMS is less commonly asked about directly. It usually comes up in context: "how would you detect hot keys in a data pipeline?" or "how would you find the top-10 most frequent events in a stream without storing all frequencies?" Knowing that CMS provides frequency upper bounds (never underestimates) and that it pairs with a heap for streaming top-k shows you've thought about production applications.
```

## Task 4: Glossary Updates

Add to WORKING_GLOSSARY.md:

- **heavy hitter**: An element whose frequency exceeds a threshold (e.g., >1% of total count). Detecting heavy hitters in a stream without storing all frequencies uses probabilistic structures.
- **sketch mergeability**: Property of probabilistic data structures where sketches computed on partitions can be combined to produce a sketch equivalent to one computed on the full dataset. HLL, CMS and Bloom filters are all mergeable.
- **back-of-envelope calculation**: Quick estimation using rough numbers to determine feasibility. Example: "1B users * 8 bytes per HLL register position = 8GB for exact, or 16KB for approximate." Essential skill for system design interviews.

## Verification

```bash
cd ~/dev/projects/data-engineering-interview-patterns

echo "=== At Scale sections ==="
for f in $(find patterns/11_probabilistic_structures/ -name "*.md" -not -name "README.md" | sort); do
    name=$(basename "$f")
    has_scale=$(grep -q "## At Scale" "$f" && echo "Y" || echo "N")
    echo "  $name: At Scale=$has_scale"
done

echo ""
echo "=== README enriched ==="
grep -q "Production deployment" patterns/11_probabilistic_structures/README.md && echo "✅" || echo "❌"

echo ""
echo "=== Evaluator framing ==="
for f in $(find patterns/11_probabilistic_structures/ -name "*.md" -not -name "README.md" | sort); do
    has_eval=$(grep -q "interviewer evaluates" "$f" && echo "Y" || echo "N")
    echo "  $(basename $f): evaluator=$has_eval"
done

echo ""
echo "=== Style + tests ==="
grep -rn "—" patterns/11_probabilistic_structures/ --include="*.md" && echo "❌" || echo "✅ No em dashes"
uv run pytest patterns/11_probabilistic_structures/ --tb=short -q 2>&1 | tail -3
```
