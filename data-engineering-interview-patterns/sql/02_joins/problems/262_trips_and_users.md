# Trips and Users (LeetCode #262)

🔗 [LeetCode 262: Trips and Users](https://leetcode.com/problems/trips-and-users/)

> **Difficulty:** Hard | **Interview Frequency:** Common

## Problem Statement

Calculate the cancellation rate for each day between '2013-10-01' and '2013-10-03'. Only consider trips where both the client and the driver are not banned. Cancellation rate = number of cancelled trips / total trips, rounded to 2 decimal places.

## Thought Process

1. **Filter banned users:** Both the client and the driver must be unbanned. This requires joining Trips to Users twice: once for the client, once for the driver.
2. **Conditional aggregation:** Count cancelled trips using CASE WHEN inside SUM. Divide by COUNT(*) for the rate.
3. **Date filtering:** WHERE request_at BETWEEN filters the date range.
4. **Rounding:** ROUND(..., 2) formats the output.

## Worked Example

The query combines three concepts: double join for filtering, conditional aggregation for the ratio and date-range filtering. Breaking it into steps makes the logic clear. First, join to eliminate banned users. Then, group by day and compute the cancellation ratio within each group.

```
Users table:
  users_id | banned | role
  1        | No     | client
  2        | Yes    | client
  3        | No     | client
  10       | No     | driver
  11       | No     | driver

Trips table:
  id | client_id | driver_id | status              | request_at
  1  | 1         | 10        | completed           | 2013-10-01
  2  | 2         | 11        | cancelled_by_driver | 2013-10-01
  3  | 3         | 10        | completed           | 2013-10-01
  4  | 3         | 11        | cancelled_by_client | 2013-10-01

Step 1 - Join to filter banned users:
  Trip 2: client_id=2 is banned -> excluded by JOIN to Users (client side)
  Trips 1, 3, 4 remain

Step 2 - Group by day (2013-10-01):
  3 trips total, 1 cancelled (trip 4)
  Rate = 1/3 = 0.33

Result:
  Day        | Cancellation Rate
  2013-10-01 | 0.33
```

## Approaches

### Approach 1: Double JOIN + CASE Aggregation

<details>
<summary>Explanation</summary>

Join Trips to Users twice (once for client, once for driver) with the banned='No' filter. Use CASE WHEN inside SUM to count cancellations.

```sql
SELECT t.request_at AS "Day",
       ROUND(
           SUM(CASE WHEN t.status LIKE 'cancelled%' THEN 1.0 ELSE 0.0 END) /
           COUNT(*),
           2
       ) AS "Cancellation Rate"
FROM Trips t
JOIN Users c ON t.client_id = c.users_id AND c.banned = 'No'
JOIN Users d ON t.driver_id = d.users_id AND d.banned = 'No'
WHERE t.request_at BETWEEN '2013-10-01' AND '2013-10-03'
GROUP BY t.request_at
ORDER BY t.request_at;
```

The LIKE 'cancelled%' pattern matches both 'cancelled_by_client' and 'cancelled_by_driver'. Using 1.0 (not 1) ensures decimal division.

**Dialect notes:** ROUND(x, 2) works identically across DuckDB, Postgres, BigQuery and Snowflake. MySQL uses the same syntax. Spark uses ROUND or BROUND.

</details>

## Edge Cases

| Scenario | Expected | Why |
|---|---|---|
| Day with no cancellations | Rate = 0.00 | SUM of zeros / COUNT |
| Day with all cancellations | Rate = 1.00 | All CASE matches |
| Banned client | Trip excluded | INNER JOIN filters it |
| Banned driver | Trip excluded | Second INNER JOIN filters it |
| Day outside range | Not in result | WHERE BETWEEN filters it |

## Interview Tips

> "I'll join Trips to Users twice since both the client and driver must be unbanned. For the cancellation rate, I'll use CASE WHEN inside SUM to count only cancelled trips, then divide by COUNT(*). The LIKE 'cancelled%' pattern handles both cancellation types."

**What the interviewer evaluates:** This is a hard LeetCode SQL problem that combines multiple concepts. The double join tests whether you can use the same table in two roles within one query. The conditional aggregation tests CASE WHEN inside aggregate functions. Breaking the problem into steps during the interview (first identify what needs filtering, then what needs aggregating) demonstrates systematic thinking rather than trying to write the full query at once.

## At Scale

JOIN + GROUP BY is the standard pattern for aggregated metrics with dimension filters. Performance considerations:
- **Indexing request_at** enables partition pruning for the date filter
- **The double join** to Users is cheap if Users is small (broadcast join)
- **Conditional aggregation** is a single-pass operation over the grouped data

For a ride-sharing platform with billions of trips, this query would run against a partitioned fact table (Trips partitioned by request_at). The date filter prunes to the relevant partitions. The Users table is small (dimension table) and gets broadcast to every node.

Pre-aggregating daily cancellation rates into a summary table avoids recomputing over raw trips for dashboard queries.

## DE Application

Computing rates and ratios from fact tables with dimension filters is one of the most common analytics patterns:
- "Failure rate per day excluding test accounts" (same structure as this problem)
- "Conversion rate by channel excluding bot traffic"
- "Error rate per service excluding maintenance windows"

The double-join-to-dimension pattern appears whenever a fact table references the same dimension in multiple roles (client and driver here, sender and receiver in messaging, source and target in network flows).

## Related Problems

- [181. Employees Earning More](181_employees_earning_more.md) - Self-join concept
- [570. Managers with 5 Reports](570_managers_with_5_reports.md) - JOIN + GROUP BY + HAVING
