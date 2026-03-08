# HyperLogLog

> **Difficulty:** Medium | **Interview Frequency:** Common

## Problem Statement

Implement a HyperLogLog cardinality estimator that can count the number of distinct elements in a dataset using fixed memory regardless of dataset size. Support adding elements, estimating cardinality and merging two HLL instances.

## Thought Process

1. **The observation:** If you hash elements uniformly and look at the binary representation, the probability of seeing k leading zeros is 1/2^k. So if the longest run of leading zeros you've seen is 10, you've probably seen about 2^10 = 1024 distinct elements.
2. **Reduce variance with buckets:** A single maximum is noisy. Split elements into m buckets (using the first p bits of the hash as the bucket index) and track the max leading zeros per bucket. Combine using the harmonic mean for a more stable estimate.
3. **Bias corrections:** Small cardinalities and very large cardinalities need corrections. Linear counting handles the small range (when many registers are still zero). Large range correction handles hash collision effects.

## Worked Example

Each element is hashed and split into a bucket index (first p bits) and a run value (leading zeros in the remaining bits). The register stores the maximum run seen for each bucket. The harmonic mean of 2^(-register) values across all registers gives the raw estimate, corrected by a constant alpha.

```
Precision p=4 -> 16 registers (tiny, for illustration)

Add "alice":
  hash = 0b 0011 010110001... (32 bits)
  bucket = 0b0011 = 3 (first 4 bits)
  remaining = 010110001... -> leading zeros = 0 -> run = 1
  registers[3] = max(0, 1) = 1

Add "bob":
  hash = 0b 0011 000010110...
  bucket = 3 (same bucket as alice)
  remaining = 000010110... -> leading zeros = 3 -> run = 4
  registers[3] = max(1, 4) = 4

Add "charlie":
  hash = 0b 1010 001101...
  bucket = 10
  remaining = 001101... -> leading zeros = 1 -> run = 2
  registers[10] = max(0, 2) = 2

Registers after 3 items: mostly zeros, a few non-zero.
  [0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0]

Estimate:
  indicator = sum(2^(-reg)) = 14*2^0 + 2^(-4) + 2^(-2)
            = 14 + 0.0625 + 0.25 = 14.3125
  raw = alpha * 16^2 / 14.3125 ~ 0.673 * 256 / 14.3125 ~ 12.0

  Small range correction: 14 registers are zero.
  linear_count = 16 * ln(16/14) ~ 16 * 0.134 ~ 2.1

  Corrected estimate ~ 2 (close to actual 3)

With p=14 (16384 registers) and millions of items, the estimate
is typically within 1-2% of the true count.
```

## Approaches

### Approach 1: Register-Based with Bias Corrections

<details>
<summary>📝 Explanation</summary>

The implementation has three parts:

**Add:** Hash the element. Use the first p bits as the register index. Count leading zeros in the remaining 32-p bits, add 1 (so a hash of all zeros gives max value, not zero). Update the register if this value is larger than the current one.

**Estimate:** Compute the harmonic mean of 2^(-register) values across all registers. Multiply by alpha * m^2 (bias correction constant). Apply small-range correction (linear counting) when many registers are zero. Apply large-range correction when estimate approaches 2^32 (hash space limit).

**Merge:** Take the element-wise maximum of two register arrays. This works because the max leading zeros for any element is captured by whichever HLL saw it. This enables distributed counting: each worker maintains its own HLL, then a final merge produces the global estimate.

**Time:** O(1) per add, O(m) per estimate, O(m) per merge.
**Space:** O(m) = O(2^p) bytes. At p=14: 16,384 bytes = 16 KB.

The standard error is 1.04/sqrt(m). At p=14: 1.04/128 = 0.81%.

</details>

## Edge Cases

| Scenario | Behavior |
|---|---|
| Empty HLL | Estimate returns 0 (all registers zero, linear counting gives 0) |
| Single element | Returns ~1 (one register non-zero, linear counting corrects) |
| All duplicates | Returns ~1 (same hash always updates the same register to the same value) |
| 1 billion distinct elements | Returns estimate within ~1% using 16 KB |

## Interview Tips

> "HyperLogLog estimates distinct counts using fixed memory. It hashes elements, splits them into buckets using the first p bits, and tracks the longest run of leading zeros per bucket. Combining with a harmonic mean gives an estimate with about 1% error using 16 KB. This is what APPROX_COUNT_DISTINCT uses in BigQuery and Snowflake."

**Key talking points:**
- The merge operation (max of registers) enables distributed counting
- Memory is fixed regardless of cardinality
- Error is ~1.04/sqrt(m), independent of dataset size

**What the interviewer evaluates:** You don't need to derive the math. You need to know: fixed memory (~16KB), ~0.8% error, mergeable across partitions. The killer answer in an interview: "I'd use APPROX_COUNT_DISTINCT in BigQuery, which uses HLL internally. For a dashboard showing daily unique users, 0.8% error is invisible. For billing where we charge per unique user, I'd use exact COUNT(DISTINCT) and accept the higher cost." This exact-vs-approximate decision framework is what the interviewer is really testing.

## DE Application

Every data warehouse has queries like "count distinct users per day across 500M events." Exact COUNT DISTINCT requires sorting or hashing all values. APPROX_COUNT_DISTINCT uses HLL internally and returns a result with ~1% error in a fraction of the time and memory. Understanding HLL helps you explain the ~1% discrepancy to stakeholders and choose appropriate precision settings.

## At Scale

HyperLogLog with 2^14 registers (16KB) estimates cardinality of billions of elements with ~0.8% standard error. The estimation is independent of the actual cardinality - counting 1M unique users and 1B unique users uses the same 16KB. This is why every major analytics database uses HLL for COUNT(DISTINCT). The practical consideration at scale: HLL registers are mergeable. You can compute per-partition HLL sketches in parallel and merge them for a global estimate. This is how distributed COUNT(DISTINCT) works in BigQuery, Snowflake and Presto. The merge operation is simple (take the max register value per position) and the merged result has the same error bound as if computed centrally. For time-series cardinality (unique users per day over 365 days), store one HLL sketch per day. Any time range query merges the relevant daily sketches.

## Related Concepts

- LogLog: predecessor, uses geometric mean instead of harmonic
- HyperLogLog++: Google's improvement with better small-cardinality corrections
- MinHash: related technique for estimating set similarity (Jaccard index)
