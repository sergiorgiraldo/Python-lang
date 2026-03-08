# Rising Temperature (LeetCode #197)

🔗 [LeetCode 197: Rising Temperature](https://leetcode.com/problems/rising-temperature/)

> **Difficulty:** Easy | **Interview Frequency:** Very Common

## Problem Statement

Write a SQL query to find all dates where the temperature was higher than the previous day's temperature. Return the ids of those rows.

## Thought Process

1. **Compare to previous row:** LAG(temperature) gives the previous day's temperature. LAG(recordDate) gives the previous date.
2. **Date gap handling is critical:** We cannot just compare to the LAG value blindly. If dates are not consecutive (e.g., Jan 1 to Jan 3), comparing temperatures across a gap is invalid. We must verify that the previous date is exactly one day before.
3. **Self-join alternative:** Join the table to itself where dates differ by exactly 1 day. This naturally handles gaps because the join condition enforces date adjacency.

## Worked Example

The subtle detail is the date gap check. LAG gives the physically previous row in date order, but that row might be from a non-adjacent date. Comparing temperatures across a gap would be incorrect. We verify date adjacency with `recordDate = prev_date + INTERVAL '1 day'`.

```
Weather table:
  id | recordDate | temperature
  1  | 2015-01-01 | 10
  2  | 2015-01-02 | 25
  3  | 2015-01-03 | 20
  4  | 2015-01-04 | 30

After LAG:
  id=1: temp=10, prev_temp=NULL, prev_date=NULL        -> skip (no previous)
  id=2: temp=25, prev_temp=10, prev_date=2015-01-01    -> 25>10 and dates consecutive -> YES
  id=3: temp=20, prev_temp=25, prev_date=2015-01-02    -> 20<25 -> no
  id=4: temp=30, prev_temp=20, prev_date=2015-01-03    -> 30>20 and dates consecutive -> YES

Result: {2, 4}

Gap example:
  id=1: 2015-01-01, temp=10
  id=2: 2015-01-03, temp=25    <- gap: Jan 2 missing
  LAG gives prev_date=2015-01-01, but 2015-01-03 != 2015-01-01 + 1 day -> SKIP
```

## Approaches

### Approach 1: LAG with Date Validation

<details>
<summary>Explanation</summary>

Use LAG to get both the previous temperature and the previous date. Filter where the temperature increased AND the dates are exactly one day apart.

Both LAG values come from the same window (ORDER BY recordDate), so they are always consistent. The date check is the key addition over a naive LAG comparison.

**Dialect notes:**
- DuckDB/Postgres: `prev_date + INTERVAL '1 day'`
- MySQL: `DATE_ADD(prev_date, INTERVAL 1 DAY)`
- BigQuery: `DATE_ADD(prev_date, INTERVAL 1 DAY)`

</details>

### Approach 2: Self-Join

<details>
<summary>Explanation</summary>

Join Weather to itself where one row's date is exactly one day after the other's:

```sql
FROM Weather w1
JOIN Weather w2 ON w1.recordDate = w2.recordDate + INTERVAL '1 day'
WHERE w1.temperature > w2.temperature
```

The join condition inherently handles date gaps: if Jan 2 is missing, there is no matching row for Jan 3 to join with. Both approaches are correct and handle gaps properly.

</details>

## Edge Cases

| Scenario | Expected | Why |
|---|---|---|
| First day | Not included | No previous day to compare |
| Strictly decreasing | Empty result | No day is warmer than the previous |
| Gap in dates | Skip the gap | Dates not consecutive, no comparison |
| Same temperature | Not included | Not strictly higher |
| Single record | Empty result | Nothing to compare |

## Interview Tips

> "I'll use LAG to get the previous temperature and date. The key detail is checking that the dates are consecutive. Without the date gap check, the query would incorrectly compare across missing days."

**What the interviewer evaluates:** The date gap handling is the subtle detail that separates correct from incorrect solutions. Candidates who compare LAG values without checking date continuity produce wrong results. This tests thoroughness and attention to real-world data quality issues. Missing dates are common in production time series data.

## At Scale

LAG is a single sorted pass: O(n log n) for the sort, O(n) for the scan. The self-join needs an index on recordDate to be efficient (O(n) with index, O(n^2) without). For large time series tables (billions of rows), LAG is strictly faster because it avoids the join overhead. Partitioning the table by date range (monthly, yearly) limits the sort scope.

## DE Application

Change detection in time series is a core DE pattern: SLA monitoring (did latency increase from yesterday?), financial reporting (day-over-day revenue change) and operational alerts (did error rate spike compared to the previous hour?). The LAG + date validation pattern ensures correct comparisons even with missing data points, which is essential for production reliability.

## Related Problems

- [180. Consecutive Numbers](180_consecutive_numbers.md) - LAG for consecutive value detection
- [550. Game Play Analysis IV](550_game_play_analysis_iv.md) - Date arithmetic with first login
