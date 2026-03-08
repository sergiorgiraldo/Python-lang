# Game Play Analysis IV (LeetCode #550)

🔗 [LeetCode 550: Game Play Analysis IV](https://leetcode.com/problems/game-play-analysis-iv/)

> **Difficulty:** Medium | **Interview Frequency:** Common

## Problem Statement

Write a SQL query to find the fraction of players who logged in on the day after their first login date. Round to 2 decimal places. This is "day 1 retention."

## Thought Process

1. **Two-step decomposition:** First, find each player's first login date. Second, check if they have an activity record on the next day.
2. **Anchor date pattern:** The first login is the "anchor." We compare subsequent activity relative to this anchor. This is the same pattern used in retention analysis, cohort analysis and funnel analysis.
3. **Fraction calculation:** Count retained players divided by total players. Cast to DECIMAL to avoid integer division.

## Worked Example

The approach breaks into two logical steps. First identify the anchor event (first login) for each player. Then check if the retention event (login on day after first login) exists. The fraction is retained / total.

```
Activity table:
  player_id | event_date
  1         | 2016-03-01
  1         | 2016-03-02    <- day after first login (retained)
  2         | 2017-06-25    <- only login (not retained)
  3         | 2016-03-02
  3         | 2018-07-03    <- not the day after first login

Step 1 - First login per player:
  player 1: 2016-03-01
  player 2: 2017-06-25
  player 3: 2016-03-02

Step 2 - Check for day-after login:
  player 1: has 2016-03-02 = 2016-03-01 + 1 day -> retained
  player 2: no 2017-06-26 record -> not retained
  player 3: no 2016-03-03 record -> not retained

Fraction: 1 retained / 3 total = 0.33
```

## Approaches

### Approach 1: GROUP BY + JOIN Back

<details>
<summary>Explanation</summary>

CTE computes MIN(event_date) per player. Join back to Activity where event_date = first_date + 1 day. Count distinct matching players divided by total distinct players.

```sql
WITH first_login AS (
    SELECT player_id, MIN(event_date) AS first_date
    FROM Activity GROUP BY player_id
)
SELECT ROUND(
    CAST(COUNT(DISTINCT a.player_id) AS DECIMAL) /
    (SELECT COUNT(DISTINCT player_id) FROM Activity), 2
) AS fraction
FROM first_login f
JOIN Activity a ON a.player_id = f.player_id
    AND a.event_date = f.first_date + INTERVAL '1 day';
```

</details>

### Approach 2: Window Function for First Login

<details>
<summary>Explanation</summary>

Use `MIN(event_date) OVER (PARTITION BY player_id)` to annotate each row with the player's first login. Then filter rows where event_date = first_date + 1 day.

```sql
WITH annotated AS (
    SELECT player_id, event_date,
           MIN(event_date) OVER (PARTITION BY player_id) AS first_date
    FROM Activity
)
SELECT ROUND(
    CAST(COUNT(DISTINCT player_id) AS DECIMAL) /
    (SELECT COUNT(DISTINCT player_id) FROM Activity), 2
) AS fraction
FROM annotated
WHERE event_date = first_date + INTERVAL '1 day';
```

This avoids the explicit GROUP BY and join. The window function computes the first date inline.

</details>

## Edge Cases

| Scenario | Expected | Why |
|---|---|---|
| All players retained | 1.0 | Everyone logged in the next day |
| No players retained | 0.0 | Nobody returned |
| Player logged in on day 3 not day 2 | Not counted | Must be exactly day after first login |
| Single player, single login | 0.0 | No second login at all |

## Interview Tips

> "This is a day 1 retention calculation. I'll find each player's first login, then check if they have an activity record exactly one day later. The fraction is retained players over total players, cast to decimal to avoid integer division."

**What the interviewer evaluates:** This tests real analytics SQL, not toy problems. The multi-step decomposition (find anchor date, check condition relative to it) is a pattern that appears in retention, cohort analysis and funnel analysis. Candidates who can articulate the two-step approach and handle the date arithmetic correctly demonstrate production analytics skill.

## At Scale

GROUP BY player_id for first login is a single pass with hash aggregation: O(n). The join back to Activity is efficient with an index on (player_id, event_date): O(n) total. For 1B activity records across 100M players, the hash aggregation and indexed join complete in minutes. The window function alternative scans once but annotates every row, which uses more memory for the window buffer.

## DE Application

Day 1 retention is a critical product metric. This exact query runs in every gaming, SaaS and mobile app analytics pipeline. Variants include day 7, day 30 and day 90 retention. Cohort analysis extends this to retention curves: "for players who first logged in during week W, what fraction returned each subsequent week?" The anchor date pattern is the foundation for all of these.

## Dialect Notes

Date arithmetic syntax varies across engines:

- **DuckDB / Postgres**: `event_date + INTERVAL '1 day'` or `event_date + 1`
- **BigQuery**: `DATE_ADD(event_date, INTERVAL 1 DAY)`
- **Snowflake**: `DATEADD('day', 1, event_date)`
- **Spark SQL**: `date_add(event_date, 1)`

The window function and GROUP BY patterns are identical across all engines.

## Related Problems

- [197. Rising Temperature](197_rising_temperature.md) - Date arithmetic with adjacent rows
- [184. Department Highest Salary](184_department_highest_salary.md) - PARTITION BY for grouping
