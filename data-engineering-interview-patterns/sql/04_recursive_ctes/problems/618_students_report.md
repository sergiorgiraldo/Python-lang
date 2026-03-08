# Students Report By Geography (LeetCode #618)

🔗 [LeetCode 618: Students Report By Geography](https://leetcode.com/problems/students-report-by-geography/)

> **Difficulty:** Hard | **Interview Frequency:** Occasional

## Problem Statement

Given a Student table with `name` and `continent` columns, pivot the data so each continent becomes a column. Students within each continent are sorted alphabetically. Rows should align by position: the first alphabetical student from each continent shares row 1, the second shares row 2, etc. Columns with fewer students than the longest list should show NULL.

## Thought Process

1. **This is a pivot problem.** Convert rows into columns based on a categorical value (continent).
2. **Positional alignment is required.** We cannot just group by continent because students from different continents must align by their alphabetical rank within their continent.
3. **ROW_NUMBER creates the alignment key.** Assign each student a row number within their continent (ordered by name). Then GROUP BY this row number to align entries across continents.
4. **MAX(CASE WHEN ...) is the manual pivot.** For each row number, pull the name from each continent using conditional aggregation.

## Worked Example

The trick is that pivoting requires a shared key to align rows across columns. Without ROW_NUMBER, there is no natural key to join America's students with Asia's students. ROW_NUMBER creates that key: "first alphabetically" from each continent shares rn=1, "second alphabetically" shares rn=2, etc.

```
Input:
  name    | continent
  Jane    | America
  Pascal  | Europe
  Xi      | Asia
  Jack    | America

After ROW_NUMBER (PARTITION BY continent ORDER BY name):
  name    | continent | rn
  Jack    | America   |  1
  Jane    | America   |  2
  Xi      | Asia      |  1
  Pascal  | Europe    |  1

GROUP BY rn, then MAX(CASE WHEN continent='X' THEN name END):
  rn | America | Asia   | Europe
   1 | Jack    | Xi     | Pascal
   2 | Jane    | NULL   | NULL
```

NULL appears where a continent has fewer students than the longest list.

## Approaches

### Approach 1: ROW_NUMBER + Conditional Aggregation (Manual Pivot)

<details>
<summary>Explanation</summary>

1. Assign ROW_NUMBER within each continent, ordered by name.
2. GROUP BY the row number to create one output row per position.
3. Use MAX(CASE WHEN continent = 'X' THEN name END) to extract each continent's student at that position.

MAX works here because there is at most one name per (continent, rn) combination. MIN would work equally well. The aggregation is needed to collapse the GROUP BY.

Continent names are hardcoded in the CASE expressions. This works for a known, fixed set of continents but does not generalize to dynamic column sets.

</details>

### Approach 2: DuckDB PIVOT Syntax

<details>
<summary>Explanation</summary>

DuckDB supports native PIVOT syntax that simplifies this pattern:

```sql
WITH numbered AS (
    SELECT name, continent,
           ROW_NUMBER() OVER (PARTITION BY continent ORDER BY name) AS rn
    FROM Student_Geo
)
PIVOT numbered
ON continent
USING FIRST(name)
GROUP BY rn
ORDER BY rn;
```

The ROW_NUMBER step is still needed for positional alignment. PIVOT handles the column generation automatically. BigQuery and Snowflake have similar PIVOT syntax. Postgres and MySQL require the manual approach.

</details>

## Edge Cases

| Scenario | Expected | Why |
|---|---|---|
| Uneven continent sizes | NULL fills shorter columns | GROUP BY rn creates rows up to max count |
| Single continent populated | Other columns all NULL | CASE WHEN never matches for empty continents |
| Empty continent | Column exists but all NULL | Column is defined in SELECT, just never matched |
| One student per continent | Single row, all filled | All continents have rn=1 |

## Interview Tips

> "This is a pivot problem that requires positional alignment. I will use ROW_NUMBER within each continent to create an alignment key, then GROUP BY that key and use MAX(CASE WHEN) to pivot continent names into columns."

**What the interviewer evaluates:** This tests both window functions and pivoting. The ROW_NUMBER alignment trick is the key insight. Candidates who try to pivot without positional alignment get misaligned or duplicated output. Mentioning DuckDB/BigQuery/Snowflake PIVOT syntax as the production alternative shows pragmatism.

**Follow-up: dynamic pivoting.** If the number of continents is unknown, the column list cannot be hardcoded. In production, this requires dynamic SQL (building the query string programmatically) or a BI tool that handles pivoting in the presentation layer. This is a good discussion point to show awareness of SQL's limitations.

## At Scale

ROW_NUMBER + GROUP BY is O(n log n) for the window sort. The pivot itself produces one row per max group size, which is small. For 1B students across 7 continents, the window sort is the bottleneck. The conditional aggregation step is O(n) with constant-factor work per row (one CASE check per continent).

In practice, pivot operations in data warehouses are done on aggregated data (pivot revenue by region, pivot counts by category), not on individual names. The row counts are small after aggregation, making the pivot cheap.

For wide pivots (hundreds of columns), the query becomes unwieldy with manual CASE expressions. PIVOT syntax or dynamic SQL is essential.

## DE Application

Pivoting is one of the most common data transformation patterns:
- Converting row-per-metric to column-per-metric for dashboards
- Feature engineering for ML: one-hot encoding categorical variables in SQL
- Report generation: months as columns, products as rows
- ETL transformations: normalizing source data into wide-format tables

The ROW_NUMBER alignment pattern specifically applies when pivoting individual values (not aggregates). For aggregate pivots (SUM of revenue by month), the GROUP BY key is natural (month) and ROW_NUMBER is not needed.

## Related Problems

- [569. Median Employee Salary](569_median_employee_salary.md) - ROW_NUMBER for positional logic
