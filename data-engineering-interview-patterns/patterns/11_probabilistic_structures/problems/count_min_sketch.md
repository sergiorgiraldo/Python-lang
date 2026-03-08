# Count-Min Sketch

> **Difficulty:** Medium | **Interview Frequency:** Common

## Problem Statement

Implement a Count-Min Sketch that tracks approximate frequency counts for elements in a data stream using fixed memory. Support adding elements with counts, estimating frequencies and detecting heavy hitters.

## Thought Process

1. **The structure:** A 2D table with d rows and w columns. Each row has its own hash function. To increment, hash the item with each function and increment those d cells. To query, hash and return the minimum across all d rows.
2. **Why minimum?** Each cell accumulates counts from all items that hash to that position. The true count for an item is always <= each cell's value. Taking the minimum across rows gives the cell with the least collision noise.
3. **Error bounds:** The over-count is at most epsilon * N (total count) with probability at least 1 - delta, where epsilon = e/w and delta = e^(-d).

## Worked Example

The Count-Min Sketch is a grid where each row uses a different hash function. Adding an element increments one cell per row. Querying returns the minimum across rows. The minimum gives the tightest upper bound because it includes the least collision noise from other elements.

```
CMS with width=8, depth=3 (tiny, for illustration)

Add "apple" x 5:
  Row 0: h0("apple") = 3 -> table[0][3] += 5
  Row 1: h1("apple") = 1 -> table[1][1] += 5
  Row 2: h2("apple") = 6 -> table[2][6] += 5

Add "banana" x 3:
  Row 0: h0("banana") = 3 -> table[0][3] += 3  (collision with apple in row 0)
  Row 1: h1("banana") = 5 -> table[1][5] += 3
  Row 2: h2("banana") = 2 -> table[2][2] += 3

Table:
  Row 0: [0, 0, 0, 8, 0, 0, 0, 0]   <- cell 3 has apple(5) + banana(3)
  Row 1: [0, 5, 0, 0, 0, 3, 0, 0]   <- no collisions in this row
  Row 2: [0, 0, 3, 0, 0, 0, 5, 0]   <- no collisions in this row

Estimate "apple":
  Row 0, col 3: 8  (inflated by banana collision)
  Row 1, col 1: 5  (exact)
  Row 2, col 6: 5  (exact)
  min(8, 5, 5) = 5  exact

Estimate "banana":
  Row 0, col 3: 8  (inflated)
  Row 1, col 5: 3  (exact)
  Row 2, col 2: 3  (exact)
  min(8, 3, 3) = 3  exact

Estimate "cherry" (never added):
  Row 0, col 1: 0
  -> min includes 0 -> estimate = 0

The minimum operation "routes around" collisions. As long as at least
one row has no collision for a given item, the estimate is exact.
With more rows (depth), the probability of collision in ALL rows drops
exponentially.
```

## Approaches

### Approach 1: 2D Array with Multiple Hash Functions

<details>
<summary>📝 Explanation</summary>

The table is a list of d lists, each of width w. Use MurmurHash3 with different seeds for each row.

**Add(item, count):** For each row i, compute h_i(item) % w and increment that cell by count.

**Estimate(item):** For each row i, compute h_i(item) % w and read that cell. Return the minimum.

The minimum is the best estimate because:
- Each cell value >= true count (counts are only added, never subtracted)
- The cell with the fewest collisions is closest to the true count
- The minimum across all rows selects the least-collided cell

**Sizing:**
- Width w controls accuracy: epsilon = e/w
- Depth d controls confidence: delta = e^(-d)
- For epsilon=0.1% and delta=1%: w=2719, d=5 -> ~108 KB

**Time:** O(d) per add and estimate.
**Space:** O(w * d) counters.

</details>

## Edge Cases

| Scenario | Behavior |
|---|---|
| Never-added item | Returns 0 (all cells for that item are 0 unless collisions) |
| Item added once | Returns >= 1 (exact unless extreme collision) |
| Very frequent item | Accurate (its own count dominates any collision noise) |
| All unique items | Accuracy degrades (many collisions, cells fill up) |

## Interview Tips

> "A Count-Min Sketch is a 2D array with d hash functions. To add an item, hash it with each function and increment those cells. To query, return the minimum cell value. The minimum gives the tightest upper bound. It never under-counts but can over-count by at most epsilon times the total count."

**Key talking points:**
- It's a frequency estimator, not a set membership test (that's Bloom filter)
- The "sketch" name comes from the fact that it's a compressed summary of the data
- Heavy hitter detection pairs CMS with a small heap of candidates

**What the interviewer evaluates:** CMS is less commonly asked about directly. It usually comes up in context: "how would you detect hot keys in a data pipeline?" or "how would you find the top-10 most frequent events in a stream without storing all frequencies?" Knowing that CMS provides frequency upper bounds (never underestimates) and that it pairs with a heap for streaming top-k shows you've thought about production applications.

## DE Application

Hot key detection in streaming pipelines. When events flow through a system at millions per second, identifying which keys are "hot" (appearing much more than average) helps diagnose skew, set up targeted caching or trigger alerts. A Count-Min Sketch tracks approximate frequencies for all keys using fixed memory, flagging any key whose estimated count exceeds a threshold percentage of total traffic.

## At Scale

A Count-Min Sketch with width 2000 and depth 5 uses ~40KB and estimates frequencies with error proportional to total count / width. For 1B events, the maximum overestimate per element is ~500K (0.05% of total). This is compact enough to maintain per-partition in a streaming system. In production, CMS is used for finding heavy hitters (elements exceeding a frequency threshold) without storing all frequencies. Network monitoring uses CMS to detect high-traffic IP addresses. In data pipelines, CMS detects hot keys before a shuffle: if one key accounts for 10% of traffic, the pipeline can salt that key to avoid partition skew. The "count then check" pattern (CMS for fast frequency approximation, exact counting only for elements above the threshold) reduces memory from O(unique elements) to O(sketch size).

## Related Concepts

- Count Sketch: allows both over and under-estimation, uses random signs for unbiased estimates
- Space Saving: deterministic heavy hitter algorithm, exact for items above threshold
- Misra-Gries: classic streaming frequency algorithm, relates to CMS
