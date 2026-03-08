# Game Play Analysis I (LeetCode #511)

🔗 [LeetCode 511: Game Play Analysis I](https://leetcode.com/problems/game-play-analysis-i/)

> **Difficulty:** Easy | **Interview Frequency:** Occasional

## Problem Statement

Find the first login date for each player from the Activity table.

## Thought Process

1. **Group by player:** Each player has multiple activity rows. GROUP BY player_id collapses them.
2. **MIN for earliest date:** MIN(event_date) returns the earliest login per group.
3. **No filtering needed:** Every player has at least one row, so no HAVING clause is required.

## Worked Example

The query groups all activity rows by player and selects the minimum event_date from each group. MIN on a DATE column returns the earliest date. This is the simplest form of "find the first occurrence per entity."

```
Activity:
  player_id | event_date
  1         | 2016-03-01
  1         | 2016-05-02
  2         | 2017-06-25
  2         | 2017-06-23

GROUP BY player_id:
  player 1 -> dates: [2016-03-01, 2016-05-02] -> MIN = 2016-03-01
  player 2 -> dates: [2017-06-25, 2017-06-23] -> MIN = 2017-06-23

Result:
  player_id | first_login
  1         | 2016-03-01
  2         | 2017-06-23
```

## Approaches

### Approach 1: GROUP BY + MIN

<details>
<summary>Explanation</summary>

```sql
SELECT player_id,
       MIN(event_date) AS first_login
FROM Activity
GROUP BY player_id;
```

The most direct approach. GROUP BY collapses rows per player, MIN picks the earliest date. One pass through the data, one output row per player.

</details>

### Approach 2: Window Function

<details>
<summary>Explanation</summary>

```sql
SELECT DISTINCT player_id,
       FIRST_VALUE(event_date) OVER (
           PARTITION BY player_id ORDER BY event_date
       ) AS first_login
FROM Activity;
```

FIRST_VALUE with ORDER BY event_date returns the earliest date per player. DISTINCT removes duplicate rows. This approach is overkill for this problem but becomes useful when you need additional columns from the first-login row (like device_id or games_played) without a separate join.

</details>

## Edge Cases

| Scenario | Expected | Why |
|---|---|---|
| Player with single login | That date returned | MIN of one value is itself |
| Multiple players with same first date | Each appears with that date | GROUP BY is per player |
| Rows inserted in non-chronological order | Correct MIN regardless | MIN is order-independent |
| Same player logs in twice on same date | That date returned | MIN of identical values is the value |

## Interview Tips

> "I'll GROUP BY player_id and take MIN(event_date) to find each player's first login. GROUP BY collapses rows per player and MIN picks the earliest date. If I also needed columns from the first-login row, I'd use a window function or a correlated subquery instead."

**What the interviewer evaluates:** This is a warm-up problem. The teaching value is the GROUP BY vs window function distinction. GROUP BY collapses rows (one row per group). Window functions preserve all rows. When you only need one value per group, GROUP BY is simpler and more readable. The interviewer may follow up with "now also return the device they used on their first login," which requires either a window function approach or a self-join back to the original table.

## At Scale

GROUP BY player_id with MIN is a streaming aggregation: each row updates a running minimum for its player. Time is O(n), memory is O(distinct players). For a game with 100M players and 10B activity rows, the hash table of player_id to min_date is roughly 1.5GB (player_id integer + date per entry).

In distributed engines, this is a single-stage aggregation. Each node computes local MIN values, then a final aggregation merges them. MIN is associative and commutative, so partial aggregation is trivially parallelizable.

## DE Application

Finding anchor events per entity is a foundational pattern in data engineering:

- "First purchase date per customer" (customer lifetime value calculation)
- "First error per pipeline run" (root cause analysis in orchestration)
- "Earliest record per primary key" (incremental processing watermarks)
- "First appearance per dimension key" (SCD Type 2 effective dates)
- "Oldest unprocessed event per partition" (consumer lag monitoring)

## Dialect Notes

Syntax is identical across all major engines. GROUP BY and MIN are part of the SQL standard with no dialect variation.

## Related Problems

- [182. Duplicate Emails](182_duplicate_emails.md) - GROUP BY + HAVING
- [574. Winning Candidate](574_winning_candidate.md) - GROUP BY + ORDER BY + LIMIT
- [615. Average Salary](615_average_salary.md) - Multi-level aggregation
