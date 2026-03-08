# Human Traffic of Stadium (LeetCode #601)

🔗 [LeetCode 601: Human Traffic of Stadium](https://leetcode.com/problems/human-traffic-of-stadium/)

> **Difficulty:** Hard | **Interview Frequency:** Common

## Problem Statement

Write a SQL query to find rows in the Stadium table where 3 or more consecutive rows have people >= 100. Return all rows that are part of such a streak, ordered by id.

## Thought Process

1. **This is the "island" problem:** We need to find groups of consecutive qualifying rows. The classic technique is `id - ROW_NUMBER()`: for consecutive qualifying rows, this difference is constant, creating a group identifier.
2. **Two-phase approach:** Phase 1 identifies the groups. Phase 2 filters for groups with 3+ members. A final join retrieves the full rows.
3. **Why id - ROW_NUMBER works:** If qualifying ids are 5, 6, 7, 8, then ROW_NUMBER gives 1, 2, 3, 4, and the differences are 4, 4, 4, 4. They share the same group. If there is a gap (ids 2, 3, 5, 6, 7), the differences change at the gap: 1, 1, 2, 2, 2. Two separate groups.

## Worked Example

The island technique relies on a mathematical property: when you subtract a sequential counter from a sequential value, consecutive sequences produce the same constant. A break in the sequence changes the constant, creating a new group.

```
Stadium table (filtered to people >= 100):
  id | people    ROW_NUMBER  | id - ROW_NUMBER (grp)
  2  | 109       1           | 1
  3  | 150       2           | 1
  5  | 145       3           | 2
  6  | 1455      4           | 2
  7  | 199       5           | 2
  8  | 188       6           | 2

Groups:
  grp=1: ids 2, 3     -> 2 rows (< 3, excluded)
  grp=2: ids 5, 6, 7, 8 -> 4 rows (>= 3, included)

Result: ids 5, 6, 7, 8

Why id=4 breaks the group: id=4 has people=99 (< 100), so it is
excluded from the filtered set. This changes the ROW_NUMBER sequence
and creates a new group constant.
```

## Approaches

### Approach 1: Island Technique (id - ROW_NUMBER)

<details>
<summary>Explanation</summary>

1. Filter for rows where people >= 100
2. Compute `id - ROW_NUMBER() OVER (ORDER BY id)` as a group identifier
3. Group by this identifier and keep groups with COUNT(*) >= 3
4. Join back to get the full rows

The technique requires:
- A sequential or sortable column (id in this case)
- ROW_NUMBER to create a sequential counter within the filtered set
- The difference between the two creates group boundaries at gaps

**Dialect notes:** All major engines support this pattern. No dialect-specific concerns.

</details>

## Edge Cases

| Scenario | Expected | Why |
|---|---|---|
| No row has people >= 100 | Empty result | No qualifying rows |
| Exactly 3 consecutive | Those 3 rows | Minimum qualifying streak |
| Two separate streaks | All rows from both | Each streak meets threshold |
| All rows qualify | All rows | One big streak |
| Streaks of 1 and 2 | Empty result | Neither meets threshold |

## Interview Tips

> "This is the island problem. I'll filter for rows with people >= 100, then use the id minus ROW_NUMBER trick to group consecutive qualifying rows. Groups with 3 or more members are the answer."

**What the interviewer evaluates:** The island technique is a must-know for data engineers. If you do not recognize the `id - ROW_NUMBER()` trick, this problem is nearly impossible to solve efficiently. This tests whether you have studied SQL patterns specifically, not just general SQL syntax. Being able to explain why the subtraction creates groups demonstrates deep understanding.

## At Scale

ROW_NUMBER is a single pass after sorting: O(n log n). The GROUP BY with HAVING is hash aggregation: O(n). The join back is O(n). Total: O(n log n), dominated by the sort. For 1B rows, this is fast. The alternative (triple self-join or nested LAG) is either O(n^2) or limited to fixed streak lengths. The island technique scales linearly and handles arbitrary streak lengths.

## DE Application

The island technique appears in:
- **Monitoring:** detecting streaks of consecutive alerts or SLA breaches
- **Session detection:** grouping consecutive events into sessions (variant of sessionization)
- **Data quality:** finding consecutive missing values or consecutive anomalies
- **Clickstream:** identifying browsing sessions separated by idle periods

It is one of the most frequently asked SQL questions in DE interviews because it tests a non-obvious technique that has direct production applications.

## Related Problems

- [180. Consecutive Numbers](180_consecutive_numbers.md) - Simpler consecutive detection with LAG
- [197. Rising Temperature](197_rising_temperature.md) - Row-to-row comparison
