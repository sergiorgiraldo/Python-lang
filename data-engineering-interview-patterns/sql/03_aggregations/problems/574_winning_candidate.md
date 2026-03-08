# Winning Candidate (LeetCode #574)

🔗 [LeetCode 574: Winning Candidate](https://leetcode.com/problems/winning-candidate/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

## Problem Statement

Find the name of the candidate who received the most votes.

## Thought Process

1. **Join Vote to Candidate:** Each vote references a candidateId. Join to get the candidate's name.
2. **GROUP BY candidate:** Count votes per candidate using COUNT(*).
3. **ORDER BY + LIMIT 1:** Sort by vote count descending and take the top row.

## Worked Example

The query joins votes to candidates, groups by candidate and counts votes, then orders descending and limits to one row. The JOIN filters out votes for non-existent candidates. The GROUP BY + ORDER BY + LIMIT pattern is the standard way to find the "top-1" entity.

```
Candidate:             Vote:
  id | name              id | candidateId
  1  | A                 1  | 2
  2  | B                 2  | 4
  3  | C                 3  | 3
                         4  | 2
                         5  | 2

JOIN on candidateId = id (vote for candidateId=4 dropped, no match):
  (B, vote1), (C, vote3), (B, vote4), (B, vote5)

GROUP BY c.id, c.name:
  B -> COUNT(*) = 3
  C -> COUNT(*) = 1

ORDER BY COUNT(*) DESC, LIMIT 1:
  B (3 votes)

Result: B
```

## Approaches

### Approach 1: JOIN + GROUP BY + ORDER BY + LIMIT

<details>
<summary>Explanation</summary>

```sql
SELECT c.name
FROM Vote v
JOIN Candidate c ON v.candidateId = c.id
GROUP BY c.id, c.name
ORDER BY COUNT(*) DESC
LIMIT 1;
```

The most direct approach. The join resolves candidate names, GROUP BY counts votes, ORDER BY + LIMIT finds the maximum. This is the "top-1 with detail" pattern: aggregate, sort, take one.

</details>

### Approach 2: Subquery for Max Count

<details>
<summary>Explanation</summary>

```sql
SELECT c.name
FROM Candidate c
WHERE c.id = (
    SELECT candidateId
    FROM Vote
    GROUP BY candidateId
    ORDER BY COUNT(*) DESC
    LIMIT 1
);
```

The subquery finds the candidateId with the most votes. The outer query retrieves the name. This separates the aggregation from the lookup, which can be clearer when the logic is complex.

</details>

### Approach 3: Window Function with RANK

<details>
<summary>Explanation</summary>

```sql
SELECT name
FROM (
    SELECT c.name,
           RANK() OVER (ORDER BY COUNT(*) DESC) AS rnk
    FROM Vote v
    JOIN Candidate c ON v.candidateId = c.id
    GROUP BY c.id, c.name
) ranked
WHERE rnk = 1;
```

RANK handles ties: if two candidates tie for first, both are returned. This is the correct approach when ties must be preserved rather than arbitrarily broken by LIMIT 1.

</details>

## Edge Cases

| Scenario | Expected | Why |
|---|---|---|
| Clear winner | That candidate | Highest COUNT |
| Tie for first | LIMIT 1 returns one (non-deterministic) | Use RANK to return all tied winners |
| Single vote | That candidate wins | Only one group |
| All votes for one candidate | That candidate | COUNT is total votes |
| Vote for non-existent candidate | Ignored | INNER JOIN drops unmatched rows |

## Interview Tips

> "I'll join Vote to Candidate to get names, GROUP BY candidate to count votes, then ORDER BY count descending with LIMIT 1 to get the winner. If ties matter, I'd use RANK() OVER (ORDER BY COUNT(*) DESC) instead of LIMIT 1."

**What the interviewer evaluates:** This is straightforward. The interview value is in handling ties: "what if two candidates tie?" Mentioning RANK for tie handling shows depth. The interviewer may also ask about the INNER JOIN behavior: votes for non-existent candidates are silently dropped. Noting this shows attention to data quality.

## At Scale

GROUP BY candidateId is cheap because the number of candidates is small (typically dozens to thousands). The join is also small if the Candidate table fits in memory. The ORDER BY + LIMIT 1 operates on the aggregated result (one row per candidate), which is trivially fast.

For very large vote tables (millions of votes), the bottleneck is scanning the Vote table. The GROUP BY uses hash aggregation with O(candidates) memory. In distributed engines, partial aggregation per node reduces shuffle to one row per candidate per node.

## DE Application

Finding the top entity by count is a universal analytics pattern:

- "Most popular product" (orders grouped by product)
- "Most active user" (events grouped by user)
- "Table with the most rows" (metadata aggregation)
- "Busiest API endpoint" (request logs grouped by endpoint)
- Combined with HAVING for threshold-based selection ("products with 100+ orders")

## Dialect Notes

Syntax is identical across all major engines. JOIN, GROUP BY, ORDER BY and LIMIT are part of the SQL standard. Note that SQL Server uses `TOP 1` instead of `LIMIT 1`, but the pattern is otherwise universal.

## Related Problems

- [182. Duplicate Emails](182_duplicate_emails.md) - GROUP BY + HAVING
- [570. Managers with 5 Reports](../../02_joins/problems/570_managers_with_5_reports.md) - JOIN + GROUP BY + HAVING
- [585. Investments in 2016](585_investments_in_2016.md) - Subquery with GROUP BY + HAVING
