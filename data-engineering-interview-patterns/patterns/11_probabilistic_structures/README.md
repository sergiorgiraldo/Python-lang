# Probabilistic Data Structures

## What Is It?

### The problem: exact answers don't scale

Counting unique visitors across 10 billion events. Checking if an IP is in a blocklist of 500 million addresses. Finding which keys in a stream are "hot" (appear more than 0.1% of the time). These problems have exact solutions, but the exact solutions require storing the entire dataset in memory.

A hash set for 500 million IPs uses roughly 8 GB of RAM. A `set()` for 10 billion unique user IDs is even larger. At scale, the memory cost of exact answers becomes the bottleneck.

Probabilistic data structures trade a small, bounded amount of accuracy for massive memory savings. A Bloom filter can answer "is this IP in the blocklist?" using 1/100th of the memory, at the cost of occasionally saying "yes" when the answer is "no" (false positives). A HyperLogLog can estimate 10 billion unique visitors using 12 KB of memory, accurate to within 2%.

### The three structures

**Bloom Filter: "Is this element in the set?"**
- Answers membership queries: yes (maybe) or no (definitely)
- False positives possible, false negatives impossible
- Memory: few bits per element (much less than storing the element)
- Use when: dedup pre-filtering, cache lookup, blocklist checking

**HyperLogLog (HLL): "How many distinct elements?"**
- Estimates cardinality (COUNT DISTINCT) with bounded error
- Standard error: ~1.04 / sqrt(m) where m is the number of registers
- Memory: 12-16 KB for billions of elements (with ~2% error)
- Use when: counting unique users, distinct IPs, unique queries

**Count-Min Sketch (CMS): "How often does this element appear?"**
- Estimates frequency of individual elements
- Over-estimates possible, under-estimates impossible
- Memory: fixed regardless of data size
- Use when: heavy hitter detection, frequency capping, hot key identification

### How they work (intuition, not proofs)

All three use hash functions to map elements to positions in a compact data structure. The "probabilistic" part comes from hash collisions: different elements can map to the same positions, causing errors. More memory means fewer collisions means higher accuracy.

**Bloom Filter:** An array of bits with k hash functions. To add an element, hash it k times and set those k bit positions to 1. To check membership, hash it k times and check if ALL k positions are 1. If any position is 0, the element is definitely not in the set. If all are 1, it's probably in the set (or those bits were set by other elements - a false positive).

**HyperLogLog:** Hash each element and count the number of leading zeros in the binary hash. Intuitively: if you've seen a hash with 10 leading zeros, you've probably hashed about 2^10 = 1024 distinct elements (because each additional leading zero is half as likely). Use multiple "buckets" (registers) and combine their estimates with a harmonic mean.

**Count-Min Sketch:** A 2D array (d rows x w columns) with d hash functions. To increment an element's count, hash it with each function and increment the corresponding cell. To query, hash it with each function and return the minimum cell value. The minimum is the best estimate because it has the least collision noise.

### Connection to data engineering

These structures are everywhere in production data systems, often hidden inside tools you already use:

- **BigQuery's `APPROX_COUNT_DISTINCT()`** uses HyperLogLog internally
- **Snowflake's `APPROX_COUNT_DISTINCT()`** also uses HLL
- **Redis** has built-in Bloom filter and HyperLogLog commands
- **Apache Spark** uses Count-Min Sketch for approximate frequency counts
- **Cassandra** and **Druid** use Bloom filters for efficient row lookups
- **Data quality tools** use Bloom filters to check for duplicates in streaming data

Understanding the mechanics helps you:
1. Choose the right approximate function and set appropriate error bounds
2. Explain to stakeholders why the count is "approximately 4.2 million" not "exactly 4,203,881"
3. Debug when approximate counts are unexpectedly inaccurate
4. Design memory-efficient pipelines for high-cardinality data

### What the implementations in this section cover

| Structure | Query type | Error type | Memory |
|---|---|---|---|
| [Bloom Filter](problems/bloom_filter.md) | "Is X in the set?" | False positives | ~10 bits/element |
| [HyperLogLog](problems/hyperloglog.md) | "How many distinct?" | ±2% typical | 12 KB fixed |
| [Count-Min Sketch](problems/count_min_sketch.md) | "How often does X appear?" | Over-counts | Fixed by accuracy |

Each implementation is built from scratch with tests, then compared against the math-predicted error bounds.

## When to Use It

**Use probabilistic structures when:**
- The exact answer requires more memory than available
- A bounded error (1-5%) is acceptable
- Speed matters more than precision
- You're dealing with streaming data (can't rescan)

**Don't use when:**
- Financial calculations requiring exact counts
- Small datasets where exact fits in memory
- Legal/compliance requirements for exact numbers
- The error bound would change the decision

**Recognition signals in interviews:**
- "Billions of events / users / records"
- "Memory-efficient" or "space-efficient"
- "Approximate count" or "estimate frequency"
- Any problem where storing the full dataset is impractical

## Visual Aid

```
Bloom Filter (k=3 hash functions, m=16 bits):

  Add "apple":  h1("apple")=2, h2("apple")=7, h3("apple")=13
  Bits:  0 0 1 0 0 0 0 1 0 0 0 0 0 1 0 0
              ^             ^             ^

  Add "banana": h1("banana")=4, h2("banana")=7, h3("banana")=11
  Bits:  0 0 1 0 1 0 0 1 0 0 0 1 0 1 0 0
              ^   ^       ^       ^   ^

  Check "apple": positions 2,7,13 → all 1 → PROBABLY IN SET ✓
  Check "cherry": h1=2, h2=4, h3=11 → all 1 → FALSE POSITIVE
      (positions 2,4,11 were set by "apple" and "banana", not "cherry")
  Check "date":  h1=0, h2=7, h3=15 → position 0 is 0 → DEFINITELY NOT IN SET

  False positive rate ≈ (1 - e^(-kn/m))^k
  With k=3, n=2 elements, m=16 bits: ≈ 3.5%
  More bits → fewer collisions → lower false positive rate.


HyperLogLog (simplified):

  Hash "user_1" → binary: 0001011...  → 3 leading zeros → register = max(register, 3+1) = 4
  Hash "user_2" → binary: 0000001...  → 6 leading zeros → register = max(register, 6+1) = 7
  Hash "user_3" → binary: 0101001...  → 1 leading zero  → register = max(register, 7) = 7 (no change)

  Estimate: 2^(average register value) ≈ 2^((4+7)/2) ≈ 2^5.5 ≈ 45
  (Actual uses harmonic mean across many registers for better accuracy)
```

## Trade-offs

**Bloom Filter sizing:**
- More bits (m) → lower false positive rate but more memory
- More hash functions (k) → lower false positive rate up to optimal, then higher
- Optimal k = (m/n) * ln(2) where n is expected element count
- Rule of thumb: 10 bits per element gives ~1% false positive rate

**HyperLogLog precision:**
- p bits of precision → 2^p registers → error ≈ 1.04/sqrt(2^p)
- p=14 (default in most implementations) → 16384 registers → ~0.8% error → 12 KB memory
- Doubling memory (p+1) reduces error by ~30%, not 50%

**Count-Min Sketch sizing:**
- Width w and depth d control accuracy
- Probability of over-counting > ε*N is at most δ, where ε=e/w, δ=e^(-d)
- More width → better accuracy. More depth → higher confidence.
- Typical: d=5 rows, w=2000 columns for most streaming use cases

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

## Problems in This Section

| Structure | What You Build | Key Concept |
|---|---|---|
| [Bloom Filter](problems/bloom_filter.md) | From-scratch Bloom filter with tunable FP rate | Bit arrays + multiple hash functions |
| [HyperLogLog](problems/hyperloglog.md) | From-scratch HLL with register-based counting | Leading zeros + harmonic mean |
| [Count-Min Sketch](problems/count_min_sketch.md) | From-scratch CMS with frequency estimation | 2D hash array + minimum query |

## DE Scenarios

| Scenario | Structure | Real-World Use |
|---|---|---|
| [Stream Deduplication](de_scenarios/stream_dedup.md) | Bloom Filter | Pre-filter duplicates in event streams |
| [Approximate Distinct Count](de_scenarios/approx_distinct.md) | HyperLogLog | COUNT DISTINCT over billions of rows |
| [Heavy Hitter Detection](de_scenarios/heavy_hitters.md) | Count-Min Sketch | Find hot keys in streaming data |
| [Memory Budget Analysis](de_scenarios/memory_budget.md) | All three | Compare exact vs approximate at various scales |
