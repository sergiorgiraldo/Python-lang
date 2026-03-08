# Friend Requests II - Who Has the Most Friends (LeetCode #602)

🔗 [LeetCode 602: Friend Requests II - Who Has the Most Friends](https://leetcode.com/problems/friend-requests-ii-who-has-the-most-friends/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

## Problem Statement

Each row in RequestAccepted represents a mutual friendship. Find the person with the most friends and their friend count.

## Thought Process

1. **Bidirectional relationships:** Each row (requester_id, accepter_id) represents a friendship from both sides. Person A requesting and Person B accepting means both gain a friend.
2. **Normalize with UNION ALL:** Create two rows per friendship: one for the requester, one for the accepter. This lets us count friends per person with a simple GROUP BY.
3. **UNION ALL not UNION:** UNION deduplicates, which would incorrectly remove a person's friend count if they appear as both requester and accepter of different friendships with the same count.
4. **Top 1:** ORDER BY count DESC LIMIT 1.

## Worked Example

The key insight is that friendships are bidirectional but stored as a single directed edge. To count friends per person, we need to "unfold" each edge into two rows: one crediting the requester and one crediting the accepter. UNION ALL stacks these without deduplication.

```
RequestAccepted table:
  requester_id | accepter_id
  1            | 2
  1            | 3
  2            | 3
  3            | 4

UNION ALL (normalize both sides):
  id: 1 (requester of friendship with 2)
  id: 2 (accepter of friendship with 1)
  id: 1 (requester of friendship with 3)
  id: 3 (accepter of friendship with 1)
  id: 2 (requester of friendship with 3)
  id: 3 (accepter of friendship with 2)
  id: 3 (requester of friendship with 4)
  id: 4 (accepter of friendship with 3)

GROUP BY id, COUNT(*):
  1 -> 2 friends (2, 3)
  2 -> 2 friends (1, 3)
  3 -> 3 friends (1, 2, 4)
  4 -> 1 friend (3)

ORDER BY num DESC LIMIT 1:
  Person 3 with 3 friends
```

## Approaches

### Approach 1: UNION ALL + GROUP BY

<details>
<summary>Explanation</summary>

```sql
WITH all_friends AS (
    SELECT requester_id AS id FROM RequestAccepted
    UNION ALL
    SELECT accepter_id AS id FROM RequestAccepted
)
SELECT id, COUNT(*) AS num
FROM all_friends
GROUP BY id
ORDER BY num DESC
LIMIT 1;
```

UNION ALL creates two rows per friendship. GROUP BY id with COUNT(*) gives friend count per person. LIMIT 1 returns the top result.

**Why UNION ALL, not UNION:** UNION deduplicates. If person 1 appears as requester in one row and accepter in another, UNION would collapse them into one row before counting, losing a friend count. UNION ALL preserves every occurrence.

</details>

## Edge Cases

| Scenario | Expected | Why |
|---|---|---|
| Tie for most friends | LIMIT 1 returns one (either valid) | Problem spec says "the person" |
| Person on both sides | Both sides counted | UNION ALL includes both |
| Single friendship | Both have 1 friend | Each person appears once in UNION ALL |
| Large fan-out | Correct count | Every edge contributes exactly 2 rows |

## Interview Tips

> "Friendships are bidirectional but stored as directed edges. I'll normalize with UNION ALL to create two rows per friendship, one per participant. Then GROUP BY id and COUNT gives friend counts. UNION ALL is important here, not UNION, because UNION would deduplicate and lose counts."

**What the interviewer evaluates:** Recognizing that friendships are bidirectional and need normalization tests data modeling understanding. The UNION ALL vs UNION distinction for this purpose tests whether you understand when deduplication is harmful. This pattern generalizes to any graph metric computation from an edge list.

## At Scale

UNION ALL doubles the data. For n friendships, the normalized table has 2n rows. GROUP BY on the combined set is O(2n) time and O(k) memory where k is the number of distinct persons.

For social graphs with billions of friendships:
- **Pre-aggregated friend counts** maintained incrementally avoid full recomputation. Each new friendship increments two counters.
- **Graph databases** (Neo4j, Neptune) store adjacency lists natively, making degree computation O(1) per node.
- **Approximate counts** using HyperLogLog provide cardinality estimates without exact counting for dashboards.

In a warehouse context, materializing friend counts as a summary table and updating incrementally on new friendships is the standard pattern.

## DE Application

Graph metrics from edge lists follow this same normalize-then-aggregate pattern:
- "Most connected node in a dependency graph" (package dependencies, table lineage)
- "Average degree of a social network" (UNION ALL + GROUP BY + AVG)
- "Find nodes with degree > threshold" (high-connection anomaly detection)
- "Bidirectional event flows" (sender/receiver in messaging, source/target in API calls)

The UNION ALL normalization step is the foundation for any analysis that treats directed edges as undirected relationships.

## Dialect Notes

Syntax is identical across all major engines. UNION ALL, GROUP BY, ORDER BY and LIMIT are part of the SQL standard. Note that SQL Server uses `TOP 1` instead of `LIMIT 1`, but the pattern is otherwise universal.

## Related Problems

- [181. Employees Earning More](181_employees_earning_more.md) - Self-referencing relationships
- [570. Managers with 5 Reports](570_managers_with_5_reports.md) - Aggregation with threshold
