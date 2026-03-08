# DE Scenario: Memory Budget Analysis

## Real-World Context

Choosing between exact and approximate data structures is a principal-level decision. The answer depends on cardinality (how many items), accuracy requirements (is 1% error acceptable) and memory budget (what fits in a single machine's RAM).

This analysis shows how the gap between exact and approximate grows with cardinality. At 1K items, exact is fine. At 100M items, exact needs 8+ GB while approximate structures need kilobytes.

## Worked Example

The memory comparison reveals why approximate structures exist. Below 100K items, exact structures fit comfortably in memory and the accuracy trade-off isn't worth it. Above 1M items, the memory savings become significant. Above 100M, approximate structures are often the only option that fits in memory.

```
Cardinality    Exact Set     Bloom 1%   Bloom 0.1%      HLL        CMS
-----------   ----------    ---------   ----------   --------   --------
      1,000      88.0 KB      1.2 KB      1.8 KB    16.0 KB    78.1 KB
     10,000     878.9 KB     11.7 KB     17.6 KB    16.0 KB    78.1 KB
    100,000       8.6 MB    117.2 KB    175.8 KB    16.0 KB    78.1 KB
  1,000,000      85.8 MB      1.1 MB      1.7 MB    16.0 KB    78.1 KB
 10,000,000     858.3 MB     11.4 MB     17.1 MB    16.0 KB    78.1 KB
100,000,000       8.4 GB    114.2 MB    171.4 MB    16.0 KB    78.1 KB

Key observations:
  - Exact set: grows linearly with cardinality. O(n).
  - Bloom filter: grows linearly but ~70x smaller than exact. O(n).
  - HLL: FIXED at 16 KB regardless of cardinality. O(1).
  - CMS: FIXED at ~80 KB regardless of cardinality. O(1).

Decision framework:
  - Need exact membership? Use a set (if it fits) or database.
  - Need approximate membership? Bloom filter.
  - Need approximate count distinct? HLL. Always fits. ~1% error.
  - Need approximate frequency? CMS. Fixed memory.
  - Cardinality under 100K? Just use exact. Memory is cheap.
  - Cardinality over 10M? Approximate is probably necessary.
```
