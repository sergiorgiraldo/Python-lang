# Investments in 2016 (LeetCode #585)

🔗 [LeetCode 585: Investments in 2016](https://leetcode.com/problems/investments-in-2016/)

> **Difficulty:** Medium | **Interview Frequency:** Occasional

## Problem Statement

Find the total tiv_2016 (rounded to 2 decimal places) for policyholders who meet both conditions:
1. Their tiv_2015 value is the same as at least one other policyholder's tiv_2015
2. Their location (lat, lon) is unique among all policyholders

## Thought Process

1. **Two independent filters:** The problem defines two set membership conditions. Each can be expressed as a GROUP BY + HAVING subquery.
2. **Shared tiv_2015:** GROUP BY tiv_2015, HAVING COUNT(*) > 1 gives the set of shared values. Filter with IN.
3. **Unique location:** GROUP BY lat, lon, HAVING COUNT(*) = 1 gives unique locations. Filter with IN.
4. **Combine with AND:** Both conditions must hold. SUM the qualifying tiv_2016 values.

## Worked Example

The two conditions are independent filters that each use GROUP BY + HAVING to define a set. The main query checks membership in both sets using IN clauses combined with AND. The SUM aggregates only the rows that pass both filters.

```
Insurance:
  pid | tiv_2015 | tiv_2016 | lat | lon
  1   | 10       | 5        | 10  | 10
  2   | 20       | 20       | 20  | 20
  3   | 10       | 30       | 20  | 20
  4   | 10       | 40       | 40  | 40

Shared tiv_2015 (COUNT > 1): {10}  (appears 3 times)
Unique locations (COUNT = 1): {(10,10), (40,40)}  ((20,20) appears twice)

Filter:
  pid 1: tiv_2015=10 IN {10} AND (10,10) IN unique -> YES -> tiv_2016=5
  pid 2: tiv_2015=20 NOT IN {10}                   -> NO
  pid 3: tiv_2015=10 IN {10} AND (20,20) NOT IN unique -> NO
  pid 4: tiv_2015=10 IN {10} AND (40,40) IN unique -> YES -> tiv_2016=40

SUM = 5 + 40 = 45.00
```

## Approaches

### Approach 1: Subquery with GROUP BY + HAVING

<details>
<summary>Explanation</summary>

```sql
SELECT ROUND(SUM(tiv_2016), 2) AS tiv_2016
FROM Insurance
WHERE tiv_2015 IN (
    SELECT tiv_2015
    FROM Insurance
    GROUP BY tiv_2015
    HAVING COUNT(*) > 1
)
AND (lat, lon) IN (
    SELECT lat, lon
    FROM Insurance
    GROUP BY lat, lon
    HAVING COUNT(*) = 1
);
```

Each subquery defines a set using GROUP BY + HAVING. The main query filters for rows in both sets. This is readable and clearly separates the two conditions.

**Dialect notes:** Tuple IN `(lat, lon) IN (...)` works in DuckDB, Postgres and MySQL. In BigQuery, use `STRUCT(lat, lon) IN (...)`. In Snowflake, use two separate conditions or a CTE with a join.

</details>

### Approach 2: Window Functions

<details>
<summary>Explanation</summary>

```sql
SELECT ROUND(SUM(tiv_2016), 2) AS tiv_2016
FROM (
    SELECT tiv_2016,
           COUNT(*) OVER (PARTITION BY tiv_2015) AS tiv_cnt,
           COUNT(*) OVER (PARTITION BY lat, lon) AS loc_cnt
    FROM Insurance
) t
WHERE tiv_cnt > 1 AND loc_cnt = 1;
```

Two window functions compute both counts in a single pass. The outer query filters on the computed counts. This avoids subqueries and makes a single scan of the table.

**Trade-off:** The window function approach is more efficient (single pass) but less immediately readable than the subquery approach. For this problem, the subquery version is clearer about intent.

</details>

## Edge Cases

| Scenario | Expected | Why |
|---|---|---|
| No one meets both criteria | NULL | SUM of empty set is NULL in SQL |
| All share tiv_2015 and all unique locations | Sum of all tiv_2016 | Every row qualifies |
| Single policyholder | NULL | tiv_2015 not shared (COUNT = 1, needs > 1) |
| Two at same location with same tiv_2015 | Neither qualifies for location | Both have loc COUNT = 2 |

## Interview Tips

> "I see two independent conditions. I'll use GROUP BY + HAVING subqueries to define each set, then filter the main table with IN for both conditions. For the location uniqueness, I'll use a tuple IN with (lat, lon). Finally, SUM and ROUND the qualifying tiv_2016 values."

**What the interviewer evaluates:** This is a medium-hard problem. The two independent conditions must both be correct. Getting the HAVING direction right (> 1 for shared, = 1 for unique) is the key detail. The window function alternative shows versatility. Mentioning query plan differences (single pass vs multiple passes) demonstrates optimization awareness. The tuple IN syntax is a dialect-awareness signal.

## At Scale

**Subquery approach:** Three passes over the table (two subqueries + outer query). Each subquery does a GROUP BY (hash aggregation). The outer query probes both result sets for each row. Total work is O(3n) with O(distinct_tiv + distinct_locations) memory.

**Window function approach:** Single pass with two hash-based window aggregations. Total work is O(n) with the same memory footprint. For large tables, the single-pass approach is likely faster due to reduced I/O.

For 10M insurance records, the subquery approach scans the table three times (30M row reads), while the window approach scans once (10M row reads). On columnar storage, the difference is less pronounced since only the needed columns are read.

## DE Application

Filtering entities based on multiple aggregate conditions is common in production:

- "Find customers whose 2023 spend matches at least one other customer but whose location is unique" (fraud detection)
- "Find tables where column cardinality matches expectations but row count is anomalous" (data quality)
- "Find events with shared session properties but unique device fingerprints" (bot detection)

The pattern of defining sets with GROUP BY + HAVING and then filtering with IN is the SQL equivalent of set intersection and difference operations.

## Related Problems

- [182. Duplicate Emails](182_duplicate_emails.md) - GROUP BY + HAVING for duplicates
- [574. Winning Candidate](574_winning_candidate.md) - GROUP BY + aggregate + ORDER BY
- [615. Average Salary](615_average_salary.md) - Multi-level aggregation
