# Consecutive Numbers (LeetCode #180)

🔗 [LeetCode 180: Consecutive Numbers](https://leetcode.com/problems/consecutive-numbers/)

> **Difficulty:** Medium | **Interview Frequency:** Very Common

## Problem Statement

Write a SQL query to find all numbers that appear at least three times consecutively in the Logs table. The table has columns id (auto-increment) and num.

## Thought Process

1. **Compare adjacent rows:** We need to check if the current row's num matches the two preceding rows. This is a textbook LAG use case.
2. **LAG vs self-join:** LAG(num, 1) and LAG(num, 2) look back one and two rows. A self-join on `l2.id = l1.id + 1` does the same but assumes contiguous IDs.
3. **Distinct results:** Multiple overlapping triples of the same number should produce one result row, so we use DISTINCT.

## Worked Example

The key insight is that "consecutive" means adjacent in id order. LAG looks back N rows in that order, giving us the previous values to compare against. If the current num equals both LAG(1) and LAG(2), we have three consecutive identical values.

```
Logs table:
  id | num
  1  | 1
  2  | 1
  3  | 1
  4  | 2
  5  | 1
  6  | 2
  7  | 2

After LAG:
  id=1: num=1, prev1=NULL, prev2=NULL
  id=2: num=1, prev1=1,    prev2=NULL
  id=3: num=1, prev1=1,    prev2=1     -> match (1=1=1)
  id=4: num=2, prev1=1,    prev2=1     -> no match
  id=5: num=1, prev1=2,    prev2=1     -> no match
  id=6: num=2, prev1=1,    prev2=2     -> no match
  id=7: num=2, prev1=2,    prev2=1     -> no match

Result: {1}
```

## Approaches

### Approach 1: LAG Window Function

<details>
<summary>Explanation</summary>

Use LAG(num, 1) and LAG(num, 2) to get the two preceding values. Filter where all three are equal. This is a single pass through the data with O(1) lookback per row.

Extending to N consecutive is straightforward: add more LAG calls up to LAG(num, N-1). No structural change to the query.

**Dialect notes:** All major engines support LAG/LEAD.

</details>

### Approach 2: Self-Join

<details>
<summary>Explanation</summary>

Join the table to itself three times on consecutive ids:

```sql
FROM Logs l1
JOIN Logs l2 ON l2.id = l1.id + 1
JOIN Logs l3 ON l3.id = l1.id + 2
WHERE l1.num = l2.num AND l2.num = l3.num
```

This works when IDs are contiguous but breaks when there are gaps in the auto-increment sequence. Gaps are common in production: deleted rows, failed inserts, rolled-back transactions. The LAG approach handles gaps correctly because it operates on row order, not ID arithmetic.

</details>

## Edge Cases

| Scenario | Expected | Why |
|---|---|---|
| No three in a row | Empty result | No consecutive triples |
| Exactly three consecutive | That number | Minimum qualifying streak |
| Longer streak (5+) | That number once | DISTINCT deduplicates |
| Multiple different numbers | All qualifying numbers | Each checked independently |
| Two consecutive only | Empty result | Does not meet threshold |

## Interview Tips

> "I'll use LAG to look back one and two rows. If the current value matches both, we have three consecutive. LAG is preferable to the self-join approach because self-joins assume contiguous IDs, which is fragile in production data."

**What the interviewer evaluates:** LAG/LEAD knowledge is essential for DE roles. The self-join approach is a red flag because it assumes contiguous IDs, which is rarely true in production systems. Reaching for window functions first is the expected behavior. Mentioning the fragility of ID arithmetic shows production awareness.

## At Scale

LAG is a single sorted pass: O(n log n) for the sort, O(n) for the scan with O(1) lookback. The self-join is O(n) with an index on id but O(n^2) without one. For 1B log rows, LAG completes in a single pass after sorting. The self-join requires three index lookups per row. At scale, the window function approach is strictly better.

## DE Application

Detecting consecutive occurrences is a core monitoring pattern: consecutive pipeline failures trigger alerts, consecutive days of metric decline trigger investigations and consecutive SLA breaches escalate to incident response. The LAG pattern extends naturally to "N consecutive events matching a condition," which is the foundation of complex event processing (CEP) in streaming systems.

## Related Problems

- [601. Human Traffic of Stadium](601_human_traffic_of_stadium.md) - Island technique for streak detection
- [197. Rising Temperature](197_rising_temperature.md) - LAG for day-over-day comparison
