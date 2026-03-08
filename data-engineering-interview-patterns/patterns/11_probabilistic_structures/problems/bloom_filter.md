# Bloom Filter

> **Difficulty:** Medium | **Interview Frequency:** Common

## Problem Statement

Implement a Bloom filter that supports adding elements and checking membership with a configurable false positive rate. The filter should automatically calculate optimal size and hash count based on the expected number of elements.

## Thought Process

1. **The core idea:** Instead of storing elements, store k hashed "fingerprints" as bit positions. To check membership, verify all k positions are set. If any bit is 0, the element was never added (no false negatives). If all are 1, it was probably added (but hash collisions can cause false positives).
2. **Optimal sizing:** Given n expected elements and desired FP rate p, the optimal bit array size is m = -(n * ln(p)) / (ln(2))^2, and optimal hash count is k = (m/n) * ln(2).
3. **Double hashing:** Instead of k independent hash functions, use two hashes and combine them: h_i(x) = h1(x) + i * h2(x). This gives equally good results with less computation.

## Worked Example

A Bloom filter is a bit array where each element "claims" k bit positions via hashing. Membership is confirmed only if ALL k positions are set. False positives occur when different elements' hash positions overlap, setting bits that make a non-member look like a member.

```
Parameters: expected_items=3, fp_rate=0.10
Calculated: size=15 bits, hash_count=3

Add "apple":
  h1("apple")=2, h2("apple")=8, h3("apple")=13
  Bit array: 0 0 1 0 0 0 0 0 1 0 0 0 0 1 0
                  ^               ^           ^

Add "banana":
  h1("banana")=1, h2("banana")=5, h3("banana")=9
  Bit array: 0 1 1 0 0 1 0 0 1 1 0 0 0 1 0
                ^               ^       ^

Query "apple": positions 2,8,13 -> all 1 -> PROBABLY IN SET
Query "banana": positions 1,5,9 -> all 1 -> PROBABLY IN SET

Query "cherry":
  h1("cherry")=2, h2("cherry")=5, h3("cherry")=13
  positions 2,5,13 -> all 1 -> FALSE POSITIVE
  (positions 2 and 13 from "apple", position 5 from "banana")

Query "date":
  h1("date")=0, h2("date")=5, h3("date")=14
  position 0 is 0 -> DEFINITELY NOT IN SET
  (one zero bit is enough to confirm absence)

Memory: 2 bytes for 3 elements (vs ~210 bytes for a Python set)
```

## Approaches

### Approach 1: Bit Array with Double Hashing

<details>
<summary>📝 Explanation</summary>

Use a bytearray as the bit storage (Python doesn't have a built-in bit array). Calculate optimal m (bits) and k (hashes) from the expected items and desired FP rate.

For each add/query, compute k positions using double hashing: position_i = (h1 + i * h2) % m. This avoids needing k independent hash functions while maintaining the same theoretical properties.

The key formulas:
- Optimal bits: m = -(n * ln(p)) / (ln(2))^2
- Optimal hashes: k = (m/n) * ln(2)
- Theoretical FP rate: (1 - e^(-kn/m))^k

At 1% FP rate, each element needs about 9.6 bits (roughly 1.2 bytes). A million elements need about 1.2 MB. Compare to a Python set that would need roughly 70 MB.

**Time:** O(k) per add and query. k is typically 3-10.
**Space:** O(m) bits. For 1% FP: ~10 bits per expected element.

</details>

## Edge Cases

| Scenario | Behavior |
|---|---|
| Query on empty filter | Always returns False (no bits set) |
| Same element added twice | No change (bits already set) |
| More items than expected | Works but FP rate increases beyond configured target |
| Very low FP rate (0.001) | Needs more bits and more hash functions |

## Interview Tips

> "A Bloom filter trades a small false positive rate for massive memory savings. It uses k hash functions to map each element to k bit positions. If all k bits are set, the element is probably in the set. If any bit is 0, it's definitely not. For 1% false positive rate, you need about 10 bits per element."

**Follow-ups:**
- "Can you delete elements?" - Not from a standard Bloom filter (clearing a bit might affect other elements). Use a Counting Bloom Filter (replace bits with counters).
- "What hash functions?" - MurmurHash3 is standard. Double hashing (two hashes combined) is as good as k independent hashes.
- "What if the number of elements exceeds the expected count?" - The filter still works but FP rate degrades. Monitor fill ratio.

**What the interviewer evaluates:** Understanding false positives (possible) vs false negatives (impossible) is the baseline. Explaining the math (optimal k, bit array sizing for target FPR) shows depth. The real principal-level signal: knowing where Bloom filters are used in production (Cassandra, HBase, LSM tree compaction) and being able to calculate the memory/error tradeoff for a given use case. "For 100M keys at 1% FPR, I need ~120MB" is the kind of back-of-envelope calculation interviewers want to hear.

## DE Application

Deduplication pre-filter in streaming pipelines. Before doing an expensive database lookup to check "have I seen this event ID before?", check the Bloom filter first. If it says "no," skip the DB call (guaranteed correct). If it says "maybe," do the DB call (might be a false positive). This eliminates 99%+ of unnecessary database queries.

## At Scale

A Bloom filter for 1B elements at 1% false positive rate uses ~1.2GB. For 0.1% false positive rate, ~1.8GB. This is fixed regardless of element size - a Bloom filter for 1B URLs (averaging 100 bytes each) uses the same 1.2GB as for 1B integers. The hash computations are the bottleneck: for k=7 hash functions and 1B lookups, that's 7B hash operations (~10 seconds). In production, Bloom filters are used as gatekeepers: Cassandra checks a Bloom filter before reading from disk. If the filter says "not present," the disk read is skipped entirely. This saves ~90% of disk reads for non-existent keys. The false positive rate means ~1% of "not found" queries still hit disk unnecessarily - an acceptable tradeoff. For distributed systems, each partition maintains its own Bloom filter. Merging Bloom filters across partitions is possible (bitwise OR) but increases the false positive rate.

## Related Concepts

- Counting Bloom Filter: allows deletions by replacing bits with counters
- Cuckoo Filter: better for workloads that need deletion, slightly more memory efficient
- Quotient Filter: cache-friendly alternative
